#!/usr/bin/env python3
"""Clew module tools - thin wrapper delegating to scitex-clew package.

Single source of truth: scitex-clew MCP tools.
"""


def register_clew_tools(mcp) -> None:
    """Register clew tools by delegating to scitex-clew package."""
    try:
        from scitex_clew._mcp.tools import register_all_tools

        register_all_tools(mcp)
    except ImportError:
        # Fallback when scitex-clew is not installed
        @mcp.tool()
        def clew_status() -> str:
            """Get clew verification status (not installed)."""
            return "scitex-clew is required. Install with: pip install scitex-clew"


# EOF
