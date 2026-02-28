#!/usr/bin/env python3
# Timestamp: 2026-01-27
# File: /home/ywatanabe/proj/scitex-python/src/scitex/_mcp_tools/social.py
"""Social module tools - thin wrapper delegating to socialia package.

Single source of truth: socialia MCP tools.
"""



def register_social_tools(mcp) -> None:
    """Register social tools by delegating to socialia package.

    Only registers core tools (post, delete, status).
    Analytics tools are excluded to reduce tool count.
    """
    try:
        from socialia._mcp.tools import social

        # Register only core social tools (post, delete, status)
        # Analytics tools (pageviews, realtime, sources, track) excluded
        social.register_tools(mcp)
    except ImportError:
        # Fallback when socialia is not installed
        @mcp.tool()
        def social_status() -> str:
            """[social] Get social media status (not installed)."""
            return "socialia is required. Install with: pip install socialia"


# EOF
