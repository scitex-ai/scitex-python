#!/usr/bin/env python3
# Timestamp: 2026-05-04
# File: scitex/_mcp_tools/dev.py
"""Developer tools for FastMCP unified server.

Programmatically bridges all scitex-dev MCP tools into scitex MCP.
No manual wrapping — any new scitex-dev tool appears automatically.
"""


def register_dev_tools(mcp) -> None:
    """Mount scitex-dev MCP server with 'dev' prefix.

    Uses safe_mount() — same pattern as crossref-local, openalex-local,
    cloud, etc. Tools are prefixed: dev_ecosystem_list, dev_docs_search,
    dev_skills_list, dev_bulk_rename, etc.
    """
    try:
        from scitex_dev._mcp._server import mcp as dev_mcp

        from ._compat import safe_mount

        safe_mount(mcp, dev_mcp, namespace="dev")
    except ImportError:

        @mcp.tool()
        async def dev_not_available() -> str:
            """scitex-dev not installed."""
            return "scitex-dev package required. Install with: pip install scitex-dev"
