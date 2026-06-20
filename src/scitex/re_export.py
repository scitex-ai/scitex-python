#!/usr/bin/env python3
"""scitex.re_export — the single home for the umbrella's re-export machinery.

The umbrella ships NO duplicate implementation: each `scitex.<short>` resolves
to its standalone peer (`scitex_<short>`, or a branded peer like `figrecipe`).
This module owns every mechanism that makes that work, so `__init__.py` only
*declares* the surface and consumes the engine here:

1. `_LazyModule` / `_CallableModuleWrapper` — lazy attribute proxies for
   `scitex.<short>` access (and `@scitex.session` decorator sugar).
2. `EXTERNAL_REEXPORTS` — the curated `{short: peer_import}` map for peers that
   have NO in-tree `scitex/<short>/` dir and re-export a top-level standalone.
3. `register_external_lazy_modules()` — pre-registers those peers in
   `sys.modules` via `importlib.util.LazyLoader` so `import scitex` stays
   sub-second while `from scitex.<short> import X` still resolves.
4. `install_alias_finder()` — a `MetaPathFinder` (registry-driven) that routes
   `import scitex.<short>[.…]` to the peer, deferring to a real on-disk
   `scitex/<short>/` dir when one exists (the migration escape hatch).

NOTE: `EXTERNAL_REEXPORTS` is curated rather than derived wholesale from the
ecosystem registry because the registry also lists peers that still have
in-tree dirs (`io`, `plt`, `stats`, `pd`, `writer`, …). Pre-registering those
as external would shadow their in-tree implementation. The alias finder guards
against that with an in-tree check; the eager pre-registration list cannot, so
it stays explicit.
"""

from __future__ import annotations

import importlib
import importlib.util as _importlib_util
import sys
import warnings
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Mapping, Optional

from ._canonical_redirects import (
    missing_extras_hint as _missing_extras_hint,
)
from ._canonical_redirects import (
    phantom_attr_hint as _phantom_attr_hint,
)
from ._canonical_redirects import (
    venv_pip_hint as _venv_pip_hint,
)


# =============================================================================
# Lazy attribute proxies
# =============================================================================
class _LazyModule:
    def __init__(self, name, external=None, fallback=None):
        self._name = name
        # If `external` is given, the lazy module proxies an external top-level
        # package (e.g. "scitex_io") instead of the in-tree submodule
        # `scitex.<name>`. This lets the umbrella drop pure re-export shim
        # directories — no source tree under `src/scitex/<name>/` is required.
        self._external = external
        # `fallback` is a secondary external tried when the primary `external`
        # is not importable. Used where two packages absorbed each other in
        # conflicting ADRs (e.g. scitex.security: ADR-0001 #139 routed it to
        # `scitex_audit.github`, while ADR-0002 #142 made `scitex_security`
        # the unified home and `scitex-audit` the deprecated shim). The
        # fallback keeps `scitex.security` reachable whichever package is
        # actually installed, instead of dying with a bare ModuleNotFoundError.
        self._fallback = fallback
        self._module = None

    def _load_module(self):
        if self._module is None:
            if self._external is not None:
                try:
                    self._module = importlib.import_module(self._external)
                except (ImportError, ModuleNotFoundError):
                    if self._fallback is None:
                        raise
                    self._module = importlib.import_module(self._fallback)
            else:
                self._module = importlib.import_module(
                    f".{self._name}", package="scitex"
                )
        return self._module

    def _warn_missing(self):
        warnings.warn(
            f"scitex.{self._name} requires additional dependencies. "
            f"Install with: {_venv_pip_hint(self._name)}",
            UserWarning,
            stacklevel=3,
        )

    def __getattr__(self, attr):
        # Return sensible defaults for dunder attrs without triggering import
        # (prevents Sphinx autodoc crashes when optional deps are missing)
        if attr == "__name__":
            return f"scitex.{self._name}"
        if attr == "__module__":
            return "scitex"
        if attr == "__qualname__":
            return self._name
        if attr == "__path__":
            return []
        if attr == "__file__":
            return None
        if attr == "__loader__":
            return None
        if attr == "__spec__":
            return None
        try:
            return getattr(self._load_module(), attr)
        except (ImportError, ModuleNotFoundError):
            # Either the external package itself is not importable (missing
            # extras), or a deeper transitive ImportError fired at module-
            # body exec. Route through the canonical-redirect hint so attrs
            # with a known core home don't demand a heavy extras install.
            self._module = None  # Reset so next attempt retries
            raise ImportError(_missing_extras_hint(self._name, attr)) from None
        except AttributeError:
            # The external package loaded fine but doesn't carry ``attr`` —
            # the "phantom" case (e.g. scitex.gen.load_configs where
            # load_configs actually lives in scitex_io, not scitex_gen).
            # If the redirect map names a canonical home, raise an
            # AttributeError naming it; otherwise let the original
            # AttributeError propagate untouched.
            hint = _phantom_attr_hint(self._name, attr)
            if hint is None:
                raise
            raise AttributeError(hint) from None

    def __dir__(self):
        """Return dir of the actual module for tab completion."""
        try:
            members = dir(self._load_module())
        except (ImportError, ModuleNotFoundError):
            self._module = None  # Reset so next attempt retries
            self._warn_missing()
            return []
        # Detect broken modules stuck in sys.modules (only have dunder attrs)
        public = [m for m in members if not m.startswith("_")]
        if not public:
            self._module = None
            self._warn_missing()
            return []
        return members

    def __repr__(self):
        if self._module is None:
            return f"<LazyModule(scitex.{self._name}) - not loaded>"
        return repr(self._module)


