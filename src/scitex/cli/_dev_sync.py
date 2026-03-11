#!/usr/bin/env python3
# Timestamp: 2026-02-24
# File: scitex/cli/_dev_sync.py

"""CLI subcommand: scitex dev versions sync."""

import click


def _print_local_results(local_results, mode):
    """Print local sync results in human-readable format."""
    has_error = False
    click.secho(f"Local packages [{mode}]", fg="cyan", bold=True)
    for pkg, info in local_results.items():
        status = info.get("status", "unknown")
        if status == "ok":
            click.secho(f"  {pkg}: ok", fg="green")
        elif status == "dry_run":
            cmds = info.get("commands", [])
            click.secho(f"  {pkg}: " + " ".join(cmds), fg="yellow")
        elif status == "skipped":
            click.secho(f"  {pkg}: {info.get('error', 'skipped')}", fg="yellow")
        else:
            click.secho(f"  {pkg}: {info.get('error', status)}", fg="red")
            has_error = True
    return has_error


def _print_remote_results(remote_results, mode):
    """Print remote sync results in human-readable format."""
    has_error = False
    click.secho(f"Remote hosts [{mode}]", fg="cyan", bold=True)
    if not remote_results:
        click.secho("  No enabled hosts found.", fg="yellow")
    for host_name, pkgs in remote_results.items():
        click.secho(f"\n  {host_name}:", fg="cyan", bold=True)
        for pkg, info in pkgs.items():
            status = info.get("status", "unknown")
            if status == "ok":
                click.secho(f"    {pkg}: ok", fg="green")
            elif status == "dry_run":
                cmds = info.get("commands", [])
                click.secho(f"    {pkg}: " + " && ".join(cmds), fg="yellow")
            else:
                click.secho(f"    {pkg}: {info.get('error', status)}", fg="red")
                has_error = True
    return has_error


def _print_tag_results(tag_results, mode):
    """Print tag push results in human-readable format."""
    has_error = False
    click.secho(f"Tag push [{mode}]", fg="cyan", bold=True)
    for pkg, info in tag_results.items():
        status = info.get("status", "unknown")
        tag = info.get("tag", "?")
        if status == "ok":
            click.secho(f"  {pkg} ({tag}): ok", fg="green")
        elif status == "dry_run":
            click.secho(
                f"  {pkg} ({tag}): " + " ".join(info.get("commands", [])),
                fg="yellow",
            )
        elif status == "skipped":
            click.secho(f"  {pkg}: {info.get('error', 'skipped')}", fg="yellow")
        else:
            click.secho(f"  {pkg}: {info.get('error', status)}", fg="red")
            has_error = True
    return has_error


@click.command("sync")
@click.option("--host", multiple=True, help="Sync specific host(s)")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--local", is_flag=True, help="Install local editable packages")
@click.option("--tags", is_flag=True, help="Push local tags to origin")
@click.option("--no-install", is_flag=True, help="Git pull only, skip pip install")
@click.option("--confirm", is_flag=True, help="Execute (default is preview/dry-run)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def sync(host, package, local, tags, no_install, confirm, as_json):
    r"""
    Sync ecosystem packages (safe: preview by default).

    \b
    Without --confirm, shows what would be done (dry run).
    With --confirm, executes sync in parallel across hosts.

    \b
    Operations:
      (default)   Sync to remote hosts (git stash, pull, install)
      --local     Install local editable packages (pip install -e)
      --tags      Push local tags to origin (git push --tags)

    \b
    Examples:
      scitex dev versions sync                        # Preview remote sync
      scitex dev versions sync --confirm              # Execute remote sync
      scitex dev versions sync --confirm --host nas   # Sync specific host
      scitex dev versions sync --confirm -p scitex    # Sync specific package
      scitex dev versions sync --local                # Preview local install
      scitex dev versions sync --local --confirm      # Execute local install
      scitex dev versions sync --tags                 # Preview tag push
      scitex dev versions sync --tags --confirm       # Execute tag push
    """
    import json as json_mod
    import sys

    from scitex._dev._sync import sync_all as _sync_all
    from scitex._dev._sync import sync_local as _sync_local
    from scitex._dev._sync import sync_tags as _sync_tags

    packages_list = list(package) if package else None
    hosts_list = list(host) if host else None
    has_error = False
    mode = "EXECUTE" if confirm else "PREVIEW (add --confirm to execute)"
    all_results = {}

    # Determine what to sync (default: remote hosts)
    do_remote = not local and not tags

    # Warn if --host is passed with --local (host is irrelevant for local)
    if local and hosts_list and not as_json:
        click.secho("Warning: --host is ignored with --local", fg="yellow")

    if local:
        local_results = _sync_local(packages=packages_list, confirm=confirm)
        all_results["local"] = local_results
        if not as_json:
            has_error |= _print_local_results(local_results, mode)

    if do_remote:
        remote_results = _sync_all(
            hosts=hosts_list,
            packages=packages_list,
            install=not no_install,
            confirm=confirm,
        )
        all_results["hosts"] = remote_results
        if not as_json:
            has_error |= _print_remote_results(remote_results, mode)

    if tags:
        tag_results = _sync_tags(packages=packages_list, confirm=confirm)
        all_results["tags"] = tag_results
        if not as_json:
            has_error |= _print_tag_results(tag_results, mode)

    if as_json:
        click.echo(json_mod.dumps(all_results, indent=2, default=str))

    sys.exit(1 if has_error else 0)


@click.command("sync-local")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--confirm", is_flag=True, help="Execute (default is preview/dry-run)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def sync_local_cmd(package, confirm, as_json):
    r"""
    Install local editable packages (pip install -e .).

    \b
    Without --confirm, shows what would be done (dry run).
    With --confirm, executes the installs.

    \b
    Examples:
      scitex dev versions sync-local                 # Preview
      scitex dev versions sync-local --confirm       # Execute
      scitex dev versions sync-local -p scitex       # Specific package
    """
    import json as json_mod
    import sys

    from scitex._dev._sync import sync_local as _sync_local

    packages_list = list(package) if package else None
    mode = "EXECUTE" if confirm else "PREVIEW (add --confirm to execute)"
    result = _sync_local(packages=packages_list, confirm=confirm)

    if as_json:
        click.echo(json_mod.dumps(result, indent=2, default=str))
        has_error = any(
            info.get("status") not in ("ok", "dry_run", "skipped")
            for info in result.values()
        )
        sys.exit(1 if has_error else 0)

    click.secho(f"Local packages [{mode}]", fg="cyan", bold=True)
    has_error = False
    for pkg, info in result.items():
        status = info.get("status", "unknown")
        if status == "ok":
            click.secho(f"  {pkg}: ok", fg="green")
        elif status == "dry_run":
            cmds = info.get("commands", [])
            click.secho(f"  {pkg}: " + " ".join(cmds), fg="yellow")
        elif status == "skipped":
            click.secho(f"  {pkg}: {info.get('error', 'skipped')}", fg="yellow")
        else:
            click.secho(f"  {pkg}: {info.get('error', status)}", fg="red")
            has_error = True
    sys.exit(1 if has_error else 0)


# EOF
