#!/usr/bin/env python3
# Timestamp: 2026-02-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/diagram.py
"""Diagram module tools for FastMCP unified server.

Programmatically bridges all figrecipe diagram_* tools into scitex MCP.
No manual wrapping — any new figrecipe diagram tool appears automatically.
"""

from __future__ import annotations


def register_diagram_tools(mcp) -> None:
    """Register all figrecipe diagram_* tools with the FastMCP server."""
    try:
        from figrecipe._mcp import server as fr_mcp
    except ImportError:

        @mcp.tool()
        def diagram_not_available() -> str:
            """[diagram] figrecipe not installed."""
            return "figrecipe is required. Install with: pip install figrecipe"

        return

    tools = fr_mcp.mcp._tool_manager._tools
    for name, tool in tools.items():
        if name.startswith("diagram_"):
            mcp.add_tool(tool)


# EOF