class _CallableModuleWrapper:
    """Callable module wrapper that acts as both a decorator and a module.

    This allows:
    - @scitex.session (new clean API)
    - @scitex.session.session (old API for backwards compatibility)
    - scitex.session.start() and other module functions

    Example:
        import scitex

        @scitex.session  # Clean! Calls __call__()
        def main(): pass

        @scitex.session.session  # Backwards compatible
        def main(): pass

        scitex.session.start(...)  # Access other functions
    """

    def __init__(self, module_name, main_decorator_name="session", external=None):
        self._module_name = module_name
        self._main_decorator_name = main_decorator_name
        # If `external` is given, the wrapper proxies an external package (e.g.
        # "scitex_hub.module") instead of the in-tree `scitex.<name>` submodule.
        # Used for optional peers (scitex-hub) so callability (`scitex.module(...)`)
        # is preserved while the in-tree dir is deleted. A missing peer raises a
        # friendly ImportError on first access/call rather than at `import scitex`.
        self._external = external
        self._module = None
        self._parent_name = None
        self._attr_name = None

    def _setup_persistence(self, parent_name, attr_name):
        """Set up persistence information to prevent replacement."""
        self._parent_name = parent_name
        self._attr_name = attr_name

    def _load_module(self):
        """Lazy load the actual module."""
        if self._module is None:
            # Import the module (external peer or in-tree submodule)
            if self._external is not None:
                try:
                    self._module = importlib.import_module(self._external)
                except ImportError as exc:
                    # Optional peer missing → friendly install hint, mirroring
                    # the `_make_missing_peer_stub` contract used elsewhere.
                    peer = self._external.split(".", 1)[0]
                    raise ImportError(
                        f"scitex.{self._module_name} requires `{peer}`. "
                        f"Install with: pip install 'scitex[{self._module_name}]' "
                        f"(or: pip install {peer.replace('_', '-')})"
                    ) from exc
            else:
                self._module = importlib.import_module(
                    f".{self._module_name}", package="scitex"
                )

            # Restore ourselves in the parent module's __dict__ to prevent replacement
            if self._parent_name and self._attr_name:
                parent_module = sys.modules.get(self._parent_name)
                if parent_module is not None:
                    setattr(parent_module, self._attr_name, self)

        return self._module

    def __call__(self, *args, **kwargs):
        """When used as @scitex.session"""
        module = self._load_module()
        main_decorator = getattr(module, self._main_decorator_name)
        return main_decorator(*args, **kwargs)

    def __getattr__(self, name):
        """When accessed as scitex.session.session or scitex.session.start"""
        if name == self._main_decorator_name:
            # Return self so @scitex.session.session works
            return self

        # Otherwise, delegate to the actual module
        module = self._load_module()
        return getattr(module, name)

    def __dir__(self):
        """Return dir of the actual module for tab completion."""
        module = self._load_module()
        return dir(module)

    def __repr__(self):
        """Show module representation."""
        if self._module is None:
            return f"<LazyModule(scitex.{self._module_name}) - not loaded>"
        return repr(self._module)


