"""Writer tools for FastMCP unified server.

Programmatically bridges all scitex-writer MCP tools into scitex MCP via
`safe_mount` — every new scitex-writer tool appears automatically with the
`writer` namespace, matching the umbrella↔standalone passthrough rule.
"""


def register_writer_tools(mcp) -> None:
    """Mount scitex-writer MCP server with 'writer' namespace."""
    try:
        from scitex_writer._mcp_server import mcp as writer_mcp

        from ._compat import safe_mount

        safe_mount(mcp, writer_mcp, namespace="writer")
    except ImportError:

        @mcp.tool()
        async def writer_not_available() -> str:
            """scitex-writer not installed."""
            return "scitex-writer package required. Install with: pip install scitex-writer"


# EOF
