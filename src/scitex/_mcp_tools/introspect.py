#!/usr/bin/env python3
# Timestamp: 2025-01-20
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/introspect.py

"""Introspection module tools for FastMCP unified server."""

from typing import Optional


def register_introspect_tools(mcp) -> None:
    """Register introspection tools with FastMCP server."""
    # IPython-style tools (primary)

    @mcp.tool()
    async def introspect_signature(
        dotted_path: str,
        include_defaults: bool = True,
        include_annotations: bool = True,
    ) -> str:
        """Get function/class signature with parameters and types."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import q_handler

        return await async_wrap_as_mcp(
            q_handler,
            next_steps=[
                "introspect_source to see full source code",
                "introspect_docstring for detailed documentation",
            ],
            idempotent=True,
            dotted_path=dotted_path,
            include_defaults=include_defaults,
            include_annotations=include_annotations,
        )

    @mcp.tool()
    async def introspect_source(
        dotted_path: str,
        max_lines: Optional[int] = None,
        include_decorators: bool = True,
    ) -> str:
        """Get source code of a Python object."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import qq_handler

        return await async_wrap_as_mcp(
            qq_handler,
            next_steps=[
                "introspect_call_graph to see what this function calls",
                "introspect_examples to find usage examples",
            ],
            idempotent=True,
            dotted_path=dotted_path,
            max_lines=max_lines,
            include_decorators=include_decorators,
        )

    @mcp.tool()
    async def introspect_dir(
        dotted_path: str,
        filter: str = "public",
        kind: Optional[str] = None,
        include_inherited: bool = False,
    ) -> str:
        """List members of module/class (like dir()). filter: all|public|private|dunder."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import dir_handler

        return await async_wrap_as_mcp(
            dir_handler,
            next_steps=[
                "introspect_signature for details on a specific member",
                "introspect_api for recursive API tree",
            ],
            idempotent=True,
            dotted_path=dotted_path,
            filter=filter,
            kind=kind,
            include_inherited=include_inherited,
        )

    @mcp.tool()
    async def introspect_api(
        dotted_path: str,
        max_depth: int = 5,
        docstring: bool = False,
        root_only: bool = False,
    ) -> str:
        """List the API tree of a module recursively."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import list_api_handler

        return await async_wrap_as_mcp(
            list_api_handler,
            next_steps=[
                "introspect_signature for details on a specific API",
                "introspect_source to read implementation",
            ],
            idempotent=True,
            dotted_path=dotted_path,
            max_depth=max_depth,
            docstring=docstring,
            root_only=root_only,
        )

    @mcp.tool()
    async def introspect_docstring(
        dotted_path: str,
        format: str = "raw",
    ) -> str:
        """Get docstring of a Python object. format: raw|parsed|summary."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import docstring_handler

        return await async_wrap_as_mcp(
            docstring_handler,
            next_steps=[
                "introspect_signature for parameter details",
                "introspect_examples for usage examples",
            ],
            idempotent=True,
            dotted_path=dotted_path,
            format=format,
        )

    @mcp.tool()
    async def introspect_exports(dotted_path: str) -> str:
        """Get __all__ exports of a module."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import exports_handler

        return await async_wrap_as_mcp(
            exports_handler,
            next_steps=["introspect_dir for all members including non-exported"],
            idempotent=True,
            dotted_path=dotted_path,
        )

    @mcp.tool()
    async def introspect_examples(
        dotted_path: str,
        search_paths: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Find usage examples in tests/examples directories."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import examples_handler

        # Parse search_paths if provided as comma-separated string
        paths_list = None
        if search_paths:
            paths_list = [p.strip() for p in search_paths.split(",")]

        return await async_wrap_as_mcp(
            examples_handler,
            next_steps=["introspect_source to read the referenced source code"],
            idempotent=True,
            dotted_path=dotted_path,
            search_paths=paths_list,
            max_results=max_results,
        )

    # Advanced introspection tools

    @mcp.tool()
    async def introspect_class_hierarchy(
        dotted_path: str,
        include_builtins: bool = False,
        max_depth: int = 10,
    ) -> str:
        """Get class inheritance hierarchy (MRO + subclasses)."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import class_hierarchy_handler

        return await async_wrap_as_mcp(
            class_hierarchy_handler,
            next_steps=["introspect_source to read a specific class"],
            idempotent=True,
            dotted_path=dotted_path,
            include_builtins=include_builtins,
            max_depth=max_depth,
        )

    @mcp.tool()
    async def introspect_type_hints(
        dotted_path: str,
        include_extras: bool = True,
    ) -> str:
        """Get detailed type hint analysis for function/class."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import type_hints_handler

        return await async_wrap_as_mcp(
            type_hints_handler,
            next_steps=["introspect_signature for full signature with defaults"],
            idempotent=True,
            dotted_path=dotted_path,
            include_extras=include_extras,
        )

    @mcp.tool()
    async def introspect_imports(
        dotted_path: str,
        categorize: bool = True,
    ) -> str:
        """Get all imports from a module (AST-based static analysis)."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import imports_handler

        return await async_wrap_as_mcp(
            imports_handler,
            next_steps=["introspect_dependencies for recursive dependency tree"],
            idempotent=True,
            dotted_path=dotted_path,
            categorize=categorize,
        )

    @mcp.tool()
    async def introspect_dependencies(
        dotted_path: str,
        recursive: bool = False,
        max_depth: int = 3,
    ) -> str:
        """Get module dependencies (what it imports)."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import dependencies_handler

        return await async_wrap_as_mcp(
            dependencies_handler,
            next_steps=["introspect_imports for detailed import analysis"],
            idempotent=True,
            dotted_path=dotted_path,
            recursive=recursive,
            max_depth=max_depth,
        )

    @mcp.tool()
    async def introspect_call_graph(
        dotted_path: str,
        max_depth: int = 2,
        timeout_seconds: int = 10,
        internal_only: bool = True,
    ) -> str:
        """Get function call graph (with timeout protection)."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import call_graph_handler

        return await async_wrap_as_mcp(
            call_graph_handler,
            next_steps=["introspect_source to read a specific function in the graph"],
            idempotent=True,
            dotted_path=dotted_path,
            max_depth=max_depth,
            timeout_seconds=timeout_seconds,
            internal_only=internal_only,
        )