# =============================================================================
# External re-export map + eager lazy pre-registration
# =============================================================================
# `scitex.<short>` maps to top-level `scitex_<short>`. Registering eagerly in
# sys.modules so that internal `from scitex.<short> import X` (and submodule
# imports like `from scitex.<short>.<sub> import Y`) resolve to the external
# package without requiring a `src/scitex/<short>/` directory in this repo.
EXTERNAL_REEXPORTS = {
    "bridge": "scitex_bridge",
    "capture": "scitex_capture",
    "config": "scitex_config",
    "datetime": "scitex_datetime",
    "decorators": "scitex_decorators",
    "dsp": "scitex_dsp",
    "events": "scitex_events",
    # NOTE: `gen` is intentionally absent. `scitex.gen` is no longer a peer
    # re-export of the standalone `scitex_gen`; it is a FAIL-LOUD deprecation
    # shim shipped in-tree at `src/scitex/gen.py`. Leaving it out of this map
    # prevents `register_external_lazy_modules()` from pre-registering a lazy
    # `scitex_gen` proxy in `sys.modules["scitex.gen"]` (which would shadow the
    # on-disk shim). The shim names the focused package each old symbol moved
    # to and raises — no fallback to `scitex_gen`.
    "git": "scitex_git",
    "linalg": "scitex_linalg",
    "nn": "scitex_nn",
    "notification": "scitex_notification",
    "pd": "scitex_pd",
    "resource": "scitex_resource",
    "sh": "scitex_sh",
    "ui": "scitex_ui",
    "web": "scitex_web",
    "writer": "scitex_writer",
    "io": "scitex_io",  # in-tree dir removed (#289); pure re-export of scitex_io
    "clew": "scitex_clew",  # in-tree dir removed; session hooks moved into scitex_clew (>=0.2.14)
    "stats": "scitex_stats",  # in-tree dir removed; integration glue moved into scitex_stats (>=0.2.23)
    # `scitex.ai` was split into the `ml` + `genai` standalones; `ai` is now a
    # deprecated alias handled in __init__.__getattr__ (no `scitex_ai` package).
    "ml": "scitex_ml",
    "genai": "scitex_genai",
    "etc": "scitex_etc",
    "media": "scitex_etc.media",  # in-tree dir removed; shipped in scitex-etc (>=0.2.0)
    "gists": "scitex_gists",
    "audit": "scitex_audit",
    "compat": "scitex_compat",
    "repro": "scitex_repro",
    "app": "scitex_app",
    "scholar": "scitex_scholar",
    "dict": "scitex_dict",
    "notebook": "scitex_notebook",
    "str": "scitex_str",
    "logging": "scitex_logging",
    "browser": "scitex_browser",
    "parallel": "scitex_parallel",
    "path": "scitex_path",
    "db": "scitex_db",
    "audio": "scitex_audio",
    "types": "scitex_types",
    "template": "scitex_template",
    "benchmark": "scitex_benchmark",
    "context": "scitex_context",
    "cv": "scitex_cv",
    "introspect": "scitex_introspect",
    "msword": "scitex_msword",
    "os": "scitex_os",
    # `scitex.security`: ADR-0001 (scitex-dev #139, 2026-06-07) routed it to
    # `scitex_audit.github` (scitex-security absorbed into scitex-audit 0.2.0).
    # ADR-0002 (#142) then REVERSED the direction: `scitex_security` 0.2.0 is
    # the unified home and `scitex-audit` is now the deprecated thin shim.
    # The two ADRs conflict, and which package is installed varies. Primary
    # stays `scitex_audit.github` (ADR-0001 SSOT); `_EXTERNAL_FALLBACKS` adds
    # `scitex_security` so the module stays reachable whichever side resolves.
    # The 5 public symbols (check_github_alerts, save_alerts_to_file,
    # get_latest_alerts_file, format_alerts_report, GitHubSecurityError) are
    # exposed by both.
    "security": "scitex_audit.github",
    "session": "scitex_session",  # @scitex.session decorator + INJECTED sentinel
    "tex": "scitex_tex",
}


# Secondary external tried when the primary `EXTERNAL_REEXPORTS[<short>]` is
# not importable. Keeps `import scitex.<short>` and `scitex.<short>.X` working
# across the conflicting security ADRs (see the `security` note above). Mirrors
# the `fallback=` argument of `_LazyModule`.
_EXTERNAL_FALLBACKS = {
    "security": "scitex_security",
}


