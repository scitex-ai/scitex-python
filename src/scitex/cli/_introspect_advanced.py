#!/usr/bin/env python3
"""Advanced introspection CLI commands (docstring, exports, examples, hierarchy, hints, imports, deps, calls)."""

import sys

import click

from ._introspect_helpers import echo_json_error, echo_json_result


def _normalize_path(ctx, param, value):
    """Normalize dotted path: convert hyphens to underscores for Python module names."""
    if value:
        return value.replace("-", "_")
    return value


def _print_subclasses(subclasses, indent=0):
    """Helper to print subclass tree."""
    for sub in subclasses:
        click.echo(" " * indent + f"- {sub['qualname']}")
        if "subclasses" in sub:
            _print_subclasses(sub["subclasses"], indent + 2)


def register_advanced_commands(group):  # noqa: C901
    """Register advanced introspection commands on the given click group."""

    @group.command()
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["raw", "parsed", "summary"]),
        default="raw",
        help="Output format",
    )
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def docstring(dotted_path, format, as_json):
        """
        Get docstring of a Python object

        \b
        Formats:
          raw     - Full docstring as-is
          parsed  - Parse into sections (summary, parameters, returns, etc.)
          summary - First line/paragraph only

        \b
        Examples:
          scitex introspect docstring scitex.plt.plot
          scitex introspect docstring scitex.audio.speak --format parsed
        """
        from scitex.introspect import get_docstring

        result = get_docstring(dotted_path, format=format)

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            click.echo(result["docstring"])
            if format == "parsed" and result.get("sections"):
                click.echo("\n--- Parsed Sections ---")
                for key, value in result["sections"].items():
                    if value:
                        click.secho(f"\n[{key}]", fg="cyan", bold=True)
                        click.echo(value)

    @group.command()
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def exports(dotted_path, as_json):
        """
        Get __all__ exports of a module

        \b
        Examples:
          scitex introspect exports scitex.audio
          scitex introspect exports scitex.plt
        """
        from scitex.introspect import get_exports

        result = get_exports(dotted_path)

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            has_all = "defined" if result["has_all"] else "not defined (showing public)"
            click.secho(f"__all__ is {has_all}", fg="cyan")
            click.secho(f"Exports ({result['count']}):", fg="cyan")
            for name in result["exports"]:
                click.echo(f"  {name}")

    @group.command()
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option("--search-paths", "-p", help="Comma-separated search paths")
    @click.option("--max-results", "-n", type=int, default=10, help="Max examples")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def examples(dotted_path, search_paths, max_results, as_json):
        """
        Find usage examples in tests/examples directories

        \b
        Examples:
          scitex introspect examples scitex.plt.plot
          scitex introspect examples scitex.audio.speak --max-results 5
        """
        from scitex.introspect import find_examples

        paths_list = None
        if search_paths:
            paths_list = [p.strip() for p in search_paths.split(",")]

        result = find_examples(
            dotted_path,
            search_paths=paths_list,
            max_results=max_results,
        )

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            click.secho(f"Found {result['count']} examples:", fg="cyan")
            for ex in result["examples"]:
                click.echo()
                click.secho(f"--- {ex['file']}:{ex['line']} ---", fg="yellow")
                click.echo(ex["context"])

    @group.command("hierarchy")
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option("--builtins", is_flag=True, help="Include builtin classes")
    @click.option("--max-depth", "-d", type=int, default=10, help="Max subclass depth")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def class_hierarchy(dotted_path, builtins, max_depth, as_json):
        """Get class inheritance hierarchy (MRO + subclasses)"""
        from scitex.introspect import get_class_hierarchy

        result = get_class_hierarchy(
            dotted_path, include_builtins=builtins, max_depth=max_depth
        )

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            click.secho(f"Class: {dotted_path}", fg="cyan", bold=True)
            click.secho(f"\nMRO ({result['mro_count']} classes):", fg="yellow")
            for cls in result["mro"]:
                click.echo(f"  {cls['qualname']}")
            click.secho(f"\nSubclasses ({result['subclass_count']}):", fg="yellow")
            _print_subclasses(result.get("subclasses", []), indent=2)

    @group.command("hints")
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def type_hints(dotted_path, as_json):
        """Get detailed type hint analysis"""
        from scitex.introspect import get_type_hints_detailed

        result = get_type_hints_detailed(dotted_path)

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            click.secho(f"Type hints ({result['hint_count']}):", fg="cyan")
            for name, info in result.get("hints", {}).items():
                opt = " (optional)" if info.get("is_optional") else ""
                click.echo(f"  {name}: {info['raw']}{opt}")
            if result.get("return_hint"):
                click.secho(f"\nReturn: {result['return_hint']['raw']}", fg="green")

    @group.command("imports")
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option("--no-categorize", is_flag=True, help="Don't group by category")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def imports(dotted_path, no_categorize, as_json):
        """Get all imports from a module (AST-based)"""
        from scitex.introspect import get_imports

        result = get_imports(dotted_path, categorize=not no_categorize)

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            click.secho(f"Imports ({result['import_count']}):", fg="cyan")
            if result.get("categories"):
                for cat, imps in result["categories"].items():
                    if imps:
                        click.secho(f"\n  [{cat}] ({len(imps)}):", fg="yellow")
                        for imp in imps:
                            click.echo(f"    {imp['module']}")
            else:
                for imp in result["imports"]:
                    click.echo(f"  {imp['module']}")

    @group.command("deps")
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option("--recursive", "-r", is_flag=True, help="Recursive analysis")
    @click.option("--max-depth", "-d", type=int, default=3, help="Max recursion depth")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def dependencies(dotted_path, recursive, max_depth, as_json):
        """Get module dependencies"""
        from scitex.introspect import get_dependencies

        result = get_dependencies(dotted_path, recursive=recursive, max_depth=max_depth)

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            click.secho(f"Dependencies ({result['dependency_count']}):", fg="cyan")
            for dep in result.get("dependencies", []):
                click.echo(f"  {dep}")

    @group.command("calls")
    @click.argument("dotted_path", callback=_normalize_path)
    @click.option("--timeout", "-t", type=int, default=10, help="Timeout in seconds")
    @click.option("--all", "all_calls", is_flag=True, help="Include external calls")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def call_graph(dotted_path, timeout, all_calls, as_json):
        """Get function call graph (with timeout protection)"""
        from scitex.introspect import get_call_graph

        result = get_call_graph(
            dotted_path, timeout_seconds=timeout, internal_only=not all_calls
        )

        if not result.get("success", False):
            if as_json:
                echo_json_error(result.get("error", "Unknown error"))
            click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
            sys.exit(1)

        if as_json:
            echo_json_result(result)
        else:
            if "calls" in result:
                click.secho(f"Calls ({result['call_count']}):", fg="cyan")
                for call in result["calls"]:
                    click.echo(f"  -> {call['name']} (line {call['line']})")
                click.secho(f"\nCalled by ({result['caller_count']}):", fg="yellow")
                for caller in result.get("called_by", []):
                    click.echo(f"  <- {caller['name']} (line {caller['line']})")
            elif "graph" in result:
                click.secho(
                    f"Module call graph ({result['function_count']} functions):",
                    fg="cyan",
                )
                for func, info in result["graph"].items():
                    calls = ", ".join(c["name"] for c in info["calls"][:5])
                    if len(info["calls"]) > 5:
                        calls += "..."
                    click.echo(f"  {func}: {calls or '(no calls)'}")
