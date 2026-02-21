#!/usr/bin/env python3
# Timestamp: 2026-02-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/diagram.py
"""Diagram module tools for FastMCP unified server.

Programmatically bridges all figrecipe diagram_* tools into scitex MCP,
renamed as plt_diagram_* for consistent scitex branding.
  diagram_create  →  plt_diagram_create
  diagram_render  →  plt_diagram_render
  ...
"""

from __future__ import annotations


def register_diagram_tools(mcp) -> None:
    """Register figrecipe diagram_* tools as plt_diagram_* in the FastMCP server."""
    try:
        from figrecipe._mcp import server as fr_mcp
    except ImportError:

        @mcp.tool()
        def plt_diagram_not_available() -> str:
            """[plt] figrecipe not installed."""
            return "figrecipe is required. Install with: pip install figrecipe"

        return

    tools = fr_mcp.mcp._tool_manager._tools
    for name, tool in tools.items():
        if name.startswith("diagram_"):
            new_name = "plt_diagram_" + name[len("diagram_") :]
            mcp.add_tool(tool.model_copy(update={"name": new_name}))


# EOF