def register_external_lazy_modules() -> None:
    """Lazily register every external standalone in ``sys.modules``.

    `import scitex.io` resolves immediately (returns the lazy proxy), but the
    actual `scitex_io` module body — and its transitive cv2 / docx / torch
    imports — only runs on first attribute access. This keeps `import scitex`
    < 0.5s instead of 8s+.

    Mechanism: ``importlib.util.LazyLoader`` wraps the real loader;
    ``module_from_spec`` returns a proxy that delegates ``__getattr__`` to a
    deferred ``exec_module()``.
    """
    for _short, _ext in EXTERNAL_REEXPORTS.items():
        # Resolve the primary external, else its registered fallback (the
        # security-ADR conflict case). The first candidate that is importable
        # wins; both are pre-registered lazily under `scitex.<short>`.
        _candidates = [_ext]
        _fb = _EXTERNAL_FALLBACKS.get(_short)
        if _fb is not None:
            _candidates.append(_fb)
        if any(_c in sys.modules for _c in _candidates):
            # Already imported (e.g. by user code earlier in this process); reuse.
            _hit = next(_c for _c in _candidates if _c in sys.modules)
            sys.modules[f"scitex.{_short}"] = sys.modules[_hit]
            continue
        for _target in _candidates:
            try:
                _spec = _importlib_util.find_spec(_target)
            except (ImportError, ModuleNotFoundError):
                continue  # this candidate's parent is missing — try the next
            if _spec is None or _spec.loader is None:
                continue  # missing optional dep — try fallback, else proxy
            _spec.loader = _importlib_util.LazyLoader(_spec.loader)
            _mod = _importlib_util.module_from_spec(_spec)
            sys.modules[_target] = _mod
            sys.modules[f"scitex.{_short}"] = _mod
            _spec.loader.exec_module(_mod)  # records spec; defers body
            break  # candidate registered — done with this short


# =============================================================================
# Registry-driven alias finder (`import scitex.<short>` → peer standalone)
# =============================================================================
# `short` → `peer_import_name`. Branded peers (e.g. plt → figrecipe) get
# explicit entries; the rest follow the `scitex_<short>` convention by default,
# which the registry-driven map fills in automatically.
_DEFAULT_BRANDED = {
    "plt": "figrecipe.pyplot",
    "diagram": "figrecipe.diagram",  # in-tree dir removed; public figrecipe.diagram (>=0.28.13)
    "social": "socialia",
    "ai": "scitex_ml",  # ai split into ml + genai; default to ml
    "reproduce": "scitex_repro",  # umbrella name vs standalone short
    "rng": "scitex_repro",  # rng helpers ship from scitex_repro
    "verify": "scitex_clew",  # verify renamed to clew; in-tree dir removed
    "tunnel": "scitex_ssh",  # scitex-tunnel merged into scitex-ssh; in-tree dir removed
    "errors": "scitex_logging",  # error taxonomy lives in scitex-logging; in-tree shim removed
    "torch": "scitex_linalg",  # torch numerics (apply_to + nan reductions) live in scitex-linalg
    "dt": "scitex_datetime",  # legacy short for the dt module → standalone scitex-datetime
    # OPTIONAL peers — scitex-hub is NOT a hard dep (kept out of `[all]`). When
    # absent, the alias finder returns a `_make_missing_peer_stub` so
    # `import scitex.cloud` (and `.module` / `.project`) raise a friendly
    # install hint instead of crashing `import scitex`.
    "cloud": "scitex_hub",
    "module": "scitex_hub.module",
    "project": "scitex_hub.project",
}


def _build_alias_map() -> dict[str, str]:
    """Read scitex_dev._ecosystem registry; produce {short: peer_import}."""
    alias: dict[str, str] = dict(_DEFAULT_BRANDED)
    try:
        from scitex_dev._ecosystem._core import ECOSYSTEM
    except Exception:
        # Broad except: a misconfigured peer (e.g. tensorflow with a
        # mismatched protobuf raising VersionError at import time) shouldn't
        # break the umbrella's import — fall back to the explicit branded
        # map. The rest of the alias resolution still works for those names.
        return alias
    for dist, info in ECOSYSTEM.items():
        if info.get("category") == "umbrella":
            continue
        if info.get("archived"):
            continue
        # `scitex-foo` → short=`foo`, import=`scitex_foo`
        if not dist.startswith("scitex-"):
            continue  # branded standalones (figrecipe, socialia, …) handled above
        short = dist[len("scitex-") :]
        if short in alias:
            continue  # explicit override wins
        alias[short] = info.get("import_name") or f"scitex_{short.replace('-', '_')}"
    return alias


