#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: src/scitex/_mcp_tools/io.py
"""IO module tools for FastMCP unified server.

Mounts scitex-io MCP server — same pattern as stats, clew.
Any new tool in scitex-io appears automatically.
"""


def register_io_tools(mcp) -> None:
    """Mount scitex-io MCP server with 'io' prefix."""
    try:
        from scitex_io._mcp.server import mcp as io_mcp

        from ._compat import safe_mount

        safe_mount(mcp, io_mcp, namespace="io")
    except ImportError:

        @mcp.tool()
        def io_not_available() -> str:
            """scitex-io not installed."""
            return "scitex-io is required. Install with: pip install scitex-io[mcp]"


# EOF
