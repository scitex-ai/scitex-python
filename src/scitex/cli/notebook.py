#!/usr/bin/env python3
"""SciTeX CLI - Notebook commands for Jupyter verification and compilation."""

import sys

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.pass_context
def notebook(ctx, help_recursive):
    """
    Jupyter notebook verification and compilation tools.

    \b
    Commands:
      verify    Verify all clew sessions from a notebook
      compile   Reconstruct execution DAG from clew timestamps
      convert   Convert .ipynb to .py with @scitex.session
      check     Find cells with untracked IO

    \b
    Examples:
      scitex notebook verify experiment.ipynb
      scitex notebook compile experiment.ipynb
      scitex notebook convert experiment.ipynb -o script.py
      scitex notebook check experiment.ipynb
    """
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(notebook, info_name="notebook", parent=fake_parent)
    click.secho("--- scitex notebook ---", fg="cyan", bold=True)
    click.echo(notebook.get_help(parent_ctx))
    for name in sorted(notebook.list_commands(ctx) or []):
        cmd = notebook.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"--- scitex notebook {name} ---", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@notebook.command("verify")
@click.argument("path", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def verify_cmd(path, as_json):
    """
    Verify all clew sessions associated with a notebook.

    Finds sessions in the clew DB whose metadata references this notebook,
    then runs L1 (cache) verification on each.

    \b
    Examples:
      scitex notebook verify experiment.ipynb
      scitex notebook verify experiment.ipynb --json
    """
    try:
        from scitex.notebook import verify_notebook

        results = verify_notebook(path)

        if as_json:
            import json

            click.echo(json.dumps(results, indent=2))
        else:
            if not results:
                click.echo("No tracked sessions found for this notebook.")
                click.echo("Use @stx.session in cells and run them first.")
                return

            for r in results:
                status = r.get("status", "unknown")
                sid = r["session_id"]
                if r.get("is_verified"):
                    click.secho(f"  V {sid}", fg="green")
                else:
                    click.secho(f"  X {sid} ({status})", fg="red")

            verified = sum(1 for r in results if r.get("is_verified"))
            click.echo(f"\n{verified}/{len(results)} sessions verified")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notebook.command("compile")
@click.argument("path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output .py file")
@click.option("--mermaid", is_flag=True, help="Output Mermaid DAG diagram")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def compile_cmd(path, output, mermaid, as_json):
    """
    Reconstruct execution DAG from clew DB timestamps.

    Queries the clew database for all sessions run from this notebook,
    builds a dependency DAG from IO relationships, and outputs the
    result as a DAG-ordered .py script or Mermaid diagram.

    \b
    Examples:
      scitex notebook compile experiment.ipynb
      scitex notebook compile experiment.ipynb --mermaid
      scitex notebook compile experiment.ipynb -o pipeline.py
    """
    try:
        from scitex.notebook import compile_notebook

        compiled = compile_notebook(path)

        if not compiled.execution_order:
            click.echo("No execution history found for this notebook.")
            click.echo("Run cells with @stx.session first.")
            return

        if as_json:
            import json

            click.echo(
                json.dumps(
                    {
                        "notebook_path": compiled.notebook_path,
                        "execution_order": compiled.execution_order,
                        "dag": compiled.dag,
                    },
                    indent=2,
                )
            )
        elif mermaid:
            click.echo(compiled.to_mermaid())
        elif output:
            from pathlib import Path

            script = compiled.to_script()
            Path(output).write_text(script, encoding="utf-8")
            click.secho(f"Compiled to: {output}", fg="green")
        else:
            click.secho("Execution DAG", fg="cyan", bold=True)
            click.echo(compiled.to_mermaid())
            n = len(compiled.execution_order)
            edges = sum(len(v) for v in compiled.dag.values())
            click.echo(f"\n{n} sessions, {edges} dependencies")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notebook.command("convert")
@click.argument("path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output .py file")
@click.option(
    "--order",
    type=click.Choice(["cell", "dag"]),
    default="cell",
    help="Cell ordering: cell (notebook order) or dag (execution order)",
)
def convert_cmd(path, output, order):
    """
    Convert .ipynb to .py with @scitex.session wrappers.

    Each code cell becomes a function decorated with @stx.session.
    Use --order=dag to reorder cells by actual execution order
    (requires prior execution with clew tracking).

    \b
    Examples:
      scitex notebook convert experiment.ipynb
      scitex notebook convert experiment.ipynb -o script.py
      scitex notebook convert experiment.ipynb --order dag -o pipeline.py
    """
    try:
        from scitex.notebook import convert_notebook

        if output is None:
            from pathlib import Path

            output = str(Path(path).with_suffix(".py"))

        script = convert_notebook(path, output=output, order=order)
        click.secho(f"Converted to: {output}", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notebook.command("check")
@click.argument("path", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def check_cmd(path, as_json):
    """
    Find cells with scitex.io calls not wrapped in @scitex.session.

    Scans notebook code cells for scitex.io.load/save calls that are
    not inside an @scitex.session decorated function. These represent
    untracked IO that breaks the verification chain.

    \b
    Examples:
      scitex notebook check experiment.ipynb
      scitex notebook check experiment.ipynb --json
    """
    try:
        from scitex.notebook import check_notebook

        issues = check_notebook(path)

        if as_json:
            import json

            click.echo(json.dumps(issues, indent=2))
        else:
            if not issues:
                click.secho("All IO cells are tracked.", fg="green")
                return

            click.secho("Untracked IO found:", fg="yellow", bold=True)
            for issue in issues:
                idx = issue["index"]
                ops = []
                if issue["has_load"]:
                    ops.append("load")
                if issue["has_save"]:
                    ops.append("save")
                click.echo(f"  Cell {idx}: {', '.join(ops)}")

            click.echo(f"\n{len(issues)} cell(s) with untracked IO")
            click.echo("Wrap these cells with @stx.session to enable tracking.")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    notebook()
