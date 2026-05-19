#!/usr/bin/env python3
# Timestamp: 2026-05-06
# File: src/scitex/_mcp_tools/dataset.py
"""Dataset tools for FastMCP unified server.

Mounts scitex-dataset MCP server with the ``dataset`` namespace —
same pattern as cloud, io, stats, clew. Tools become
``dataset_openneuro_fetch``, ``dataset_db_build``, etc.

Standalone scitex-dataset users see the bare names
(``openneuro_fetch``, ``db_build``); the umbrella adds the prefix at
mount time so the umbrella tool surface stays scoped per-package.
"""


def register_dataset_tools(mcp) -> None:
    """Mount scitex-dataset MCP server with 'dataset' prefix."""
    try:
        from scitex_dataset._mcp.server import mcp as dataset_mcp

        from ._compat import safe_mount

        safe_mount(mcp, dataset_mcp, namespace="dataset")
    except ImportError:

        @mcp.tool()
        def dataset_not_available() -> str:
            """scitex-dataset not installed."""
            return (
                "scitex-dataset is required. Install with: pip install scitex-dataset"
            )


# EOF
