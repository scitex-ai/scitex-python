#!/usr/bin/env python3
# Timestamp: 2026-02-02
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
    Examples:
      scitex dev versions              # List all ecosystem versions
      scitex dev versions --check      # Check version consistency
      scitex dev versions --json       # Output as JSON
      scitex dev versions -p scitex    # Check specific package
    """
    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, dev)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@dev.command("versions")
@click.option(
    "--check",
    is_flag=True,
    help="Check version consistency and show summary",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "-p",
    "--package",
    multiple=True,
    help="Filter to specific package(s)",
)
@click.option(
    "--local-only",
    is_flag=True,
    help="Skip remote (PyPI) version checks",
)
@click.option(
    "--host",
    multiple=True,
    help="Check specific SSH host(s)",
)
@click.option(
    "--all-hosts",
    is_flag=True,
    help="Check all configured SSH hosts",
)
@click.option(
    "--remote",
    multiple=True,
    help="Check specific GitHub remote(s)",
)
@click.option(
    "--all-remotes",
    is_flag=True,
    help="Check all configured GitHub remotes",
)
@click.option(
    "--rtd",
    is_flag=True,
    help="Check Read the Docs build status",
)
@click.option(
    "--all/--no-all",
    "check_all",
    default=True,
    help="Check all sources (hosts, remotes, RTD). Default: on.",
)
@click.option(
    "--dashboard",
    is_flag=True,
    help="Start the Flask version dashboard (GUI).",
)
@click.option(
    "--dashboard-port", default=5000, type=int, help="Dashboard port (default: 5000)."
)
@click.option(
    "--force", is_flag=True, help="Kill existing dashboard process using the port."
)
def versions(
    check,
    as_json,
    package,
    local_only,
    host,
    all_hosts,
    remote,
    all_remotes,
    rtd,
    check_all,
    dashboard,
    dashboard_port,
    force,
):
    r"""
    List versions across the scitex ecosystem.

    \b
    Shows version information from multiple sources:
      - pyproject.toml (local source)
      - installed package (pip/importlib.metadata)
      - git tag (latest version tag)
      - git branch (current branch)
      - PyPI (remote published version)
      - SSH hosts (--all-hosts or --all)
      - GitHub remotes (--all-remotes or --all)
      - Read the Docs (--rtd or --all)

    \b
    Examples:
      scitex dev versions                    # List all versions (incl. hosts, remotes, RTD)
      scitex dev versions --no-all           # Skip hosts, remotes, RTD
      scitex dev versions --check            # Check consistency
      scitex dev versions --json             # JSON output
      scitex dev versions -p scitex          # Single package
      scitex dev versions --host spartan     # Check specific host only
      scitex dev versions --dashboard        # Start version dashboard GUI
      scitex dev versions --dashboard --force  # Restart dashboard
    """
    if dashboard:
        from scitex._dev import run_dashboard

        run_dashboard(
            host="127.0.0.1",
            port=dashboard_port,
            debug=False,
            open_browser=True,
            force=force,
        )
        return

    import json as json_module

    from scitex._dev import check_versions, list_versions

    from ._dev_fmt import (
        print_check_result,
        print_hosts,
        print_remotes,
        print_rtd,
        print_versions,
    )

    packages = list(package) if package else None

    if check:
        result = check_versions(packages)
        if local_only:
            for pkg_info in result["packages"].values():
                pkg_info.get("remote", {}).pop("pypi", None)
    else:
        result = list_versions(packages)
        if local_only:
            for pkg_info in result.values():
                pkg_info.get("remote", {}).pop("pypi", None)

    if host or all_hosts or check_all:
        from scitex._dev import check_all_hosts

        hosts_filter = list(host) if host else None
        try:
            result["hosts"] = check_all_hosts(packages=packages, hosts=hosts_filter)
        except Exception as e:
            result["hosts"] = {"error": str(e)}

    if remote or all_remotes or check_all:
        from scitex._dev import check_all_remotes

        remotes_filter = list(remote) if remote else None
        try:
            result["remotes"] = check_all_remotes(
                packages=packages, remotes=remotes_filter
            )
        except Exception as e:
            result["remotes"] = {"error": str(e)}

    if rtd or check_all:
        try:
            from scitex._dev._rtd import check_all_rtd

            result["rtd"] = check_all_rtd(packages=packages, versions=["latest"])
        except Exception as e:
            result["rtd"] = {"error": str(e)}

    if as_json:
        click.echo(json_module.dumps(result, indent=2))
        return

    if check:
        print_check_result(result)
    else:
        print_versions(result)

    if "hosts" in result and result["hosts"]:
        print_hosts(result["hosts"])

    if "remotes" in result and result["remotes"]:
        print_remotes(result["remotes"])

    if "rtd" in result and result["rtd"]:
        print_rtd(result["rtd"])


# MCP subgroup
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
        ("dev_list_versions", "List versions across ecosystem", "packages", "JSON"),
        ("dev_check_versions", "Check version consistency", "packages", "JSON"),
        ("dev_check_hosts", "Check versions on SSH hosts", "packages, hosts", "JSON"),
        ("dev_check_remotes", "Check versions on GitHub", "packages, remotes", "JSON"),
        ("dev_get_config", "Get current configuration", "", "JSON"),
        (
            "dev_full_versions",
            "Get comprehensive data",
            "packages, hosts, remotes",
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


# Config subgroup
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
    from scitex._dev import get_config_path, load_config

    config_path = get_config_path()
    if not config_path.exists():
        click.secho(f"Config not found: {config_path}", fg="red")
        click.echo("Run 'scitex dev config create' to create one.")
        return

    try:
        cfg = load_config()
        click.secho("Configuration is valid.", fg="green")
        click.echo(f"  Packages: {len(cfg.packages)}")
        click.echo(f"  Hosts: {len(cfg.hosts)}")
        click.echo(f"  Remotes: {len(cfg.github_remotes)}")
    except Exception as e:
        click.secho(f"Configuration error: {e}", fg="red")


# Register commands from separate modules
from ._dev_clone import clone
from ._dev_rename import rename
from ._dev_test import test

dev.add_command(clone)
dev.add_command(rename)
dev.add_command(test)


# EOF
