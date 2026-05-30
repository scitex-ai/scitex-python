#!/usr/bin/env python3
"""Linter module tools — delegate to scitex_dev.linter MCP tools.

Single source of truth: `scitex_dev.linter._mcp.tools`. The engine
moved out of the (archived) scitex-linter package; this stays as a
thin re-export so the umbrella's MCP server still exposes the same
tools.
"""


def register_linter_tools(mcp) -> None:
    """Register linter tools by delegating to scitex_dev.linter."""
    try:
        from scitex_dev.linter._mcp.tools import register_all_tools

        register_all_tools(mcp)
    except ImportError:

        @mcp.tool()
        def linter_usage() -> str:
            """Get usage guide for SciTeX Linter (not installed)."""
            return "scitex-dev is required. Install with: pip install scitex-dev"


# EOF
