#!/usr/bin/env python3
"""MCP tools for docs aggregation and unified search via scitex-dev."""

import json
from typing import Optional


def register_docs_tools(mcp) -> None:
    """Register documentation and search MCP tools."""

    @mcp.tool()
    async def docs_list() -> str:
        """List all installed SciTeX packages with documentation."""
        from scitex_dev.mcp import docs_list as _docs_list

        return _docs_list()

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
        from scitex_dev.mcp import docs_get as _docs_get

        return _docs_get(package=package, format=format, page=page)

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
        from scitex_dev.mcp import docs_build as _docs_build

        return _docs_build(package=package, formats=formats)

    @mcp.tool()
    async def docs_search(
        query: str,
        scope: str = "all",
        package: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Search documentation, APIs, CLI commands, and MCP tools across SciTeX.

        Query syntax (Google-like):
            "save figure"       → match any term
            '"exact phrase"'    → exact phrase match
            "+required term"    → term must appear
            "stats -deprecated" → exclude results with "deprecated"

        Args:
            query: Search query string.
            scope: What to search: "all", "api", "cli", "mcp", or "docs".
            package: Limit search to a single package.
            max_results: Maximum number of results.
        """
        from scitex_dev.search import search

        try:
            results = search(
                query=query,
                scope=scope,
                package=package,
                max_results=max_results,
            )
            return json.dumps(
                {
                    "success": True,
                    "data": results,
                    "query": query,
                    "scope": scope,
                    "count": len(results),
                    "next_steps": [
                        f"docs_get(package='{r['package']}', page='{r['name']}') for details"
                        for r in results[:3]
                    ],
                },
                default=str,
            )
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "next_steps": ["Check query and retry"],
                }
            )
