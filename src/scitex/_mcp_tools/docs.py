#!/usr/bin/env python3
"""MCP tools for docs aggregation and unified search via scitex-dev."""

from typing import Optional


def register_docs_tools(mcp) -> None:
    """Register documentation and search MCP tools."""

    @mcp.tool()
    async def docs_list() -> str:
        """List all installed SciTeX packages with documentation."""
        from scitex_dev.docs import get_docs
        from scitex_dev.mcp_utils import wrap_as_mcp

        return wrap_as_mcp(get_docs)

    @mcp.tool()
    async def docs_get(
        package: str,
        format: Optional[str] = None,
        page: Optional[str] = None,
    ) -> str:
        """Get documentation for a specific SciTeX package.

        Args:
            package: Package name (e.g. "scitex-writer").
            format: None for manifest, "json" for structured, "html" for path.
            page: Specific documentation page name.
        """
        from scitex_dev.docs import get_docs
        from scitex_dev.mcp_utils import wrap_as_mcp

        return wrap_as_mcp(get_docs, package=package, format=format, page=page)

    @mcp.tool()
    async def docs_build(
        package: Optional[str] = None,
        formats: Optional[list[str]] = None,
    ) -> str:
        """Build documentation from Sphinx source for one or all packages.

        Args:
            package: Package name. None = build all.
            formats: List of builders ("html", "json"). Default: ["html"].
        """
        from scitex_dev.docs import build_docs
        from scitex_dev.mcp_utils import wrap_as_mcp

        return wrap_as_mcp(build_docs, package=package, formats=formats)

    @mcp.tool()
    async def docs_search(
        query: str,
        scope: str = "all",
        package: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Search documentation, APIs, CLI commands, and MCP tools across SciTeX.

        Query syntax (Google-like):
            "save figure"       -> match any term
            '"exact phrase"'    -> exact phrase match
            "+required term"    -> term must appear
            "stats -deprecated" -> exclude results with "deprecated"

        Args:
            query: Search query string.
            scope: What to search: "all", "api", "cli", "mcp", or "docs".
            package: Limit search to a single package.
            max_results: Maximum number of results.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp
        from scitex_dev.search import search

        return wrap_as_mcp(
            search,
            query=query,
            scope=scope,
            package=package,
            max_results=max_results,
        )
