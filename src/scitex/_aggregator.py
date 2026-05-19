#!/usr/bin/env python3
"""scitex._aggregator — registry-driven peer-package alias finder.

Per the umbrella architecture rule:
- `scitex.<short>` should resolve to the standalone peer `scitex_<short>`
  (or the explicit `peer_import` for branded peers like `figrecipe`).
- The umbrella ships NO duplicate impl. Standalones are the single source
  of truth.
- A `scitex/<short>/` directory is only allowed when migration to the
  standalone hasn't started yet (no peer repo, or peer src is empty).
- Cross-peer glue lives in `scitex._integration` (NOT in any single
  `<short>/` dir).

This module installs a `MetaPathFinder` that intercepts every
`import scitex.<short>[.…]` and routes it to the peer module. Without
this finder, only attribute access (`scitex.dsp.foo` via `__getattr__`)
worked — submodule imports (`import scitex.dsp`) needed a real on-disk
`scitex/dsp/` dir.

Failure mode contract: when the peer is not installed,
`import scitex.<short>` succeeds (returns a stub module); any attribute
access on that stub raises `ImportError` with the install hint.
"""

from __future__ import annotations

import importlib
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Mapping, Optional

# `short` → `peer_import_name`. Branded peers (e.g. plt → figrecipe) get
# explicit entries; the rest follow the `scitex_<short>` convention by
# default, which the registry-driven map fills in automatically.
_DEFAULT_BRANDED = {
    "plt": "figrecipe",
    "social": "socialia",
    "ai": "scitex_ml",  # ai split into ml + genai; default to ml
    "reproduce": "scitex_repro",  # umbrella name vs standalone short
    "rng": "scitex_repro",  # rng helpers ship from scitex_repro
    "dt": "scitex_datetime",  # legacy short for scitex_core.dt → standalone
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
    mod.__file__ = "<scitex._aggregator stub>"
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

    Skipped when the in-tree `scitex/<short>/` directory exists — that's
    the "migration not started yet" escape hatch. Installation order
    matters: this finder must come AFTER the default path-based finders so
    on-disk dirs win.
    """

    def __init__(self, alias: Mapping[str, str], scitex_pkg_path: list):
        self._alias = dict(alias)
        # Resolve in-tree directory presence ONCE at construction; the
        # umbrella package layout doesn't change during a process lifetime.
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


__all__ = ["install_alias_finder"]
