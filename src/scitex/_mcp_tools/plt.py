#!/usr/bin/env python3
# Timestamp: 2026-02-21
# File: src/scitex/_mcp_tools/plt.py
"""Plt module tools for FastMCP unified server.

Bridges figrecipe plt_* tools into scitex MCP.
Note: figrecipe serves plt_*, fr_*, diagram_* from one MCP server.
Each prefix is cherry-picked separately (plt.py, fr.py, diagram.py)
because fr_* and diagram_* need renaming (fr_* → plt_stx_*, diagram_* → plt_diagram_*).
"""


def register_plt_tools(mcp) -> None:
    """Register all figrecipe plt_* tools with the FastMCP server."""
    try:
        from figrecipe._mcp import server as fr_mcp
    except ImportError:

        @mcp.tool()
        def plt_not_available() -> str:
            """Figrecipe not installed."""
            return "figrecipe is required. Install with: pip install figrecipe"

        return

    from ._compat import get_tools_sync

    tools = get_tools_sync(fr_mcp.mcp, include_mounted=False)
    for name, tool in tools.items():
        if name.startswith("plt_"):
            mcp.add_tool(tool)


# EOF
