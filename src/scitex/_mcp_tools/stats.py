#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: src/scitex/_mcp_tools/stats.py
"""Stats tools for FastMCP unified server.

Programmatically bridges all scitex-stats MCP tools into scitex MCP.
No manual wrapping — any new stats tool appears automatically.
"""


def register_stats_tools(mcp) -> None:
    """Mount scitex-stats MCP server with 'stats' prefix.

    Uses mcp.mount() — same pattern as cloud, crossref-local, openalex-local.
    Tools are prefixed: stats_run_test, stats_recommend_tests, etc.
    """
    # Try standalone package first, then fall back to internal module
    try:
        from scitex_stats._server import mcp as stats_mcp

        mcp.mount(stats_mcp, namespace="stats")
    except ImportError:
        try:
            from scitex.stats._mcp.server import mcp as stats_mcp

            mcp.mount(stats_mcp, namespace="stats")
        except ImportError:

            @mcp.tool()
            async def stats_not_available() -> str:
                """scitex-stats not installed."""
                return (
                    "scitex-stats package required. "
                    "Install with: pip install scitex[stats]"
                )


# EOF
