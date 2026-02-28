#!/usr/bin/env python3
"""Dataset module tools - thin wrapper delegating to scitex-dataset package.

Single source of truth: scitex-dataset MCP tools.
"""



def register_dataset_tools(mcp) -> None:
    """Register dataset tools by delegating to scitex-dataset package."""
    try:
        from scitex_dataset._mcp.tools import register_all_tools

        # Delegate all MCP tools to scitex-dataset
        register_all_tools(mcp)
    except ImportError:
        # Fallback when scitex-dataset is not installed
        @mcp.tool()
        def dataset_usage() -> str:
            """[dataset] Get usage guide for SciTeX Dataset (not installed)."""
            return (
                "scitex-dataset is required. Install with: pip install scitex-dataset"
            )


# EOF
