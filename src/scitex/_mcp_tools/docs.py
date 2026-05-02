#!/usr/bin/env python3
"""MCP tools for docs aggregation and unified search via scitex-dev."""

from typing import Optional


def register_docs_tools(mcp) -> None:
    """Register documentation and search MCP tools."""

    @mcp.tool()
    async def docs_list() -> str:
        """Enumerate every installed SciTeX package that ships bundled Sphinx docs — each entry includes version, manifest path, and docs URL. Drop-in replacement for running `scitex-doc list` across every sub-CLI. Use when the user asks "what SciTeX packages are installed?", "which ones have docs?", "what's the ecosystem I have?", or before calling `docs_get` / `docs_search`."""
        from scitex_dev.docs import get_docs
        from scitex_dev._mcp import wrap_as_mcp

        return wrap_as_mcp(
            get_docs,
            idempotent=True,
        )

    @mcp.tool()
    async def docs_get(
        package: str,
        format: Optional[str] = None,
        page: Optional[str] = None,
    ) -> str:
        """Fetch a SciTeX package's bundled Sphinx docs — manifest (default), parsed JSON body, or a direct filesystem path to the built HTML. Drop-in replacement for manually hunting down `site-packages/<pkg>/_docs/index.html` or reading source README. Use when the user asks "show scitex-writer docs", "open the manual for X", "get the Sphinx output for Y", or is looking up per-function reference without opening the browser.

        Args:
            package: Package name (e.g. "scitex-writer").
            format: None for manifest, "json" for structured, "html" for path.
            page: Specific documentation page name.
        """
        from scitex_dev.docs import get_docs
        from scitex_dev._mcp import wrap_as_mcp

        return wrap_as_mcp(
            get_docs,
            idempotent=True,
            package=package,
            format=format,
            page=page,
        )

    @mcp.tool()
    async def docs_build(
        package: Optional[str] = None,
        formats: Optional[list[str]] = None,
    ) -> str:
        """Trigger `sphinx-build` on a single package or every installed SciTeX package, producing HTML and/or JSON output under each package's `_docs/_build/`. Drop-in replacement for `cd scitex-writer/docs && make html` in every repo. Use when the user asks to "rebuild docs", "regenerate Sphinx HTML", "refresh the manual for X", or after editing docstrings / `.rst` source.

        Args:
            package: Package name. None = build all.
            formats: List of builders ("html", "json"). Default: ["html"].
        """
        from scitex_dev.docs import build_docs
        from scitex_dev._mcp import wrap_as_mcp

        return wrap_as_mcp(
            build_docs,
            side_effects=["file_create: Sphinx HTML output in _build directory"],
            package=package,
            formats=formats,
        )

    @mcp.tool()
    async def docs_search(
        query: str,
        scope: str = "all",
        package: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Full-text search across every installed SciTeX package's docs / Python API / CLI reference / MCP tool registry — one Google-like query, cross-scope ranked results. Drop-in replacement for repeatedly grepping `site-packages/scitex*`, reading Sphinx separately, running `--help` on every CLI, and listing MCP servers by hand. Use whenever the user asks to "search the ecosystem for X", "find anything about figures / stats / writing", "which module does Y?", or is discovering functionality without knowing the owning package. Use `scope='api'|'cli'|'mcp'|'docs'` to narrow; `+required` / `-excluded` operators supported.

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
        from scitex_dev._mcp import wrap_as_mcp
        from scitex_dev.search import search

        return wrap_as_mcp(
            search,
            idempotent=True,
            query=query,
            scope=scope,
            package=package,
            max_results=max_results,
        )
