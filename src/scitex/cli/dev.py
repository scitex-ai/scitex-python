#!/usr/bin/env python3
# Timestamp: 2026-02-24
# File: scitex/cli/dev.py

"""
SciTeX Developer CLI Commands (Internal).

Commands for managing and inspecting the scitex ecosystem.
"""

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.pass_context
def dev(ctx, help_recursive):
    r"""
    Developer utilities (internal).

    \b
    Subcommands:
      versions   - Version management (list, sync, dashboard)
      config     - Manage developer configuration
      test       - Run tests locally or on HPC
      rename     - Bulk rename across ecosystem
      clone      - Clone ecosystem repos

    \b
    Examples:
      scitex dev versions                    # List all versions
      scitex dev versions sync               # Preview sync (dry run)
      scitex dev versions sync --confirm     # Execute sync
      scitex dev versions dashboard          # Start dashboard GUI
      scitex dev config show                 # Show configuration
    """
    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, dev)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ---------------------------------------------------------------------------
# versions — group for version management
# ---------------------------------------------------------------------------


@dev.group("versions", invoke_without_command=True)
@click.pass_context
def versions(ctx):
    r"""
    Version management across the scitex ecosystem.

    \b
    Subcommands:
      list          - List local/PyPI versions
      list-hosts    - List versions on SSH hosts
      list-remotes  - List versions on GitHub remotes
      list-rtd      - List Read the Docs build status
      check         - Check version consistency
      sync          - Sync packages to hosts (safe: preview by default)
      dashboard     - Start version dashboard GUI

    \b
    Examples:
      scitex dev versions list               # Local + PyPI versions
      scitex dev versions list-hosts         # SSH host versions
      scitex dev versions list-remotes       # GitHub remote versions
      scitex dev versions check              # Consistency check
      scitex dev versions sync               # Preview sync (dry run)
      scitex dev versions sync --confirm     # Execute sync
      scitex dev versions dashboard          # Start dashboard
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@versions.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--local-only", is_flag=True, help="Skip remote (PyPI) version checks")
def versions_list(as_json, package, local_only):
    r"""
    List local and PyPI versions (read-only).

    \b
    Examples:
      scitex dev versions list               # All packages
      scitex dev versions list --json        # JSON output
      scitex dev versions list -p scitex     # Specific package
      scitex dev versions list --local-only  # Skip PyPI
    """
    import json as json_module

    from scitex._dev import list_versions

    from ._dev_fmt import print_versions

    packages = list(package) if package else None
    result = list_versions(packages)
    if local_only:
        for pkg_info in result.values():
            pkg_info.get("remote", {}).pop("pypi", None)

    if as_json:
        click.echo(json_module.dumps(result, indent=2))
        return

    print_versions(result)


@versions.command("list-hosts")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--host", multiple=True, help="Check specific host(s)")
def versions_list_hosts(as_json, package, host):
    r"""
    List versions on SSH hosts.

    \b
    Examples:
      scitex dev versions list-hosts             # All enabled hosts
      scitex dev versions list-hosts --host nas  # Specific host
      scitex dev versions list-hosts --json      # JSON output
    """
    import json as json_module

    from scitex._dev import check_all_hosts

    from ._dev_fmt import print_hosts

    packages = list(package) if package else None
    hosts_filter = list(host) if host else None
    try:
        result = check_all_hosts(packages=packages, hosts=hosts_filter)
    except Exception as e:
        result = {"error": str(e)}

    if as_json:
        click.echo(json_module.dumps(result, indent=2))
        return

    print_hosts(result)


@versions.command("list-remotes")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--remote", multiple=True, help="Check specific remote(s)")
def versions_list_remotes(as_json, package, remote):
    r"""
    List versions on GitHub remotes.

    \b
    Examples:
      scitex dev versions list-remotes       # All enabled remotes
      scitex dev versions list-remotes --json
    """
    import json as json_module

    from scitex._dev import check_all_remotes

    from ._dev_fmt import print_remotes

    packages = list(package) if package else None
    remotes_filter = list(remote) if remote else None
    try:
        result = check_all_remotes(packages=packages, remotes=remotes_filter)
    except Exception as e:
        result = {"error": str(e)}

    if as_json:
        click.echo(json_module.dumps(result, indent=2))
        return

    print_remotes(result)


@versions.command("list-rtd")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
def versions_list_rtd(as_json, package):
    r"""
    List Read the Docs build status.

    \b
    Examples:
      scitex dev versions list-rtd           # All packages
      scitex dev versions list-rtd --json
    """
    import json as json_module

    from ._dev_fmt import print_rtd

    packages = list(package) if package else None
    try:
        from scitex._dev._rtd import check_all_rtd

        result = check_all_rtd(packages=packages, versions=["latest"])
    except Exception as e:
        result = {"error": str(e)}

    if as_json:
        click.echo(json_module.dumps(result, indent=2))
        return

    print_rtd(result)


@versions.command("check")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--local-only", is_flag=True, help="Skip remote (PyPI) version checks")
def versions_check(as_json, package, local_only):
    r"""
    Check version consistency across ecosystem.

    \b
    Examples:
      scitex dev versions check              # Check all packages
      scitex dev versions check -p scitex    # Check specific package
      scitex dev versions check --json       # JSON output
    """
    import json as json_module

    from scitex._dev import check_versions

    from ._dev_fmt import print_check_result

    packages = list(package) if package else None
    result = check_versions(packages)
    if local_only:
        for pkg_info in result["packages"].values():
            pkg_info.get("remote", {}).pop("pypi", None)

    if as_json:
        click.echo(json_module.dumps(result, indent=2))
        return

    print_check_result(result)


# ---------------------------------------------------------------------------
# versions subcommands — registered from separate modules
# ---------------------------------------------------------------------------

from ._dev_sync import sync as _versions_sync

versions.add_command(_versions_sync)


@versions.command("dashboard")
@click.option("--port", default=5000, type=int, help="Dashboard port (default: 5000)")
@click.option("--force", is_flag=True, help="Kill existing process using the port")
def versions_dashboard(port, force):
    r"""
    Start the version dashboard GUI.

    \b
    Examples:
      scitex dev versions dashboard              # Start on port 5000
      scitex dev versions dashboard --port 5001  # Custom port
      scitex dev versions dashboard --force      # Restart (kill existing)
    """
    from scitex._dev import run_dashboard

    run_dashboard(
        host="127.0.0.1",
        port=port,
        debug=False,
        open_browser=True,
        force=force,
    )


# ---------------------------------------------------------------------------
# MCP subgroup
# ---------------------------------------------------------------------------


@dev.group(invoke_without_command=True)
@click.pass_context
def mcp(ctx):
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
    ]
    for name, desc, params, returns in tools:
        click.secho(f"  {name}", fg="green", bold=True, nl=False)
        click.echo(f": {desc}")
        if verbose >= 1 and params:
            click.echo(f"    params: {params}")
        if verbose >= 2 and returns:
            click.echo(f"    returns: {returns}")


@dev.command("list-python-apis")
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


# ---------------------------------------------------------------------------
# Config subgroup
# ---------------------------------------------------------------------------


@dev.group(invoke_without_command=True)
@click.pass_context
def config(ctx):
    r"""
    Manage configuration.

    \b
    Commands:
      show     - Show current configuration
      validate - Validate configuration file
      create   - Create default config file

    \b
    Examples:
      scitex dev config show
      scitex dev config create
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@config.command("show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def config_show(as_json):
    """Show current configuration."""
    import json as json_module

    from scitex._dev import get_config_path, load_config

    config_path = get_config_path()
    cfg = load_config()

    if as_json:
        data = {
            "config_path": str(config_path),
            "exists": config_path.exists(),
            "packages": [p.name for p in cfg.packages],
            "hosts": [{"name": h.name, "enabled": h.enabled} for h in cfg.hosts],
            "remotes": [
                {"name": r.name, "enabled": r.enabled} for r in cfg.github_remotes
            ],
            "branches": cfg.branches,
        }
        click.echo(json_module.dumps(data, indent=2))
        return

    click.secho("Configuration", fg="cyan", bold=True)
    click.echo(f"  Path: {config_path}")
    click.echo(f"  Exists: {config_path.exists()}")
    click.echo()
    click.secho("Packages:", fg="yellow")
    for p in cfg.packages:
        click.echo(f"  - {p.name} ({p.pypi_name})")
    click.echo()
    click.secho("Hosts:", fg="yellow")
    for h in cfg.hosts:
        status = "enabled" if h.enabled else "disabled"
        click.echo(f"  - {h.name} ({h.hostname}) [{status}]")
    click.echo()
    click.secho("GitHub Remotes:", fg="yellow")
    for r in cfg.github_remotes:
        status = "enabled" if r.enabled else "disabled"
        click.echo(f"  - {r.name} (org: {r.org}) [{status}]")


@config.command("create")
@click.option("--force", is_flag=True, help="Overwrite existing config")
def config_create(force):
    """Create default configuration file."""
    from scitex._dev import create_default_config, get_config_path

    config_path = get_config_path()
    if config_path.exists() and not force:
        click.secho(f"Config already exists: {config_path}", fg="yellow")
        click.echo("Use --force to overwrite.")
        return

    path = create_default_config()
    click.secho(f"Created config: {path}", fg="green")


@config.command("validate")
def config_validate():
    """Validate configuration file."""
    import sys

    from scitex._dev import get_config_path, load_config

    config_path = get_config_path()
    if not config_path.exists():
        click.secho(f"Config not found: {config_path}", fg="red")
        click.echo("Run 'scitex dev config create' to create one.")
        sys.exit(1)

    try:
        cfg = load_config()
        click.secho("Configuration is valid.", fg="green")
        click.echo(f"  Packages: {len(cfg.packages)}")
        click.echo(f"  Hosts: {len(cfg.hosts)}")
        click.echo(f"  Remotes: {len(cfg.github_remotes)}")
    except Exception as e:
        click.secho(f"Configuration error: {e}", fg="red")
        sys.exit(1)


# Register commands from separate modules
from ._dev_clone import clone
from ._dev_rename import rename
from ._dev_test import test

dev.add_command(clone)
dev.add_command(rename)
dev.add_command(test)


# EOF
