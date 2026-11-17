#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/mcp_server.py
"""Back-compat shim for the umbrella MCP server.

The real implementation now lives in :mod:`scitex._mcp`, a single
registry-mounting entrypoint. This module re-exports its public surface so
existing callers (`from scitex.mcp_server import main`, `scitex serve`,
external `scitex.mcp_server:main` references) keep working.
"""

from __future__ import annotations

from scitex._mcp import (  # noqa: F401
    FASTMCP_AVAILABLE,
    get_server,
    main,
    register_all_tools,
    run_server,
)

__all__ = [
    "mcp",
    "get_server",
    "run_server",
    "main",
    "register_all_tools",
    "FASTMCP_AVAILABLE",
]


def __getattr__(name: str):
    # ``mcp`` is built lazily by scitex._mcp (see its ``get_server``); forward
    # the attribute instead of binding it at import, which would build it.
    if name == "mcp":
        return get_server()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

if __name__ == "__main__":
    main()

# EOF
