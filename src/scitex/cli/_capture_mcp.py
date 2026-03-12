#!/usr/bin/env python3
"""
SciTeX CLI - Capture MCP Subcommands

MCP server operations for the capture module.
"""

import sys

import click


def register_mcp(capture_group):
    """Register the MCP subgroup onto the capture click group."""

    @capture_group.group(invoke_without_command=True)
    @click.option(
        "--json",
        "as_json",
        is_flag=True,
        help="Output as structured JSON (Result envelope).",
    )
    @click.pass_context
    def mcp(ctx, as_json):
        """MCP (Model Context Protocol) server operations for capture."""
        if ctx.invoked_subcommand is None:
            if as_json:
                from . import group_to_json

                group_to_json(ctx, mcp)
            else:
                click.echo(ctx.get_help())

    @mcp.command("start")
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
        "--port", default=8096, type=int, help="Port for HTTP/SSE (default: 8096)"
    )
    def mcp_start(transport, host, port):
        """
        Start the capture MCP server

        \b
        Examples:
          scitex capture mcp start
          scitex capture mcp start -t http --port 8096
        """
        try:
            from scitex.capture.mcp_server import main as run_server

            if transport != "stdio":
                click.secho(f"Starting capture MCP server ({transport})", fg="cyan")
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
          scitex capture mcp doctor
        """
        click.secho("Capture MCP Server Health Check", fg="cyan", bold=True)
        click.echo()

        click.echo("Checking FastMCP... ", nl=False)
        try:
            import fastmcp  # noqa: F401

            click.secho("OK", fg="green")
        except ImportError:
            click.secho("NOT INSTALLED", fg="red")
            click.echo("  Install with: pip install fastmcp")

        click.echo("Checking capture module... ", nl=False)
        try:
            from scitex import capture as _  # noqa: F401

            click.secho("OK", fg="green")
        except ImportError as e:
            click.secho(f"FAIL ({e})", fg="red")

    @mcp.command("list-tools")
    @click.option("-v", "--verbose", count=True, help="-v params, -vv returns")
    def list_tools(verbose):
        """List available MCP tools for capture."""
        click.secho("Capture MCP Tools", fg="cyan", bold=True)
        click.echo()
        # (name, desc, params, returns)
        tools = [
            (
                "capture_screenshot",
                "Capture screenshot",
                "output_path=None, monitor=0",
                "str",
            ),
            (
                "capture_window",
                "Capture specific window",
                "window_id: str, output=None",
                "str",
            ),
            (
                "start_monitoring",
                "Start continuous capture",
                "interval=5.0, monitor=0",
                "str",
            ),
            ("stop_monitoring", "Stop monitoring", "session_id=None", "str"),
            ("get_monitoring_status", "Get monitoring status", "", "JSON"),
            (
                "analyze_screenshot",
                "Analyze screenshot for errors",
                "image_path: str",
                "JSON",
            ),
            ("list_recent_screenshots", "List recent screenshots", "limit=10", "JSON"),
            ("clear_cache", "Clear screenshot cache", "older_than_hours=24", "JSON"),
            (
                "create_gif",
                "Create animated GIF",
                "session_id: str, output=None",
                "str",
            ),
            ("list_sessions", "List monitoring sessions", "", "JSON"),
            ("get_info", "Get monitor/window info", "", "JSON"),
            ("list_windows", "List visible windows", "", "JSON"),
        ]
        for name, desc, params, returns in tools:
            click.secho(f"  capture_{name}", fg="green", bold=True, nl=False)
            click.echo(f": {desc}")
            if verbose >= 1 and params:
                click.echo(f"    params: {params}")
            if verbose >= 2:
                click.echo(f"    returns: {returns}")
            if verbose >= 1:
                click.echo()

    return mcp
