#!/usr/bin/env python3
# Timestamp: 2026-01-27
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/writer.py
"""Writer module tools - thin wrapper delegating to scitex-writer package.

Single source of truth: scitex-writer MCP tools.
"""


def register_writer_tools(mcp) -> None:
    """Register writer tools by delegating to scitex-writer package."""
    try:
        from scitex_writer._mcp.tools import register_all_tools

        # Delegate all MCP tools to scitex-writer
        register_all_tools(mcp)
    except ImportError:
        # Fallback when scitex-writer is not installed
        @mcp.tool()
        def writer_usage() -> str:
            """Get usage guide for SciTeX Writer (not installed)."""
            return "scitex-writer is required. Install with: pip install scitex-writer"


# EOF
