#!/usr/bin/env python3
"""Linter module tools - thin wrapper delegating to scitex-linter package.

Single source of truth: scitex-linter MCP tools.
"""



def register_linter_tools(mcp) -> None:
    """Register linter tools by delegating to scitex-linter package."""
    try:
        from scitex_linter._mcp.tools import register_all_tools

        register_all_tools(mcp)
    except ImportError:

        @mcp.tool()
        def linter_usage() -> str:
            """[linter] Get usage guide for SciTeX Linter (not installed)."""
            return "scitex-linter is required. Install with: pip install scitex-linter"


# EOF
