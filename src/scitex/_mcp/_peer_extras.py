#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/_peer_extras.py
"""Peer MCP surfaces that need umbrella-side adjustment beyond a plain mount.

The registry loop in ``__init__`` namespace-mounts each peer's FastMCP
server verbatim. A few peers need brand-naming or tool-name adjustments
that the generic loop cannot express:

* figrecipe ``fr_*`` tools -> re-exposed as ``plt_stx_*`` (scitex branding).
* socialia core tools -> registered as ``social_*`` (a curated subset:
  post/delete/status), in addition to the full ``socialia_*`` mount.
Dev owns its linter tools; Hub owns the hosted-platform tools. Both arrive
through the normal registry mounts, never a retired-package duplicate.

Each helper is best-effort: a missing optional peer logs and is skipped.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__all__ = ["register_peer_extras"]


def register_peer_extras(mcp) -> None:
    """Apply every umbrella-side peer adjustment onto the FastMCP server."""
    _register_figrecipe_plt_stx(mcp)
    _register_social_core(mcp)


def _register_figrecipe_plt_stx(mcp) -> None:
    """Re-expose figrecipe ``fr_*`` tools as ``plt_stx_*`` for scitex branding."""
    try:
        from figrecipe._mcp import server as fr_mcp
    except ImportError:
        logger.debug("figrecipe not installed — plt_stx_* tools skipped")
        return

    from ._compat import get_tools_sync

    tools = get_tools_sync(fr_mcp.mcp, include_mounted=False)
    for name, tool in tools.items():
        if name.startswith("fr_"):
            new_name = "plt_stx_" + name[len("fr_") :]
            mcp.add_tool(tool.model_copy(update={"name": new_name}))


def _register_social_core(mcp) -> None:
    """Register socialia's core social_* tools (post/delete/status)."""
    try:
        from socialia._mcp.tools import social
    except ImportError:
        logger.debug("socialia not installed — social_* tools skipped")
        return
    try:
        social.register_tools(mcp)
    except Exception as exc:  # noqa: BLE001 — diagnostic, never fatal
        logger.warning("socialia core social_* registration failed: %s", exc)


# EOF
