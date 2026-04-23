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
        """Return a function/class signature (parameters, types, defaults) by dotted import path — IPython `?` for any installed Python object. Drop-in replacement for `inspect.signature` + manual `typing.get_type_hints` + hand-formatted argspec dumps. Use whenever the user asks "what's the signature of X?", "how do I call scitex.io.save?", "what args does this take?", or is writing a call and needs parameter names without opening the source."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import q_handler

        return await async_wrap_as_mcp(
            q_handler,
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
        """Return the source code of a Python object by dotted import path — IPython `??`. Drop-in replacement for `inspect.getsource` + hunting through `pip show` paths or cloned repos. Use whenever the user asks "show me the source of X", "what does scitex.io.save actually do?", "read that function", or is debugging unexpected behavior and wants to see the implementation without opening a file."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import qq_handler

        return await async_wrap_as_mcp(
            qq_handler,
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
        """List attribute names of a module / class / instance with visibility + kind filter — `dir()` on steroids. `filter='public'` hides dunders + underscores; `kind='function'|'class'|'module'` filters by type; `include_inherited=True` walks the MRO. Drop-in replacement for `dir(obj)` + manual `startswith('_')` / `callable` filtering. Use whenever the user asks "what's in scitex.plt?", "list methods of this class", "show public API of module X", or is exploring an unfamiliar package."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import dir_handler

        return await async_wrap_as_mcp(
            dir_handler,
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
        """Recursively walk a package / module tree and return the full API as indented text — every submodule, class, function down to `max_depth`. Drop-in replacement for hand-crafted `pkgutil.walk_packages` + `dir()` loops. Use whenever the user asks "show me the whole API of scitex.stats", "map the package layout", "what does this expose?", or is getting oriented in a large library before coding."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import list_api_handler

        return await async_wrap_as_mcp(
            list_api_handler,
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
        """Return the docstring of any dotted-path object — raw, parsed into sections (Summary / Args / Returns / Raises / Examples), or just the one-line summary. Drop-in replacement for `obj.__doc__`, `inspect.getdoc`, and manual NumPy/Google-style parsing. Use whenever the user asks "what does this function do?", "show docstring for X", "summarize this API", or is reading documentation inline."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import docstring_handler

        return await async_wrap_as_mcp(
            docstring_handler,
            idempotent=True,
            dotted_path=dotted_path,
            format=format,
        )

    @mcp.tool()
    async def introspect_exports(dotted_path: str) -> str:
        """Return a module's `__all__` list — the officially-exposed public API names. Drop-in replacement for `import pkg; pkg.__all__`. Use when the user asks "what's exported from scitex.stats?", "list the public API", "which names are re-exported?", or is writing `from X import *` and wants to know what they'll get."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import exports_handler

        return await async_wrap_as_mcp(
            exports_handler,
            idempotent=True,
            dotted_path=dotted_path,
        )

    @mcp.tool()
    async def introspect_examples(
        dotted_path: str,
        search_paths: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Grep the repo's `tests/` and `examples/` for actual call sites of an object — real usage, not just docstring examples. Drop-in replacement for `rg 'scitex.io.save' tests/ examples/`. Use when the user asks "how do I use this function?", "show me real examples of X", "what does idiomatic usage look like?", or is learning a new API by example rather than from docstring."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import examples_handler

        # Parse search_paths if provided as comma-separated string
        paths_list = None
        if search_paths:
            paths_list = [p.strip() for p in search_paths.split(",")]

        return await async_wrap_as_mcp(
            examples_handler,
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
        """Return a class's inheritance tree — full MRO (walking up) + known subclasses (walking down) via `__subclasses__`. Drop-in replacement for `Cls.__mro__` + manual `issubclass` scans. Use when the user asks "what does X inherit from?", "show subclass tree of Y", "why does isinstance(Z) match?", or is debugging MRO / method-resolution issues in a class hierarchy."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import class_hierarchy_handler

        return await async_wrap_as_mcp(
            class_hierarchy_handler,
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
        """Resolve every type hint on a function/class — including forward refs, generics, Union / Optional / Literal / Annotated extras. Drop-in replacement for `typing.get_type_hints` + `typing.get_args` / `get_origin` by hand. Use when the user asks "what type is this param?", "show type hints for X", "does this accept None?", or is debugging a type-checking error / writing a wrapper that needs to match an existing signature."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import type_hints_handler

        return await async_wrap_as_mcp(
            type_hints_handler,
            idempotent=True,
            dotted_path=dotted_path,
            include_extras=include_extras,
        )

    @mcp.tool()
    async def introspect_imports(
        dotted_path: str,
        categorize: bool = True,
    ) -> str:
        """AST-parse a module's source and list every `import` / `from ... import` it uses — optionally grouped as stdlib / third-party / local. Drop-in replacement for `ast.parse` + hand-written `ast.NodeVisitor` + `importlib.util.find_spec` stdlib-detection. Use when the user asks "what does X import?", "categorize this module's dependencies", "is this using any third-party deps?", or is auditing imports before a refactor."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import imports_handler

        return await async_wrap_as_mcp(
            imports_handler,
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
        """Resolve the transitive dependency graph of a module — every other module it imports, optionally walking recursively to `max_depth`. Drop-in replacement for `pip show` + `modulefinder.ModuleFinder` + hand-walked `__import__` traces. Use when the user asks "what depends on X?", "show me the transitive deps", "is this module pulling in pandas?", or is planning a refactor / deletion and needs to know impact."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import dependencies_handler

        return await async_wrap_as_mcp(
            dependencies_handler,
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
        """Build a call graph rooted at a function — which other functions it calls, recursively to `max_depth`, with a wall-clock timeout (AST-based, safe on unknown code). `internal_only=True` ignores stdlib / third-party. Drop-in replacement for `pyan3`, `snakefood`, or hand-running `grep`-based call-site hunts. Use when the user asks "what does this call?", "show the call graph for X", "trace how function Y reaches Z", or is debugging / refactoring a tangled function chain."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.introspect._mcp.handlers import call_graph_handler

        return await async_wrap_as_mcp(
            call_graph_handler,
            idempotent=True,
            dotted_path=dotted_path,
            max_depth=max_depth,
            timeout_seconds=timeout_seconds,
            internal_only=internal_only,
        )
