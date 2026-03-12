#!/usr/bin/env python3
"""Usage module MCP tools — discover scitex usage examples."""


def register_usage_tools(mcp) -> None:
    """Register usage discovery tools."""

    @mcp.tool()
    def usage_show(topic: str = "") -> str:
        """Show usage examples for a scitex module (plt, stats, session, etc.)."""
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.usage import show

        return wrap_as_mcp(show, topic=topic or None)

    @mcp.tool()
    def usage_list() -> str:
        """List available usage topics."""
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.usage import topics

        return wrap_as_mcp(topics)


# EOF
