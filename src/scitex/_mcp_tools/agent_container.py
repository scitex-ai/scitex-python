#!/usr/bin/env python3
# Timestamp: 2026-05-06
# File: src/scitex/_mcp_tools/agent_container.py
"""scitex-agent-container tools for FastMCP unified server.

Mounts scitex-agent-container's MCP server with the
``agent_container`` namespace — same pattern as ``dataset``,
``cloud``, ``stats``. Standalone ``sac mcp start`` users see the
bare names (``agent_list``, ``db_query``, etc.); the umbrella adds
the ``agent_container_`` prefix at mount time so the umbrella tool
surface stays scoped per-package.
"""


def register_agent_container_tools(mcp) -> None:
    """Mount scitex-agent-container MCP server with 'agent_container' prefix."""
    try:
        from scitex_agent_container._mcp.server import get_server

        from ._compat import safe_mount

        safe_mount(mcp, get_server(), namespace="agent_container")
    except ImportError:

        @mcp.tool()
        def agent_container_not_available() -> str:
            """scitex-agent-container not installed."""
            return (
                "scitex-agent-container is required. "
                "Install with: pip install scitex-agent-container[mcp]"
            )


# EOF
