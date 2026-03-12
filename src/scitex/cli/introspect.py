#!/usr/bin/env python3
"""
SciTeX CLI - Introspection Commands

Provides IPython-like introspection for Python packages.
"""

import sys

import click

from ._introspect_helpers import echo_json_error, echo_json_result


def _normalize_path(ctx, param, value):
    """Normalize dotted path: convert hyphens to underscores for Python module names."""
    if value:
        return value.replace("-", "_")
    return value


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def introspect(ctx, help_recursive, as_json):
    """
    Python package introspection utilities

    \b
    IPython-like introspection for any Python package:
      q         - Function/class signature (like func?)
      qq        - Full source code (like func??)
      dir       - List module/class members (like dir())
      api       - Full module API tree
      docstring - Extract docstrings
      exports   - Show __all__ exports
      examples  - Find usage examples

    \b
    Examples:
      scitex introspect q scitex.plt.plot
      scitex introspect qq scitex.stats.run_test --max-lines 50
      scitex introspect dir scitex.plt --kind functions
      scitex introspect api scitex --max-depth 2
    """
    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, introspect)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, introspect)
        else:
            click.echo(ctx.get_help())


@introspect.command()
@click.argument("dotted_path", callback=_normalize_path)
@click.option("--no-defaults", is_flag=True, help="Exclude default values")
@click.option("--no-annotations", is_flag=True, help="Exclude type annotations")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def q(dotted_path, no_defaults, no_annotations, as_json):
    """
    Get function/class signature (like IPython's func?)

    \b
    Examples:
      scitex introspect q scitex.plt.plot
      scitex introspect q scitex.audio.speak --json
      scitex introspect q json.dumps
    """
    from scitex.introspect import q as get_q

    result = get_q(
        dotted_path,
        include_defaults=not no_defaults,
        include_annotations=not no_annotations,
    )

    if not result.get("success", False):
        if as_json:
            echo_json_error(result.get("error", "Unknown error"))
        click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
        sys.exit(1)

    if as_json:
        echo_json_result(result)
    else:
        click.secho(result["signature"], fg="green", bold=True)
        if result.get("parameters"):
            click.echo("\nParameters:")
            for p in result["parameters"]:
                line = f"  {p['name']}"
                if "annotation" in p:
                    line += f": {p['annotation']}"
                if "default" in p:
                    line += f" = {p['default']}"
                click.echo(line)


@introspect.command()
@click.argument("dotted_path", callback=_normalize_path)
@click.option("--max-lines", "-n", type=int, help="Limit output to N lines")
@click.option("--no-decorators", is_flag=True, help="Exclude decorator lines")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def qq(dotted_path, max_lines, no_decorators, as_json):
    """
    Get source code of a Python object (like IPython's func??)

    \b
    Examples:
      scitex introspect qq scitex.plt.plot
      scitex introspect qq scitex.audio.speak --max-lines 50
    """
    from scitex.introspect import qq as get_qq

    result = get_qq(
        dotted_path,
        max_lines=max_lines,
        include_decorators=not no_decorators,
    )

    if not result.get("success", False):
        if as_json:
            echo_json_error(result.get("error", "Unknown error"))
        click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
        sys.exit(1)

    if as_json:
        echo_json_result(result)
    else:
        click.secho(f"# File: {result['file']}:{result['line_start']}", fg="cyan")
        click.secho(f"# Lines: {result['line_count']}", fg="cyan")
        click.echo()
        click.echo(result["source"])


