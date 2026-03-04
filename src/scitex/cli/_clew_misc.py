#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/cli/_clew_misc.py
"""Miscellaneous clew CLI commands: render, status, stats, clear, mcp, apis."""

import sys
from pathlib import Path

import click


def register_misc_commands(clew_group):
    """Register misc commands on the clew CLI group."""

    @clew_group.command("render")
    @click.argument("output_path", type=click.Path())
    @click.option("--session", "-s", help="Session ID to visualize")
    @click.option(
        "--file",
        "-f",
        "target_files",
        multiple=True,
        help="Target file(s) to trace (repeatable)",
    )
    @click.option("--claims", is_flag=True, help="Render DAG for all claims")
    @click.option("--title", "-t", default="Verification DAG", help="Title for output")
    def render_cmd(output_path, session, target_files, claims, title):
        """
        Render verification DAG to file (HTML, PNG, SVG, or Mermaid).

        The output format is determined by the file extension:
        - .html: Interactive HTML with Mermaid.js
        - .png: PNG image
        - .svg: SVG image
        - .mmd: Raw Mermaid code

        \b
        Examples:
          scitex clew render dag.html --file ./results/fig.png
          scitex clew render dag.html -f fig1.png -f fig2.png
          scitex clew render dag.png --session 2025Y-11M-18D-09h12m03s
          scitex clew render dag.html --claims
        """
        try:
            if not session and not target_files and not claims:
                click.secho(
                    "Error: Specify --session, --file, or --claims",
                    fg="red",
                    err=True,
                )
                sys.exit(1)

            from scitex.clew import render_dag

            target_file = None
            multi_targets = None
            if len(target_files) == 1:
                target_file = str(Path(target_files[0]).resolve())
            elif len(target_files) > 1:
                multi_targets = [str(Path(f).resolve()) for f in target_files]

            result_path = render_dag(
                output_path=output_path,
                session_id=session,
                target_file=target_file,
                target_files=multi_targets,
                claims=claims,
                title=title,
            )
            click.secho(f"Rendered to: {result_path}", fg="green")

        except Exception as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            sys.exit(1)

    @clew_group.command("status")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def status_cmd(as_json):
        """
        Show verification status (like git status).

        Displays a summary of all tracked runs and highlights any
        that have changed files (hash mismatches) or missing files.

        \b
        Examples:
          scitex clew status
          scitex clew status --json
        """
        try:
            from scitex.clew import format_status, get_status

            status = get_status()

            if as_json:
                import json

                click.echo(json.dumps(status, indent=2))
            else:
                output = format_status(status)
                click.echo(output)

        except Exception as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            sys.exit(1)

    @clew_group.command("stats")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def stats_cmd(as_json):
        """
        Show database statistics.

        \b
        Examples:
          scitex clew stats
          scitex clew stats --json
        """
        try:
            from scitex.clew import get_db

            db = get_db()
            db_stats = db.stats()

            if as_json:
                import json

                click.echo(json.dumps(db_stats, indent=2))
            else:
                click.secho("Verification Database Statistics", fg="cyan", bold=True)
                click.echo("=" * 40)
                click.echo(f"Database path:        {db_stats['db_path']}")
                click.echo(f"Total runs:           {db_stats['total_runs']}")
                click.echo(f"  Successful:         {db_stats['success_runs']}")
                click.echo(f"  Failed:             {db_stats['failed_runs']}")
                click.echo(f"Total file records:   {db_stats['total_file_records']}")
                click.echo(f"Unique files tracked: {db_stats['unique_files']}")

        except Exception as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            sys.exit(1)

    @clew_group.command("clear")
    @click.option("--force", "-f", is_flag=True, help="Skip confirmation")
    def clear_cmd(force):
        """
        Clear the verification database.

        \b
        Examples:
          scitex clew clear
          scitex clew clear -f
        """
        try:
            from scitex.clew import get_db

            db = get_db()
            db_stats = db.stats()

            if not force:
                click.echo(f"This will delete {db_stats['total_runs']} runs and ")
                click.echo(f"{db_stats['total_file_records']} file records.")
                if not click.confirm("Are you sure?"):
                    click.echo("Cancelled.")
                    return

            db_path = Path(db_stats["db_path"])
            if db_path.exists():
                db_path.unlink()
                click.secho("Database cleared.", fg="green")
            else:
                click.echo("Database already empty.")

        except Exception as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            sys.exit(1)

    @clew_group.group("mcp", invoke_without_command=True)
    @click.pass_context
    def mcp_group(ctx):
        """
        MCP (Model Context Protocol) server operations.

        \b
        Commands:
          list-tools - List available MCP tools

        \b
        Examples:
          scitex clew mcp list-tools
        """
        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    @mcp_group.command("list-tools")
    @click.option("-v", "--verbose", count=True, help="-v params, -vv returns")
    def list_tools(verbose):
        """List available MCP tools for verification."""
        click.secho("Clew MCP Tools", fg="cyan", bold=True)
        click.echo()
        collected = []

        class _MockMCP:
            def tool(self):
                def decorator(fn):
                    import inspect

                    sig = inspect.signature(fn)
                    params = [p for p in sig.parameters if p not in ("self", "cls")]
                    doc = (
                        (fn.__doc__ or "").strip().split("\n")[0].replace("[clew] ", "")
                    )
                    collected.append((fn.__name__, doc, params))
                    return fn

                return decorator

        from scitex._mcp_tools.clew import register_clew_tools

        register_clew_tools(_MockMCP())

        for name, desc, params in collected:
            click.secho(f"  {name}", fg="green", bold=True, nl=False)
            click.echo(f": {desc}")
            if verbose >= 1 and params:
                click.echo(f"    params: {', '.join(params)}")
            if verbose >= 1:
                click.echo()

    @clew_group.command("list-python-apis")
    @click.option(
        "-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc"
    )
    @click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    @click.pass_context
    def list_python_apis(ctx, verbose, max_depth, as_json):
        """List Python APIs (alias for: scitex introspect api scitex.clew)."""
        from scitex.cli.introspect import api

        ctx.invoke(
            api,
            dotted_path="scitex.clew",
            verbose=verbose,
            max_depth=max_depth,
            as_json=as_json,
        )
