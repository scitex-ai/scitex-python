"""Clew tools for FastMCP unified server.

Programmatically bridges all scitex-clew MCP tools into scitex MCP via
`safe_mount` — every new scitex-clew tool appears automatically with the
`clew` namespace, matching the umbrella↔standalone passthrough rule.
"""


def register_clew_tools(mcp) -> None:
    """Mount scitex-clew MCP server with 'clew' namespace."""
    try:
        from scitex_clew._mcp.server import mcp as clew_mcp

        from ._compat import safe_mount

        safe_mount(mcp, clew_mcp, namespace="clew")
    except ImportError:

        @mcp.tool()
        async def clew_not_available() -> str:
            """scitex-clew not installed."""
            return "scitex-clew package required. Install with: pip install scitex-clew"


# EOF
