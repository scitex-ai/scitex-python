#!/usr/bin/env python3
# Timestamp: 2026-03-05
# File: scitex/_mcp_tools/cloud.py
"""Cloud tools for FastMCP unified server.

Programmatically bridges all scitex-cloud MCP tools into scitex MCP.
No manual wrapping — any new scitex-cloud tool appears automatically.
"""


def register_cloud_tools(mcp) -> None:
    """Mount scitex-cloud MCP server with 'cloud' prefix.

    Uses mcp.mount() — same pattern as crossref-local and openalex-local.
    Tools are prefixed: cloud_repo_clone, cloud_api_status, cloud_on_site_eval_js, etc.
    """
    try:
        from scitex_cloud._mcp_server import mcp as cloud_mcp

        mcp.mount(cloud_mcp, prefix="cloud")
    except ImportError:

        @mcp.tool()
        async def cloud_not_available() -> str:
            """scitex-cloud not installed."""
            return (
                "scitex-cloud package required. Install with: pip install scitex-cloud"
            )


# EOF
