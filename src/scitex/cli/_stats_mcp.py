#!/usr/bin/env python3
"""Stats MCP CLI subcommands extracted from stats.py."""

import sys

import click


def register_mcp_commands(stats_group):
    """Register MCP subgroup on the stats CLI group."""

    @stats_group.group(invoke_without_command=True)
    @click.option(
        "--json",
        "as_json",
        is_flag=True,
        help="Output as structured JSON (Result envelope).",
    )
    @click.pass_context
    def mcp(ctx, as_json):
        """
        MCP (Model Context Protocol) server operations

        \b
        Commands:
          start      - Start the MCP server
          doctor     - Check MCP server health
          list-tools - List available MCP tools

        \b
        Examples:
          scitex stats mcp start
          scitex stats mcp list-tools
        """
        if ctx.invoked_subcommand is None:
            if as_json:
                from scitex.cli import group_to_json

                group_to_json(ctx, mcp)
            else:
                click.echo(ctx.get_help())

    @mcp.command()
    @click.option(
        "-t",
        "--transport",
        type=click.Choice(["stdio", "sse", "http"]),
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    @click.option(
        "--host", default="0.0.0.0", help="Host for HTTP/SSE (default: 0.0.0.0)"
    )
    @click.option(
        "--port", default=8095, type=int, help="Port for HTTP/SSE (default: 8095)"
    )
    def start(transport, host, port):
        """
        Start the stats MCP server

        \b
        Examples:
          scitex stats mcp start
          scitex stats mcp start -t http --port 8095
        """
        try:
            from scitex.stats.mcp_server import main as run_server

            if transport != "stdio":
                click.secho(f"Starting stats MCP server ({transport})", fg="cyan")
                click.echo(f"  Host: {host}")
                click.echo(f"  Port: {port}")

            run_server()

        except ImportError as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            click.echo("\nInstall dependencies: pip install fastmcp")
            sys.exit(1)
        except Exception as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            sys.exit(1)

    @mcp.command()
    def doctor():
        """
        Check MCP server health and dependencies

        \b
        Example:
          scitex stats mcp doctor
        """
        click.secho("Stats MCP Server Health Check", fg="cyan", bold=True)
        click.echo()

        click.echo("Checking FastMCP... ", nl=False)
        try:
            import fastmcp  # noqa: F401

            click.secho("OK", fg="green")
        except ImportError:
            click.secho("NOT INSTALLED", fg="red")
            click.echo("  Install with: pip install fastmcp")

        click.echo("Checking stats module... ", nl=False)
        try:
            from scitex import stats as _  # noqa: F401

            click.secho("OK", fg="green")
        except ImportError as e:
            click.secho(f"FAIL ({e})", fg="red")

    @mcp.command("list-tools")
    @click.option("-v", "--verbose", count=True, help="-v params, -vv returns")
    def list_tools(verbose):
        """List available MCP tools for statistics."""
        click.secho("Stats MCP Tools", fg="cyan", bold=True)
        click.echo()
        # (name, desc, params, returns)
        tools = [
            (
                "recommend_tests",
                "Recommend statistical tests",
                "data_description: str",
                "JSON",
            ),
            (
                "run_test",
                "Execute a statistical test",
                "test_name: str, data: list",
                "JSON",
            ),
            (
                "format_results",
                "Format results in journal style",
                "results: dict",
                "str",
            ),
            (
                "power_analysis",
                "Calculate power or sample size",
                "test: str, effect=0.5",
                "JSON",
            ),
            (
                "correct_pvalues",
                "Apply multiple comparison correction",
                "pvalues: list",
                "JSON",
            ),
            ("describe", "Calculate descriptive statistics", "data: list", "JSON"),
            (
                "effect_size",
                "Calculate effect size",
                "group1: list, group2: list",
                "JSON",
            ),
            ("normality_test", "Test for normal distribution", "data: list", "JSON"),
            (
                "posthoc_test",
                "Run post-hoc pairwise comparisons",
                "groups: list",
                "JSON",
            ),
            (
                "p_to_stars",
                "Convert p-value to significance stars",
                "p_value: float",
                "str",
            ),
        ]
        for name, desc, params, returns in tools:
            click.secho(f"  stats_{name}", fg="green", bold=True, nl=False)
            click.echo(f": {desc}")
            if verbose >= 1 and params:
                click.echo(f"    params: {params}")
            if verbose >= 2:
                click.echo(f"    returns: {returns}")
            if verbose >= 1:
                click.echo()
