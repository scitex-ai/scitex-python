#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/_introspect_tools.py
"""IPython-style introspection MCP tools (scitex.introspect handlers).

Umbrella-only family — wraps the handlers under
``scitex.introspect._mcp.handlers``. Split out of ``_umbrella_tools`` to
keep each module focused and within the line budget.
"""

from __future__ import annotations

import importlib
from typing import Optional

__all__ = ["register_introspect_tools"]


async def _call(handler_name: str, **kwargs) -> str:
    """Resolve and invoke an introspect handler through the Result envelope."""
    from scitex_dev.ecosystem import async_wrap_as_mcp

    handlers = importlib.import_module("scitex.introspect._mcp.handlers")
    handler = getattr(handlers, handler_name)
    return await async_wrap_as_mcp(handler, idempotent=True, **kwargs)


def register_introspect_tools(mcp) -> None:
    """Register every introspect_* tool onto the FastMCP server."""

    @mcp.tool()
    async def introspect_signature(
        dotted_path: str,
        include_defaults: bool = True,
        include_annotations: bool = True,
    ) -> str:
        """Return a function/class signature (parameters, types, defaults) by dotted import path — IPython `?` for any installed Python object. Use whenever the user asks "what's the signature of X?", "how do I call scitex.io.save?", "what args does this take?"."""
        return await _call(
            "q_handler",
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
        """Return the source code of a Python object by dotted import path — IPython `??`. Use whenever the user asks "show me the source of X", "what does scitex.io.save actually do?", "read that function"."""
        return await _call(
            "qq_handler",
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
        """List attribute names of a module / class / instance with visibility + kind filter — `dir()` on steroids. Use whenever the user asks "what's in scitex.plt?", "list methods of this class", "show public API of module X"."""
        return await _call(
            "dir_handler",
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
        """Recursively walk a package / module tree and return the full API as indented text. Use whenever the user asks "show me the whole API of scitex.stats", "map the package layout", "what does this expose?"."""
        return await _call(
            "list_api_handler",
            dotted_path=dotted_path,
            max_depth=max_depth,
            docstring=docstring,
            root_only=root_only,
        )

    @mcp.tool()
    async def introspect_docstring(dotted_path: str, format: str = "raw") -> str:
        """Return the docstring of any dotted-path object — raw, parsed into sections, or one-line summary. Use whenever the user asks "what does this function do?", "show docstring for X", "summarize this API"."""
        return await _call("docstring_handler", dotted_path=dotted_path, format=format)

    @mcp.tool()
    async def introspect_exports(dotted_path: str) -> str:
        """Return a module's `__all__` list — the officially-exposed public API names. Use when the user asks "what's exported from scitex.stats?", "list the public API"."""
        return await _call("exports_handler", dotted_path=dotted_path)

    @mcp.tool()
    async def introspect_examples(
        dotted_path: str,
        search_paths: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Grep the repo's `tests/` and `examples/` for actual call sites of an object — real usage, not just docstring examples. Use when the user asks "how do I use this function?", "show me real examples of X"."""
        paths_list = (
            [p.strip() for p in search_paths.split(",")] if search_paths else None
        )
        return await _call(
            "examples_handler",
            dotted_path=dotted_path,
            search_paths=paths_list,
            max_results=max_results,
        )

    @mcp.tool()
    async def introspect_class_hierarchy(
        dotted_path: str,
        include_builtins: bool = False,
        max_depth: int = 10,
    ) -> str:
        """Return a class's inheritance tree — full MRO + known subclasses. Use when the user asks "what does X inherit from?", "show subclass tree of Y", "why does isinstance(Z) match?"."""
        return await _call(
            "class_hierarchy_handler",
            dotted_path=dotted_path,
            include_builtins=include_builtins,
            max_depth=max_depth,
        )

    @mcp.tool()
    async def introspect_type_hints(
        dotted_path: str, include_extras: bool = True
    ) -> str:
        """Resolve every type hint on a function/class — including forward refs, generics, Union / Optional / Literal / Annotated extras. Use when the user asks "what type is this param?", "show type hints for X", "does this accept None?"."""
        return await _call(
            "type_hints_handler",
            dotted_path=dotted_path,
            include_extras=include_extras,
        )

    @mcp.tool()
    async def introspect_imports(dotted_path: str, categorize: bool = True) -> str:
        """AST-parse a module's source and list every import it uses — optionally grouped as stdlib / third-party / local. Use when the user asks "what does X import?", "categorize this module's dependencies"."""
        return await _call(
            "imports_handler", dotted_path=dotted_path, categorize=categorize
        )

    @mcp.tool()
    async def introspect_dependencies(
        dotted_path: str, recursive: bool = False, max_depth: int = 3
    ) -> str:
        """Resolve the transitive dependency graph of a module. Use when the user asks "what depends on X?", "show me the transitive deps", "is this module pulling in pandas?"."""
        return await _call(
            "dependencies_handler",
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
        """Build a call graph rooted at a function — which other functions it calls, recursively to `max_depth`, with a wall-clock timeout. Use when the user asks "what does this call?", "show the call graph for X", "trace how function Y reaches Z"."""
        return await _call(
            "call_graph_handler",
            dotted_path=dotted_path,
            max_depth=max_depth,
            timeout_seconds=timeout_seconds,
            internal_only=internal_only,
        )


# EOF
