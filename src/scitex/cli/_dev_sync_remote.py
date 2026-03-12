#!/usr/bin/env python3
# Timestamp: 2026-02-26
# File: scitex/cli/_dev_sync_remote.py

"""CLI subcommands: scitex dev versions diff/commit/pull."""

import click


@click.command("diff")
@click.option("--host", default=None, help="Host name (default: first enabled host)")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def diff(host, package, as_json):
    """
    Show uncommitted changes on remote host(s). Read-only.

    \b
    Examples:
      scitex dev versions diff                  # Show diffs on all hosts
      scitex dev versions diff --host nas       # Specific host
      scitex dev versions diff -p scitex        # Specific package
      scitex dev versions diff --json           # JSON output
    """
    import json as json_mod

    from scitex._dev._sync_remote import remote_diff

    packages = list(package) if package else None
    result = remote_diff(host=host, packages=packages)

    if as_json:
        click.echo(json_mod.dumps(result, indent=2, default=str))
        return

    if "error" in result:
        click.secho(f"Error: {result['error']}", fg="red")
        return

    for host_name, pkgs in result.items():
        click.secho(f"\n{host_name}:", fg="cyan", bold=True)
        for pkg_name, info in pkgs.items():
            status = info.get("status", "unknown")
            if status == "clean":
                click.secho(f"  {pkg_name}: clean", fg="green")
            elif status == "dirty":
                click.secho(f"  {pkg_name}: dirty", fg="yellow")
                files = info.get("files", "")
                if files:
                    for line in files.splitlines():
                        click.echo(f"    {line}")
                stat = info.get("diff_stat", "")
                if stat:
                    click.echo(f"    {stat}")
            else:
                click.secho(f"  {pkg_name}: {info.get('error', status)}", fg="red")


@click.command("commit")
@click.option("--host", required=True, help="Host name (required)")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option(
    "-m", "--message", default=None, help="Commit message (auto-generated if omitted)"
)
@click.option("--no-push", is_flag=True, help="Commit only, do not push to origin")
@click.option("--confirm", is_flag=True, help="Execute (default is preview/dry-run)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def commit(host, package, message, no_push, confirm, as_json):
    """
    Commit dirty changes on a remote host and push to origin.

    \b
    Without --confirm, shows what would be committed (dry run).
    With --confirm, executes commit + push.

    \b
    Examples:
      scitex dev versions commit --host nas             # Preview
      scitex dev versions commit --host nas --confirm   # Execute
      scitex dev versions commit --host nas -m "fix"    # Custom message
      scitex dev versions commit --host nas --no-push   # Commit only
    """
    import json as json_mod

    from scitex._dev._sync_remote import remote_commit

    packages = list(package) if package else None
    result = remote_commit(
        host=host,
        packages=packages,
        message=message,
        push=not no_push,
        confirm=confirm,
    )

    if as_json:
        click.echo(json_mod.dumps(result, indent=2, default=str))
        return

    if "error" in result:
        click.secho(f"Error: {result['error']}", fg="red")
        return

    mode = "EXECUTE" if confirm else "PREVIEW (add --confirm to execute)"
    click.secho(f"Remote commit on {host} [{mode}]", fg="cyan", bold=True)
    for pkg_name, info in result.items():
        status = info.get("status", "unknown")
        if status == "clean":
            click.secho(f"  {pkg_name}: nothing to commit", fg="green")
        elif status == "dry_run":
            click.secho(f"  {pkg_name}: dirty", fg="yellow")
            files = info.get("dirty_files", "")
            if files:
                for line in files.splitlines():
                    click.echo(f"    {line}")
            cmds = info.get("commands", [])
            if cmds:
                click.echo(f"    would run: {' && '.join(cmds)}")
        elif status == "ok":
            click.secho(f"  {pkg_name}: committed", fg="green")
            output = info.get("output", "")
            if output:
                for line in output.splitlines()[:5]:
                    click.echo(f"    {line}")
        else:
            click.secho(f"  {pkg_name}: {info.get('error', status)}", fg="red")


@click.command("pull")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--confirm", is_flag=True, help="Execute (default is preview/dry-run)")
@click.option("--no-stash", is_flag=True, help="Don't stash dirty repos before pull")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def pull(package, confirm, no_stash, as_json):
    """
    Pull latest from origin to local repos.

    \b
    Without --confirm, shows what would be pulled (dry run).
    With --confirm, executes git pull.
    Dirty repos are stashed before pull and popped after (use --no-stash to disable).

    \b
    Examples:
      scitex dev versions pull                  # Preview
      scitex dev versions pull --confirm        # Execute
      scitex dev versions pull -p scitex        # Specific package
      scitex dev versions pull --no-stash       # Don't stash dirty repos
    """
    import json as json_mod

    from scitex._dev._sync_remote import pull_local

    packages = list(package) if package else None
    result = pull_local(packages=packages, confirm=confirm, stash=not no_stash)

    if as_json:
        click.echo(json_mod.dumps(result, indent=2, default=str))
        return

    mode = "EXECUTE" if confirm else "PREVIEW (add --confirm to execute)"
    click.secho(f"Pull from origin [{mode}]", fg="cyan", bold=True)
    for pkg_name, info in result.items():
        status = info.get("status", "unknown")
        if status == "ok":
            stash_note = " (stashed+popped)" if info.get("stashed") else ""
            click.secho(
                f"  {pkg_name}: {info.get('output', 'ok')}{stash_note}", fg="green"
            )
        elif status == "stash_conflict":
            click.secho(f"  {pkg_name}: stash pop conflict", fg="red")
            click.echo(f"    pull output: {info.get('output', '')}")
            click.echo(f"    error: {info.get('error', '')}")
            click.echo("    resolve manually: git stash pop")
        elif status == "dry_run":
            cmds = info.get("commands", [])
            note = info.get("note", "")
            click.secho(f"  {pkg_name}: " + " ".join(cmds), fg="yellow")
            if note:
                click.echo(f"    note: {note}")
        elif status == "skipped":
            click.secho(f"  {pkg_name}: {info.get('error', 'skipped')}", fg="yellow")
        else:
            click.secho(f"  {pkg_name}: {info.get('error', status)}", fg="red")


# EOF