@introspect.command("dir")
@click.argument("dotted_path", callback=_normalize_path)
@click.option(
    "--filter",
    "-f",
    type=click.Choice(["all", "public", "private", "dunder"]),
    default="public",
    help="Filter members",
)
@click.option(
    "--kind",
    "-k",
    type=click.Choice(["all", "functions", "classes", "data", "modules"]),
    help="Filter by type",
)
@click.option("--inherited", is_flag=True, help="Include inherited members (classes)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dir_cmd(dotted_path, filter, kind, inherited, as_json):
    """
    List members of a module or class (like dir())

    \b
    Examples:
      scitex introspect dir scitex.plt
      scitex introspect dir scitex.audio --kind functions
      scitex introspect dir scitex.plt.AxisWrapper --filter all
    """
    from scitex.introspect import dir as get_dir

    result = get_dir(
        dotted_path,
        filter=filter,
        kind=kind,
        include_inherited=inherited,
    )

    if not result.get("success", False):
        if as_json:
            echo_json_error(result.get("error", "Unknown error"))
        click.secho(f"Error: {result.get('error', 'Unknown error')}", fg="red")
        sys.exit(1)

    if as_json:
        echo_json_result(result)
    else:
        click.secho(f"Members of {dotted_path} ({result['count']}):", fg="cyan")
        for m in result["members"]:
            kind_str = click.style(f"[{m['kind']}]", fg="yellow")
            name_str = click.style(m["name"], fg="green", bold=True)
            summary = f" - {m['summary']}" if m["summary"] else ""
            click.echo(f"  {kind_str} {name_str}{summary}")


@introspect.command()
@click.argument("dotted_path", callback=_normalize_path)
@click.option("--max-depth", "-d", type=int, default=5, help="Max recursion depth")
@click.option("--root-only", is_flag=True, help="Show only root-level items")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def api(dotted_path, max_depth, root_only, verbose, as_json):
    """List API tree with types and signatures. -v adds docstrings, -vv full docs."""
    import importlib

    from scitex.introspect import list_api

    df = list_api(
        dotted_path, max_depth=max_depth, docstring=(verbose >= 1), root_only=root_only
    )

    # Color mapping for types
    type_colors = {"M": "blue", "C": "magenta", "F": "green", "V": "cyan"}

    if as_json:
        echo_json_result(df.to_dict(orient="records"))
    else:
        from . import format_python_signature

        click.secho(f"API tree of {dotted_path} ({len(df)} items):", fg="cyan")
        legend = " ".join(
            click.style(f"[{t}]={n}", fg=type_colors[t])
            for t, n in [
                ("M", "Module"),
                ("C", "Class"),
                ("F", "Function"),
                ("V", "Variable"),
            ]
        )
        click.echo(f"Legend: {legend}")
        # Get base module for signature lookup
        base_parts = dotted_path.split(".")
        for _, row in df.iterrows():
            indent = "  " * row["Depth"]
            t = row["Type"]
            type_s = click.style(f"[{t}]", fg=type_colors.get(t, "yellow"))
            name = row["Name"].split(".")[-1]

            if t == "F":
                try:
                    rel_parts = row["Name"].split(".")[:-1]
                    full_mod = (
                        ".".join(base_parts[:-1] + rel_parts)
                        if len(base_parts) > 1
                        else ".".join(rel_parts)
                    )
                    fn = getattr(importlib.import_module(full_mod), name, None)
                    if fn and callable(fn):
                        name_s, sig_s = format_python_signature(fn, indent=indent)
                        click.echo(f"{indent}{type_s} {name_s}{sig_s}")
                    else:
                        name_s = click.style(name, fg="green", bold=True)
                        click.echo(f"{indent}{type_s} {name_s}")
                except Exception:
                    name_s = click.style(name, fg="green", bold=True)
                    click.echo(f"{indent}{type_s} {name_s}")
            else:
                name_s = click.style(name, fg=type_colors.get(t, "white"), bold=True)
                click.echo(f"{indent}{type_s} {name_s}")

            if verbose >= 1 and row.get("Docstring"):
                if verbose == 1:
                    doc = row["Docstring"].split("\n")[0][:60]
                    click.echo(f"{indent}    - {doc}")
                else:
                    for ln in row["Docstring"].split("\n"):
                        click.echo(f"{indent}    {ln}")


# Wire in advanced sub-module commands
from scitex.cli._introspect_advanced import register_advanced_commands

register_advanced_commands(introspect)
