"""scitex — thin core (PROTOTYPE, not released).

``import scitex as stx`` and then ``stx.<name>`` resolves lazily (PEP 562) to
whatever installed distribution registered ``<name>`` in the ``scitex.modules``
entry-point group. Installing any single leaf (``pip install scitex-io``) is
therefore enough for both ``import scitex_io`` and ``stx.io`` to work.

The core is stdlib-only and imports nothing from any leaf at ``import scitex``
time. The entry-point table is scanned once, on the first ``stx.<name>`` miss.

Contract (see docs/proposals/THIN_CORE_ENTRY_POINTS.md):

    [project.entry-points."scitex.modules"]
    io = "scitex_io"                    # module form -> stx.io, import scitex.io
    session = "scitex_session:session"  # object form -> stx.session only
"""

from __future__ import annotations

import importlib
import sys
import warnings
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from typing import Dict, NamedTuple, Optional

# NOTE: importlib.metadata is imported lazily (first stx.<name> miss or
# __version__ read): it costs ~35 ms cold, more than the rest of the core.

ENTRY_POINT_GROUP = "scitex.modules"


def _dist_version() -> str:
    import importlib.metadata as md

    try:
        return md.version("scitex")
    except md.PackageNotFoundError:  # running from a source tree
        return "0.0.0"


# Names the core owns; a leaf registering one of these is ignored with a warning.
_RESERVED = frozenset(
    {"ENTRY_POINT_GROUP", "ScitexModuleNotInstalled", "list_modules", "__version__"}
)

# Old spellings kept working with a DeprecationWarning (alias -> canonical name).
_DEPRECATED_ALIASES: Dict[str, str] = {
    "ai": "ml",
    "reproduce": "repro",
    "rng": "repro",
    "verify": "clew",
    "notify": "notification",
}

# Only used to word the "not installed" error. Convention: stx.<name> is
# provided by the distribution ``scitex-<name>``; these are the exceptions.
_PROVIDER_OVERRIDES: Dict[str, str] = {
    "plt": "figrecipe",
    "diagram": "figrecipe",
    "social": "socialia",
    "cloud": "scitex-hub",
    "module": "scitex-hub",
    "project": "scitex-hub",
    "tunnel": "scitex-ssh",
    "errors": "scitex-logging",
    "torch": "scitex-linalg",
    "media": "scitex-etc",
    "dt": "scitex-datetime",
    "PATHS": "scitex-config",
}


class ScitexModuleNotInstalled(AttributeError):
    """``stx.<name>`` was requested but no installed distribution provides it.

    Subclasses AttributeError so ``hasattr(stx, name)`` stays False and PEP 562
    semantics hold; the message names the distribution to install.
    """


class _Provider(NamedTuple):
    name: str
    value: str  # "pkg.mod" or "pkg.mod:attr"
    dist: str
    dist_version: str

    @property
    def is_module(self) -> bool:
        return ":" not in self.value


_registry_cache: Optional[Dict[str, _Provider]] = None
_conflicts: Dict[str, list] = {}


def _registry() -> Dict[str, _Provider]:
    """Scan the entry-point group once; remember conflicts instead of guessing."""
    global _registry_cache
    if _registry_cache is not None:
        return _registry_cache
    import importlib.metadata as md

    found: Dict[str, _Provider] = {}
    for ep in md.entry_points(group=ENTRY_POINT_GROUP):
        dist = getattr(ep, "dist", None)
        prov = _Provider(
            ep.name,
            ep.value,
            dist.metadata["Name"] if dist is not None else "<unknown>",
            dist.version if dist is not None else "<unknown>",
        )
        if ep.name in _RESERVED or ep.name.startswith("_"):
            warnings.warn(
                f"{prov.dist} registers reserved name {ep.name!r} in "
                f"{ENTRY_POINT_GROUP!r}; ignored.",
                RuntimeWarning,
                stacklevel=2,
            )
            continue
        prev = found.get(ep.name)
        if prev is not None and prev.value != prov.value:
            _conflicts.setdefault(ep.name, [prev]).append(prov)
            continue
        found[ep.name] = prov
    _registry_cache = found
    return found


