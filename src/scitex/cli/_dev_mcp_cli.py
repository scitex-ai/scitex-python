#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: scitex/cli/_dev_mcp_cli.py

"""CLI subcommand group: scitex dev mcp (and list-python-apis)."""

import click


@click.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def mcp(ctx, as_json):
    r"""
    MCP (Model Context Protocol) server operations.

    \b
    Commands:
      list-tools - List available MCP tools

    \b
    Examples:
      scitex dev mcp list-tools
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, mcp)
        else:
            click.echo(ctx.get_help())


@mcp.command("list-tools")
@click.option("-v", "--verbose", count=True, help="-v params, -vv returns")
def list_tools(verbose):
    """List available MCP tools for dev module."""
    click.secho("Dev MCP Tools", fg="cyan", bold=True)
    click.echo()
    tools = [
        ("dev_versions_list", "List versions across ecosystem", "packages", "JSON"),
        (
            "dev_versions_sync",
            "Sync to remote hosts (confirm=True to execute)",
            "hosts, packages, confirm",
            "JSON",
        ),
        (
            "dev_versions_sync_local",
            "Install local packages (confirm=True to execute)",
            "packages, confirm",
            "JSON",
        ),
        ("dev_config_show", "Get current configuration", "", "JSON"),
        (
            "dev_bulk_rename",
            "Bulk rename (confirm=True to execute)",
            "pattern, replacement, confirm",
            "JSON",
        ),
        ("dev_test_local", "Run tests locally", "module, fast, pattern", "JSON"),
        ("dev_test_hpc", "Run tests on HPC", "module, fast, async_mode", "JSON"),
        ("dev_test_hpc_poll", "Check HPC job status", "job_id", "JSON"),
        ("dev_test_hpc_result", "Fetch HPC test output", "job_id", "JSON"),
        (
            "dev_fix_mismatches",
            "Detect and fix version mismatches (confirm=True to execute)",
            "hosts, packages, local, remote, confirm",
            "JSON",
        ),
    ]
    for name, desc, params, returns in tools:
        click.secho(f"  {name}", fg="green", bold=True, nl=False)
        click.echo(f": {desc}")
        if verbose >= 1 and params:
            click.echo(f"    params: {params}")
        if verbose >= 2 and returns:
            click.echo(f"    returns: {returns}")


@click.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List Python APIs (alias for: scitex introspect api scitex._dev)."""
    from scitex.cli.introspect import api

    ctx.invoke(
        api,
        dotted_path="scitex._dev",
        verbose=verbose,
        max_depth=max_depth,
        as_json=as_json,
    )


# EOF
