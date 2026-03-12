#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: scitex/cli/_dev_fix_cli.py

"""CLI subcommand: scitex dev fix."""

import click


@click.command("fix")
@click.option("--host", multiple=True, help="Fix specific host(s)")
@click.option("-p", "--package", multiple=True, help="Filter to specific package(s)")
@click.option("--no-local", is_flag=True, help="Skip local fixes (pip install -e .)")
@click.option(
    "--no-remote", is_flag=True, help="Skip remote host fixes (git pull + install)"
)
@click.option("--confirm", is_flag=True, help="Execute (default is preview/dry-run)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def fix(host, package, no_local, no_remote, confirm, as_json):
    """
    Detect and fix version mismatches across the ecosystem.

    \b
    Combines mismatch detection with sync: pip install locally and
    git pull + pip install on remote hosts for packages out of sync.

    \b
    Without --confirm, shows what would be done (dry run).
    With --confirm, executes fixes in parallel across hosts.

    \b
    Examples:
      scitex dev fix                          # Preview all mismatches
      scitex dev fix --confirm               # Fix all mismatches
      scitex dev fix --confirm --host nas    # Fix specific host only
      scitex dev fix --confirm -p scitex     # Fix specific package
      scitex dev fix --no-remote --confirm   # Local fixes only
      scitex dev fix --no-local --confirm    # Remote fixes only
      scitex dev fix --json                  # JSON output (preview)
    """
    import json as json_mod
    import sys

    from scitex._dev._fix import fix_mismatches

    hosts_list = list(host) if host else None
    packages_list = list(package) if package else None
    do_local = not no_local
    do_remote = not no_remote
    mode = "EXECUTE" if confirm else "PREVIEW (add --confirm to execute)"

    result = fix_mismatches(
        hosts=hosts_list,
        packages=packages_list,
        local=do_local,
        remote=do_remote,
        confirm=confirm,
    )

    if as_json:
        click.echo(json_mod.dumps(result, indent=2, default=str))
        return

    summary = result.get("summary", {})
    detected = summary.get("detected", 0)

    click.secho(f"Version mismatch fix [{mode}]", fg="cyan", bold=True)
    click.echo()

    detected_info = result.get("detected", {})
    if not detected_info:
        click.secho("No version mismatches detected.", fg="green")
        return

    click.secho(f"Detected mismatches ({detected}):", fg="yellow")
    for pkg, info in detected_info.items():
        issues = info.get("issues", [])
        issue_str = (
            "; ".join(str(i) for i in issues) if issues else info.get("status", "")
        )
        click.echo(f"  {pkg}: {issue_str}")

    local_fixes = result.get("local_fixes", {})
    if local_fixes:
        click.echo()
        click.secho("Local fixes:", fg="cyan")
        for pkg, info in local_fixes.items():
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

    remote_fixes = result.get("remote_fixes", {})
    if remote_fixes:
        click.echo()
        click.secho("Remote fixes:", fg="cyan")
        for host_name, pkgs in remote_fixes.items():
            if not isinstance(pkgs, dict):
                continue
            click.secho(f"  {host_name}:", fg="cyan", bold=True)
            for pkg, info in pkgs.items():
                status = info.get("status", "unknown")
                if status == "ok":
                    click.secho(f"    {pkg}: ok", fg="green")
                elif status == "dry_run":
                    cmds = info.get("commands", [])
                    click.secho(f"    {pkg}: " + " && ".join(cmds), fg="yellow")
                else:
                    click.secho(f"    {pkg}: {info.get('error', status)}", fg="red")

    click.echo()
    local_fixed = summary.get("local_fixed", 0)
    remote_fixed = summary.get("remote_fixed", 0)
    if confirm:
        click.secho(
            f"Summary: {local_fixed} local fixed, {remote_fixed} remote fixed",
            fg="green" if (local_fixed + remote_fixed) >= detected else "yellow",
        )
    else:
        click.secho(
            f"Summary: {detected} mismatch(es) detected. Run with --confirm to fix.",
            fg="yellow",
        )

    has_error = any(
        info.get("status") not in ("ok", "dry_run", "skipped")
        for info in local_fixes.values()
    )
    sys.exit(1 if has_error else 0)


# EOF
