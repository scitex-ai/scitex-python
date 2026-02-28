#!/usr/bin/env python3
# Timestamp: 2026-02-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/plt.py
"""Plt module tools for FastMCP unified server.

Programmatically bridges all figrecipe plt_* tools into scitex MCP.
No manual wrapping — any new figrecipe plt tool appears automatically.
"""


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

    from ._compat import get_tools_sync

    tools = get_tools_sync(fr_mcp.mcp, include_mounted=False)
    registered = 0
    for name, tool in tools.items():
        if name.startswith("plt_"):
            mcp.add_tool(tool)
            registered += 1


# EOF
