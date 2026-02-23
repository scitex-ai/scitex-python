#!/usr/bin/env python3
# Timestamp: 2026-02-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/fr.py
"""FigRecipe specialized plot tools for FastMCP unified server.

Programmatically bridges all figrecipe fr_* tools into scitex MCP,
renamed as plt_stx_* for consistent scitex branding.
  fr_conf_mat  →  plt_stx_conf_mat
  fr_ecdf      →  plt_stx_ecdf
  ...
"""


def register_fr_tools(mcp) -> None:
    """Register figrecipe fr_* tools as plt_stx_* in the FastMCP server."""
    try:
        from figrecipe._mcp import server as fr_mcp
    except ImportError:

        @mcp.tool()
        def plt_stx_not_available() -> str:
            """[plt] figrecipe not installed."""
            return "figrecipe is required. Install with: pip install figrecipe"

        return

    from ._compat import get_tools_sync

    tools = get_tools_sync(fr_mcp.mcp, include_mounted=False)
    for name, tool in tools.items():
        if name.startswith("fr_"):
            new_name = "plt_stx_" + name[len("fr_") :]
            mcp.add_tool(tool.model_copy(update={"name": new_name}))


# EOF
