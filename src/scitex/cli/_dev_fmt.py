#!/usr/bin/env python3
# Timestamp: 2026-02-15
# File: scitex/cli/_dev_fmt.py

"""Formatting helpers for `scitex dev versions` output."""

from __future__ import annotations

import click


def print_versions(versions: dict) -> None:
    """Print version information in human-readable format."""
    click.secho("SciTeX Ecosystem Versions", fg="cyan", bold=True)
    click.echo("=" * 60)
    click.echo()

    for pkg, info in versions.items():
        status = info.get("status", "unknown")
        status_color = {
            "ok": "green",
            "unreleased": "yellow",
            "mismatch": "red",
            "outdated": "magenta",
            "unavailable": "white",
            "unknown": "white",
        }.get(status, "white")

        click.secho(f"{pkg}", fg="cyan", bold=True, nl=False)
        click.echo("  ", nl=False)
        click.secho(f"[{status}]", fg=status_color)

        # Local versions
        local = info.get("local", {})
        if local.get("pyproject_toml"):
            click.echo(f"    toml:      {local['pyproject_toml']}")
        if local.get("installed"):
            click.echo(f"    installed: {local['installed']}")

        # Git info
        git = info.get("git", {})
        if git.get("latest_tag"):
            click.echo(f"    git tag:   {git['latest_tag']}")
        if git.get("branch"):
            branch_str = git["branch"]
            if git.get("short_hash"):
                branch_str += f" ({git['short_hash']})"
            click.echo(f"    branch:    {branch_str}")
        # Git worktree status
        if "dirty" in git:
            dirty = git.get("dirty", False)
            ahead = git.get("ahead", 0)
            behind = git.get("behind", 0)
            parts = []
            if dirty:
                parts.append("dirty")
            else:
                parts.append("clean")
            if ahead:
                parts.append(f"ahead:{ahead}")
            if behind:
                parts.append(f"behind:{behind}")
            status_str = ", ".join(parts)
            wt_color = "red" if dirty or behind else ("yellow" if ahead else "green")
            click.echo("    worktree:  ", nl=False)
            click.secho(status_str, fg=wt_color)

        # Remote
        remote = info.get("remote", {})
        if remote.get("pypi"):
            click.echo(f"    pypi:      {remote['pypi']}")

        # Issues
        issues = info.get("issues", [])
        if issues:
            for issue in issues:
                click.secho(f"    ! {issue}", fg="yellow")

        click.echo()


def print_check_result(result: dict) -> None:
    """Print version check result with summary."""
    print_versions(result.get("packages", {}))

    summary = result.get("summary", {})
    click.secho("Summary", fg="cyan", bold=True)
    click.echo("-" * 30)

    total = summary.get("total", 0)
    ok = summary.get("ok", 0)
    unreleased = summary.get("unreleased", 0)
    mismatch = summary.get("mismatch", 0)
    outdated = summary.get("outdated", 0)
    unavailable = summary.get("unavailable", 0)

    click.echo(f"  Total:       {total}")
    click.secho(f"  OK:          {ok}", fg="green" if ok else "white")
    if unreleased:
        click.secho(f"  Unreleased:  {unreleased}", fg="yellow")
    if mismatch:
        click.secho(f"  Mismatch:    {mismatch}", fg="red")
    if outdated:
        click.secho(f"  Outdated:    {outdated}", fg="magenta")
    if unavailable:
        click.secho(f"  Unavailable: {unavailable}", fg="white")

    click.echo()
    if mismatch > 0:
        click.secho("Some packages have version mismatches!", fg="red", bold=True)
    elif unreleased > 0:
        click.secho("Some packages are ready to release.", fg="yellow")
    else:
        click.secho("All versions are consistent.", fg="green", bold=True)


def print_hosts(hosts_data: dict) -> None:
    """Print host version data."""
    click.echo()
    click.secho("SSH Hosts", fg="cyan", bold=True)
    click.echo("-" * 40)

    if "error" in hosts_data:
        click.secho(f"  Error: {hosts_data['error']}", fg="red")
        return

    for host_name, host_info in hosts_data.items():
        if host_name.startswith("_"):
            continue
        click.secho(f"  {host_name}", fg="yellow", bold=True)
        meta = host_info.get("_host", {})
        if meta:
            click.echo(f"    ({meta.get('hostname', '')} - {meta.get('role', '')})")
        for pkg, pkg_info in host_info.items():
            if pkg.startswith("_"):
                continue
            status = pkg_info.get("status", "unknown")
            installed = pkg_info.get("installed", "-")
            color = (
                "green" if status == "ok" else "red" if status == "error" else "yellow"
            )
            click.echo(f"    {pkg}: ", nl=False)
            click.secho(f"{installed}", fg=color, nl=False)
            # Show git worktree status if available
            git_parts = []
            git_hash = pkg_info.get("git_hash")
            if git_hash:
                git_parts.append(git_hash)
            if pkg_info.get("git_dirty"):
                git_parts.append("dirty")
            ahead = pkg_info.get("git_ahead", 0)
            behind = pkg_info.get("git_behind", 0)
            if ahead:
                git_parts.append(f"ahead:{ahead}")
            if behind:
                git_parts.append(f"behind:{behind}")
            if git_parts:
                git_str = " [" + ", ".join(git_parts) + "]"
                dirty = pkg_info.get("git_dirty", False)
                gc = "red" if dirty or behind else ("yellow" if ahead else "white")
                click.secho(git_str, fg=gc)
            else:
                click.echo()


def print_remotes(remotes_data: dict) -> None:
    """Print GitHub remote version data."""
    click.echo()
    click.secho("GitHub Remotes", fg="cyan", bold=True)
    click.echo("-" * 40)

    if "error" in remotes_data:
        click.secho(f"  Error: {remotes_data['error']}", fg="red")
        return

    for remote_name, remote_info in remotes_data.items():
        if remote_name.startswith("_"):
            continue
        click.secho(f"  {remote_name}", fg="yellow", bold=True)
        meta = remote_info.get("_remote", {})
        if meta:
            click.echo(f"    (org: {meta.get('org', '')})")
        for pkg, pkg_info in remote_info.items():
            if pkg.startswith("_"):
                continue
            tag = pkg_info.get("latest_tag", "-")
            release = pkg_info.get("release", "-")
            click.echo(f"    {pkg}: tag={tag}, release={release}")


def print_rtd(rtd_data: dict) -> None:
    """Print Read the Docs build status."""
    click.echo()
    click.secho("Read the Docs", fg="cyan", bold=True)
    click.echo("-" * 40)

    if "error" in rtd_data:
        click.secho(f"  Error: {rtd_data['error']}", fg="red")
        return

    for version, pkg_statuses in rtd_data.items():
        click.secho(f"  {version}", fg="yellow", bold=True)
        for pkg, info in pkg_statuses.items():
            status = info.get("status", "unknown")
            color = (
                "green"
                if status == "passing"
                else "red"
                if status == "failing"
                else "yellow"
            )
            click.echo(f"    {pkg}: ", nl=False)
            click.secho(f"{status}", fg=color)
            url = info.get("url")
            if url:
                click.echo(f"      {url}")


# EOF
