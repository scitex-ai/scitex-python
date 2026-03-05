#!/usr/bin/env python3
"""Usage module MCP tools — discover scitex usage examples."""


def register_usage_tools(mcp) -> None:
    """Register usage discovery tools."""

    @mcp.tool()
    def usage_show(topic: str = "") -> str:
        """Show usage examples for a scitex module (plt, stats, session, etc.)."""
        from scitex.usage import show

        return show(topic or None)

    @mcp.tool()
    def usage_list() -> str:
        """List available usage topics."""
        from scitex.usage import topics

        return "\n".join(topics())


# EOF
