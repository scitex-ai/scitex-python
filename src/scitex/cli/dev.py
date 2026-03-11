#!/usr/bin/env python3
# Timestamp: 2026-03-11
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
    """Developer utilities (internal).

    \b
    Subcommands:
      versions   - Version management (list, sync, dashboard)
      config     - Manage developer configuration
      fix        - Detect and fix version mismatches
      test       - Run tests locally or on HPC
      rename     - Bulk rename across ecosystem
      clone      - Clone ecosystem repos
      mcp        - MCP server operations

    \b
    Examples:
      scitex dev versions                    # List all versions
      scitex dev versions sync               # Preview sync (dry run)
      scitex dev versions sync --confirm     # Execute sync
      scitex dev versions sync-local         # Preview local installs
      scitex dev versions dashboard          # Start dashboard GUI
      scitex dev fix                         # Preview mismatch fixes
      scitex dev fix --confirm               # Execute mismatch fixes
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
    """Version management across the scitex ecosystem.

    \b
    Subcommands:
      list          - List local/PyPI versions
      list-hosts    - List versions on SSH hosts
      list-remotes  - List versions on GitHub remotes
      list-rtd      - List Read the Docs build status
      check         - Check version consistency
      sync          - Sync packages to hosts (safe: preview by default)
      sync-local    - Install local editable packages
      dashboard     - Start version dashboard GUI

    \b
    Examples:
      scitex dev versions list               # Local + PyPI versions
      scitex dev versions list-hosts         # SSH host versions
      scitex dev versions list-remotes       # GitHub remote versions
      scitex dev versions check              # Consistency check
      scitex dev versions sync               # Preview sync (dry run)
      scitex dev versions sync --confirm     # Execute sync
      scitex dev versions sync-local         # Preview local installs
      scitex dev versions sync-local --confirm  # Execute local installs
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


@versions.command("dashboard")
@click.option("--port", default=5000, type=int, help="Dashboard port (default: 5000)")
@click.option("--force", is_flag=True, help="Kill existing process using the port")
@click.option("--no-browser", is_flag=True, help="Don't open browser window")
@click.option(
    "--background", is_flag=True, help="Run as background daemon (implies --no-browser)"
)
@click.option("--stop", is_flag=True, help="Stop a running background dashboard")
def versions_dashboard(port, force, no_browser, background, stop):
    r"""
    Start the version dashboard GUI.

    \b
    Examples:
      scitex dev versions dashboard                    # Start on port 5000
      scitex dev versions dashboard --port 5001        # Custom port
      scitex dev versions dashboard --force            # Restart (kill existing)
      scitex dev versions dashboard --no-browser       # Don't open browser
      scitex dev versions dashboard --background       # Run as background daemon
      scitex dev versions dashboard --stop             # Stop background daemon
    """
    if stop:
        from scitex._dev._dashboard._app import stop_dashboard

        stop_dashboard()
        return

    if background:
        from scitex._dev._dashboard._app import run_background

        run_background(host="127.0.0.1", port=port, force=force)
        return

    from scitex._dev import run_dashboard

    run_dashboard(
        host="127.0.0.1",
        port=port,
        debug=False,
        open_browser=not no_browser,
        force=force,
    )


# ---------------------------------------------------------------------------
# versions subcommands — registered from separate modules
# ---------------------------------------------------------------------------

from ._dev_sync import sync as _versions_sync
from ._dev_sync import sync_local_cmd as _versions_sync_local
from ._dev_sync_remote import commit as _versions_commit
from ._dev_sync_remote import diff as _versions_diff
from ._dev_sync_remote import pull as _versions_pull

versions.add_command(_versions_sync)
versions.add_command(_versions_sync_local)
versions.add_command(_versions_diff)
versions.add_command(_versions_commit)
versions.add_command(_versions_pull)

# ---------------------------------------------------------------------------
# Subgroups and commands — registered from separate modules
# ---------------------------------------------------------------------------

from ._dev_clone import clone
from ._dev_config_cli import config
from ._dev_fix_cli import fix
from ._dev_mcp_cli import list_python_apis, mcp
from ._dev_rename import rename
from ._dev_test import test

dev.add_command(clone)
dev.add_command(config)
dev.add_command(fix)
dev.add_command(mcp)
dev.add_command(list_python_apis)
dev.add_command(rename)
dev.add_command(test)


# EOF
