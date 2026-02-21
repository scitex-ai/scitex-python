#!/usr/bin/env python3
# Timestamp: 2026-02-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/plt.py
"""Plt module tools for FastMCP unified server.

Programmatically bridges all figrecipe plt_* tools into scitex MCP.
No manual wrapping — any new figrecipe plt tool appears automatically.
"""

from __future__ import annotations


def register_plt_tools(mcp) -> None:
    """Register all figrecipe plt_* tools with the FastMCP server."""
    try:
        from figrecipe._mcp import server as fr_mcp
    except ImportError:

        @mcp.tool()
        def plt_not_available() -> str:
            """[plt] figrecipe not installed."""
            return "figrecipe is required. Install with: pip install figrecipe"

        return

    tools = fr_mcp.mcp._tool_manager._tools
    registered = 0
    for name, tool in tools.items():
        if name.startswith("plt_"):
            mcp.add_tool(tool)
            registered += 1


# EOF