def _make_missing_peer_stub(short: str, peer: str) -> ModuleType:
    """Return a `ModuleType` that raises `ImportError` on any attribute access.

    Mirrors the contract of `scitex.plt` when `figrecipe` isn't installed.
    """
    mod = ModuleType(f"scitex.{short}")
    mod.__file__ = "<scitex.re_export stub>"
    mod.__path__ = []  # mark as a package for `import scitex.<short>.<sub>`
    mod._scitex_peer_missing = True  # type: ignore[attr-defined]
    mod._scitex_peer_name = peer  # type: ignore[attr-defined]

    install_hint = (
        f"`{peer}` is required for scitex.{short}. "
        f"Install with: pip install 'scitex[{short}]' "
        f"(or: pip install {peer.replace('_', '-')})"
    )

    def __getattr__(name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        raise ImportError(f"scitex.{short}.{name}: {install_hint}")

    def __dir__():
        return []

    mod.__getattr__ = __getattr__  # type: ignore[attr-defined]
    mod.__dir__ = __dir__  # type: ignore[attr-defined]
    return mod


class _ScitexAliasLoader(Loader):
    """Loader that binds `scitex.<short>[…]` to the peer module."""

    def __init__(self, fullname: str, peer: str, short: str, sub: Optional[str]):
        self._fullname = fullname
        self._peer = peer
        self._short = short
        self._sub = sub  # None for top-level alias; "utils.helpers" for deep

    def create_module(self, spec: ModuleSpec) -> Optional[ModuleType]:
        target_name = self._peer if self._sub is None else f"{self._peer}.{self._sub}"
        try:
            mod = importlib.import_module(target_name)
        except ImportError:
            if self._sub is None:
                return _make_missing_peer_stub(self._short, self._peer)
            # Sub-import failure on a present peer = real ImportError surface
            raise
        return mod

    def exec_module(self, module: ModuleType) -> None:
        # `create_module` already returned a fully-initialized peer module;
        # nothing left to execute.
        return None


class _ScitexAliasFinder(MetaPathFinder):
    """Resolve `scitex.<short>[…]` to the peer standalone module.

    Skipped when the in-tree `scitex/<short>/` directory exists — that's the
    "migration not started yet" escape hatch. Installation order matters: this
    finder must come AFTER the default path-based finders so on-disk dirs win.
    """

    def __init__(self, alias: Mapping[str, str], scitex_pkg_path: list):
        self._alias = dict(alias)
        # Resolve in-tree directory presence ONCE at construction; the umbrella
        # package layout doesn't change during a process lifetime.
        from pathlib import Path

        self._intree: set[str] = set()
        for parent in scitex_pkg_path:
            p = Path(parent)
            if not p.is_dir():
                continue
            for child in p.iterdir():
                if child.is_dir() and (child / "__init__.py").exists():
                    self._intree.add(child.name)

    def find_spec(self, fullname: str, path, target=None) -> Optional[ModuleSpec]:
        if not fullname.startswith("scitex."):
            return None
        rest = fullname[len("scitex.") :]
        short = rest.split(".", 1)[0]
        # If a real on-disk scitex/<short>/ exists, defer to it
        # (migration-not-started escape hatch).
        if short in self._intree:
            return None
        peer = self._alias.get(short)
        if peer is None:
            return None
        sub = rest[len(short) + 1 :] if "." in rest else None
        return ModuleSpec(
            fullname,
            _ScitexAliasLoader(fullname, peer, short, sub),
            is_package=(sub is None),
        )


_INSTALLED = False


def install_alias_finder(scitex_pkg_path: list) -> None:
    """Install the alias finder once. Idempotent."""
    global _INSTALLED
    if _INSTALLED:
        return
    alias = _build_alias_map()
    finder = _ScitexAliasFinder(alias, scitex_pkg_path)
    # Append (not insert) so default finders win first → real `scitex/<short>/`
    # directories stay authoritative for unmigrated peers.
    sys.meta_path.append(finder)
    _INSTALLED = True


__all__ = [
    "_LazyModule",
    "_CallableModuleWrapper",
    "EXTERNAL_REEXPORTS",
    "register_external_lazy_modules",
    "install_alias_finder",
]
