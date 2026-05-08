#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registry-driven FastMCP tool registration for the scitex umbrella.

Single source of truth: the scitex-dev ecosystem registry
(``scitex_dev._ecosystem._core.ECOSYSTEM``) lists every peer package
along with its ``import_name`` and ``umbrella_subcommand``. For each
non-archived, non-umbrella entry, we attempt to import its FastMCP
instance from the canonical paths and ``safe_mount`` it under the
declared subcommand namespace.

This replaces the historical pattern of one hand-written
``register_<pkg>_tools`` bridge file per peer (anti-pattern; see
``_skills/general/03_interface_03_mcp/02_server-registration.md`` —
"Hand-wrapping is an anti-pattern"). New tools added to a peer's
``_mcp_server`` propagate automatically; no umbrella-side maintenance.

Backward-compat for bridge files: any module ``scitex._mcp_tools.<pkg>``
that still defines ``register_<pkg>_tools`` is invoked AFTER the
registry loop, so partly-migrated bridges (mixed safe_mount + inline
``@mcp.tool``) keep their inline tools until the residual hand-wrap is
moved into the peer package.
"""

from __future__ import annotations

import importlib
import logging
import os
from typing import Iterable

logger = logging.getLogger(__name__)

__all__ = ["register_all_tools"]

# Canonical places a FastMCP instance might live in a peer package.
# Mirrors `scitex_dev._cli.audit._summary._mcp_audit._resolve_mcp_server`.
_MCP_PATH_CANDIDATES = (
    "_mcp_server",
    "mcp_server",
    "_mcp.server",
    "mcp.server",
)
_MCP_ATTR_CANDIDATES = ("mcp", "server", "app")

# Categories the umbrella does NOT mount.
_SKIP_CATEGORIES = frozenset({"umbrella", "template"})

# Namespace overrides — registry's `umbrella_subcommand` may differ from
# the prefix consumers already know. Apply these renames so existing
# tool names (`crossref_search`, not `crossref-local_search`) survive
# the cutover from per-package bridges to registry-driven mounts.
_NAMESPACE_ALIASES: dict[str, str] = {
    "crossref-local": "crossref",
    "openalex-local": "openalex",
    # The CLI subcommand is "agent-container"; the historical MCP
    # namespace was the underscore form so existing tool names stay
    # compatible after the rename.
    "agent-container": "agent_container",
}


def _env_gate_key(namespace: str) -> str:
    """Return the legacy SCITEX_MCP_USE_<NS> env-var name for a namespace."""
    return "SCITEX_MCP_USE_" + namespace.upper().replace("-", "_")


def _is_enabled(namespace: str) -> bool:
    """Honour ``SCITEX_MCP_USE_<NS>=0`` to skip a peer mount."""
    return os.environ.get(_env_gate_key(namespace), "1") != "0"


def _resolve_peer_mcp(import_name: str):
    """Try every canonical location for a peer's FastMCP instance.

    Returns the FastMCP object on first match, or None.
    """
    try:
        from fastmcp import FastMCP
    except ImportError:
        return None

    for sub in _MCP_PATH_CANDIDATES:
        mod_name = f"{import_name}.{sub}"
        try:
            mod = importlib.import_module(mod_name)
        except BaseException:
            # `BaseException` because some peers `sys.exit(1)` at import
            # if their preconditions (env vars, optional deps) fail.
            # SystemExit derives from BaseException — a bare ``except
            # Exception`` would let it kill the umbrella import.
            continue
        for attr in _MCP_ATTR_CANDIDATES:
            obj = getattr(mod, attr, None)
            if isinstance(obj, FastMCP):
                return obj
    return None


def _iter_registry() -> Iterable[tuple[str, str, str]]:
    """Yield ``(pip_name, import_name, namespace)`` for every mountable peer.

    Falls back gracefully when scitex-dev is not installed (no peer
    auto-mounts; only the manual extras run).
    """
    try:
        from scitex_dev._ecosystem._core import ECOSYSTEM
    except ImportError:
        logger.warning(
            "scitex-dev not installed — peer MCP auto-mount disabled "
            "(install scitex-dev to enable)."
        )
        return

    for pip_name, info in ECOSYSTEM.items():
        if info.get("archived"):
            continue
        if info.get("category") in _SKIP_CATEGORIES:
            continue
        import_name = info.get("import_name")
        if not import_name:
            continue
        namespace = info.get("umbrella_subcommand", pip_name.removeprefix("scitex-"))
        namespace = _NAMESPACE_ALIASES.get(namespace, namespace)
        yield pip_name, import_name, namespace


def _mount_peer(mcp, peer_mcp, namespace: str) -> bool:
    """Run ``safe_mount`` and report success."""
    from ._compat import safe_mount

    try:
        safe_mount(mcp, peer_mcp, namespace=namespace)
        return True
    except Exception as exc:  # noqa: BLE001 — diagnostic, never fatal
        logger.warning("MCP mount failed for %r: %s", namespace, exc)
        return False


def _run_legacy_bridges(mcp, mounted: set[str]) -> list[str]:
    """Invoke any per-package ``register_<pkg>_tools`` shim still present.

    These are the remaining hand-wrap files; they exist only for
    namespaces whose peer doesn't yet expose ``_mcp_server.mcp``. When
    the registry loop already mounted a namespace, the matching bridge
    is skipped to avoid double-registering tools.

    Bridge stems may use underscores where the registry uses hyphens
    (``agent_container.py`` ↔ ``agent-container``); we compare both
    forms before deciding to skip.
    """
    invoked: list[str] = []
    package_dir = os.path.dirname(__file__)
    for fname in sorted(os.listdir(package_dir)):
        if not fname.endswith(".py"):
            continue
        if fname.startswith("_"):
            continue
        stem = fname[:-3]
        # Skip when the registry already mounted this namespace, in
        # either underscore or hyphen form.
        stem_hyphen = stem.replace("_", "-")
        if stem in mounted or stem_hyphen in mounted:
            continue
        try:
            mod = importlib.import_module(f"{__name__}.{stem}")
        except BaseException as exc:
            logger.warning("legacy bridge %s import failed: %s", stem, exc)
            continue
        register = getattr(mod, f"register_{stem}_tools", None)
        if register is None:
            continue
        if not _is_enabled(stem):
            continue
        try:
            register(mcp)
            invoked.append(stem)
        except Exception as exc:  # noqa: BLE001
            logger.warning("legacy bridge %s.register raised: %s", stem, exc)
    return invoked


def register_all_tools(mcp) -> None:
    """Register every peer's FastMCP tools onto the umbrella server.

    Order:
      1. Registry-driven safe_mount of peer ``_mcp_server`` instances.
      2. Any remaining legacy ``register_<pkg>_tools`` bridge whose
         namespace wasn't already mounted in step 1.

    Each peer is gated by ``SCITEX_MCP_USE_<NAMESPACE>=0`` (default
    enabled); legacy bridges honour the same gate keyed by the bridge
    file's stem.
    """
    mounted: set[str] = set()
    skipped: list[str] = []

    # 1. Registry loop ----------------------------------------------------
    for _pip, import_name, namespace in _iter_registry():
        if not _is_enabled(namespace):
            skipped.append(f"{namespace}(gated)")
            continue
        peer_mcp = _resolve_peer_mcp(import_name)
        if peer_mcp is None:
            continue
        if _mount_peer(mcp, peer_mcp, namespace):
            mounted.add(namespace)

    # 2. Legacy bridge fallback -------------------------------------------
    invoked = _run_legacy_bridges(mcp, mounted)

    if mounted:
        logger.info(
            "MCP umbrella mounted %d peer servers: %s",
            len(mounted),
            ", ".join(sorted(mounted)),
        )
    if invoked:
        logger.info(
            "MCP umbrella ran %d legacy bridges: %s",
            len(invoked),
            ", ".join(invoked),
        )
    if skipped:
        logger.debug("MCP umbrella skipped: %s", ", ".join(skipped))


# EOF
