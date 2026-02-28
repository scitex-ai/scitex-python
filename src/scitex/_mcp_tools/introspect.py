#!/usr/bin/env python3
# Timestamp: 2025-01-20
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/introspect.py

"""Introspection module tools for FastMCP unified server."""


import json
from typing import Optional


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def register_introspect_tools(mcp) -> None:
    """Register introspection tools with FastMCP server."""
    # IPython-style tools (primary)

    @mcp.tool()
    async def introspect_signature(
        dotted_path: str,
        include_defaults: bool = True,
        include_annotations: bool = True,
    ) -> str:
        """[introspect] Get function/class signature with parameters and types."""
        from scitex.introspect._mcp.handlers import q_handler

        result = await q_handler(
            dotted_path=dotted_path,
            include_defaults=include_defaults,
            include_annotations=include_annotations,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_source(
        dotted_path: str,
        max_lines: Optional[int] = None,
        include_decorators: bool = True,
    ) -> str:
        """[introspect] Get source code of a Python object."""
        from scitex.introspect._mcp.handlers import qq_handler

        result = await qq_handler(
            dotted_path=dotted_path,
            max_lines=max_lines,
            include_decorators=include_decorators,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_dir(
        dotted_path: str,
        filter: str = "public",
        kind: Optional[str] = None,
        include_inherited: bool = False,
    ) -> str:
        """[introspect] List members of module/class (like dir()). filter: all|public|private|dunder."""
        from scitex.introspect._mcp.handlers import dir_handler

        result = await dir_handler(
            dotted_path=dotted_path,
            filter=filter,
            kind=kind,
            include_inherited=include_inherited,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_api(
        dotted_path: str,
        max_depth: int = 5,
        docstring: bool = False,
        root_only: bool = False,
    ) -> str:
        """[introspect] List the API tree of a module recursively."""
        from scitex.introspect._mcp.handlers import list_api_handler

        result = await list_api_handler(
            dotted_path=dotted_path,
            max_depth=max_depth,
            docstring=docstring,
            root_only=root_only,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_docstring(
        dotted_path: str,
        format: str = "raw",
    ) -> str:
        """[introspect] Get docstring of a Python object. format: raw|parsed|summary."""
        from scitex.introspect._mcp.handlers import docstring_handler

        result = await docstring_handler(
            dotted_path=dotted_path,
            format=format,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_exports(dotted_path: str) -> str:
        """[introspect] Get __all__ exports of a module."""
        from scitex.introspect._mcp.handlers import exports_handler

        result = await exports_handler(dotted_path=dotted_path)
        return _json(result)

    @mcp.tool()
    async def introspect_examples(
        dotted_path: str,
        search_paths: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """[introspect] Find usage examples in tests/examples directories."""
        from scitex.introspect._mcp.handlers import examples_handler

        # Parse search_paths if provided as comma-separated string
        paths_list = None
        if search_paths:
            paths_list = [p.strip() for p in search_paths.split(",")]

        result = await examples_handler(
            dotted_path=dotted_path,
            search_paths=paths_list,
            max_results=max_results,
        )
        return _json(result)

    # Advanced introspection tools

    @mcp.tool()
    async def introspect_class_hierarchy(
        dotted_path: str,
        include_builtins: bool = False,
        max_depth: int = 10,
    ) -> str:
        """[introspect] Get class inheritance hierarchy (MRO + subclasses)."""
        from scitex.introspect._mcp.handlers import class_hierarchy_handler

        result = await class_hierarchy_handler(
            dotted_path=dotted_path,
            include_builtins=include_builtins,
            max_depth=max_depth,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_type_hints(
        dotted_path: str,
        include_extras: bool = True,
    ) -> str:
        """[introspect] Get detailed type hint analysis for function/class."""
        from scitex.introspect._mcp.handlers import type_hints_handler

        result = await type_hints_handler(
            dotted_path=dotted_path,
            include_extras=include_extras,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_imports(
        dotted_path: str,
        categorize: bool = True,
    ) -> str:
        """[introspect] Get all imports from a module (AST-based static analysis)."""
        from scitex.introspect._mcp.handlers import imports_handler

        result = await imports_handler(
            dotted_path=dotted_path,
            categorize=categorize,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_dependencies(
        dotted_path: str,
        recursive: bool = False,
        max_depth: int = 3,
    ) -> str:
        """[introspect] Get module dependencies (what it imports)."""
        from scitex.introspect._mcp.handlers import dependencies_handler

        result = await dependencies_handler(
            dotted_path=dotted_path,
            recursive=recursive,
            max_depth=max_depth,
        )
        return _json(result)

    @mcp.tool()
    async def introspect_call_graph(
        dotted_path: str,
        max_depth: int = 2,
        timeout_seconds: int = 10,
        internal_only: bool = True,
    ) -> str:
        """[introspect] Get function call graph (with timeout protection)."""
        from scitex.introspect._mcp.handlers import call_graph_handler

        result = await call_graph_handler(
            dotted_path=dotted_path,
            max_depth=max_depth,
            timeout_seconds=timeout_seconds,
            internal_only=internal_only,
        )
        return _json(result)
