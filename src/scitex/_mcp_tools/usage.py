#!/usr/bin/env python3
"""Usage module MCP tools — discover scitex usage examples."""


def register_usage_tools(mcp) -> None:
    """Register usage discovery tools."""

    @mcp.tool()
    def usage_show(topic: str = "") -> str:
        """Return a runnable code example for a SciTeX topic (`plt`, `stats`, `session`, `io`, `scholar`, …) — short, copy-pasteable snippets showing idiomatic usage. Drop-in replacement for hunting through `examples/`, rereading SKILL.md, or searching PyPI docs. Use when the user asks "how do I use scitex.plt?", "show me a t-test example", "give me a session boilerplate", "what's the idiomatic way to save a figure?", or needs a starting point rather than reference docs."""
        from scitex_dev._mcp import wrap_as_mcp

        from scitex.usage import show

        return wrap_as_mcp(
            show,
            idempotent=True,
            topic=topic or None,
        )

    @mcp.tool()
    def usage_list() -> str:
        """List every topic `usage_show` can serve (`plt`, `stats`, `session`, `io`, `scholar`, `audio`, `writer`, …). Use when the user asks "what examples are available?", "which modules have usage snippets?", or before calling `usage_show` with a specific topic."""
        from scitex_dev._mcp import wrap_as_mcp

        from scitex.usage import topics

        return wrap_as_mcp(
            topics,
            idempotent=True,
        )


# EOF