def _provider_hint(name: str) -> str:
    return _PROVIDER_OVERRIDES.get(name, f"scitex-{name.replace('_', '-')}")


def _check_conflict(name: str) -> None:
    if name in _conflicts:
        who = ", ".join(
            f"{p.dist}=={p.dist_version} ({p.value})" for p in _conflicts[name]
        )
        raise ImportError(
            f"scitex.{name} is registered by more than one installed "
            f"distribution: {who}. Uninstall all but one."
        )


def _resolve(name: str):
    prov = _registry().get(name)  # scans once; fills _conflicts
    _check_conflict(name)
    if prov is None:
        dist = _provider_hint(name)
        raise ScitexModuleNotInstalled(
            f"scitex.{name} is not available: no installed package registers "
            f"it. Install it with:  pip install {dist}   "
            f"(or everything: pip install 'scitex[all]')"
        )
    if prov.is_module:
        return importlib.import_module(prov.value)
    mod_name, _, attr = prov.value.partition(":")
    obj = importlib.import_module(mod_name)
    for part in attr.split("."):
        obj = getattr(obj, part)
    return obj


def __getattr__(name: str):
    # PEP 562: only called when normal module attribute lookup fails.
    if name == "__version__":
        globals()["__version__"] = v = _dist_version()
        return v
    if name.startswith("__"):
        raise AttributeError(f"module 'scitex' has no attribute {name!r}")
    if name in _DEPRECATED_ALIASES:
        canonical = _DEPRECATED_ALIASES[name]
        warnings.warn(
            f"scitex.{name} is deprecated, use scitex.{canonical} instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return __getattr__(canonical)
    value = _resolve(name)
    globals()[name] = value  # cache: later stx.<name> is a plain attribute hit
    return value


def __dir__():
    return sorted(set(globals()) | set(_registry()))


def list_modules() -> Dict[str, Dict[str, str]]:
    """Return ``{name: {"value", "dist", "version"}}`` for every registered name."""
    return {
        n: {"value": p.value, "dist": p.dist, "version": p.dist_version}
        for n, p in sorted(_registry().items())
    }


# --------------------------------------------------------------------------
# `import scitex.io` / `from scitex.io import load` / `import scitex.io.bundle`
# --------------------------------------------------------------------------
class _AliasLoader(Loader):
    def __init__(self, target: str):
        self._target = target
        self._saved_spec = None

    def create_module(self, spec):
        mod = importlib.import_module(self._target)
        # The import system overwrites __spec__ on the returned module after
        # create_module(); keep the real one and restore it in exec_module().
        self._saved_spec = getattr(mod, "__spec__", None)
        return mod

    def exec_module(self, module):
        if self._saved_spec is not None:
            module.__spec__ = self._saved_spec


class _AliasFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("scitex."):
            return None
        rest = fullname[len("scitex.") :]
        head, _, sub = rest.partition(".")
        if head.startswith("_"):  # scitex.__main__ etc. are not leaf names
            return None
        head = _DEPRECATED_ALIASES.get(head, head)
        prov = _registry().get(head)
        _check_conflict(head)
        if prov is None:
            # Fail loud with the install hint rather than a bare
            # "No module named 'scitex.io'". `name` is deliberately left unset:
            # with name=fullname, `from scitex import io` would swallow this
            # error and re-raise a hint-less "cannot import name 'io'".
            raise ModuleNotFoundError(
                f"No module named {fullname!r}: no installed package registers "
                f"scitex.{head}. Install it with:  pip install {_provider_hint(head)}"
            )
        if not prov.is_module:
            return None  # object-form entries (e.g. a decorator) are not importable
        target_name = prov.value + (f".{sub}" if sub else "")
        return ModuleSpec(fullname, _AliasLoader(target_name), is_package=True)


if not any(isinstance(f, _AliasFinder) for f in sys.meta_path):
    sys.meta_path.append(_AliasFinder())

__all__ = [
    "ENTRY_POINT_GROUP",
    "ScitexModuleNotInstalled",
    "list_modules",
    "__version__",
]
