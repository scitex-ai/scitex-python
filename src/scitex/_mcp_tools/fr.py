#!/usr/bin/env python3
# Timestamp: 2026-02-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/fr.py
"""FigRecipe specialized plot tools for FastMCP unified server.

Programmatically bridges all figrecipe fr_* tools into scitex MCP.
No manual wrapping — any new figrecipe fr tool appears automatically.
"""

from __future__ import annotations


def register_fr_tools(mcp) -> None:
    """Register all figrecipe fr_* tools with the FastMCP server."""
    try:
        from figrecipe._mcp import server as fr_mcp
    except ImportError:

        @mcp.tool()
        def fr_not_available() -> str:
            """[fr] figrecipe not installed."""
            return "figrecipe is required. Install with: pip install figrecipe"

        return

    tools = fr_mcp.mcp._tool_manager._tools
    for name, tool in tools.items():
        if name.startswith("fr_"):
            mcp.add_tool(tool)


# EOF
