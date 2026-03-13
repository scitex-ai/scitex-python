#!/usr/bin/env python3
# Timestamp: 2026-02-08
# File: scitex/cli/_dev_clone.py

"""Clone command for scitex dev CLI."""

import click


@click.command("clone")
@click.option(
    "-p",
    "--package",
    multiple=True,
    help="Clone specific package(s) only",
)
@click.option(
    "--branch",
    "-b",
    default="develop",
    help="Branch to checkout after cloning (default: develop)",
)
@click.option(
    "--install",
    "-e",
    is_flag=True,
    help="Run pip install -e . after cloning",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without executing",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def clone(package, branch, install, dry_run, as_json):
    """
    Clone ecosystem repos and switch to a branch.

    \b
    Clones all (or selected) ecosystem repositories to their
    configured local paths and checks out the specified branch.

    \b
    Examples:
      scitex dev clone                     # Clone all, checkout develop
      scitex dev clone -b main             # Clone all, stay on main
      scitex dev clone -p figrecipe        # Clone only figrecipe
      scitex dev clone -e                  # Clone all + pip install -e .
      scitex dev clone --dry-run           # Preview without executing
      scitex dev clone --json              # JSON output
    """
    from pathlib import Path

    from scitex._dev._ecosystem import ECOSYSTEM

    targets = {k: v for k, v in ECOSYSTEM.items() if not package or k in package}

    if not targets:
        if as_json:
            from scitex_dev import Result

            click.echo(
                Result(success=False, error="No matching packages found.").to_json()
            )
        else:
            click.secho("No matching packages found.", fg="red")
        return

    if dry_run:
        plan = {
            "action": "dry_run",
            "branch": branch,
            "install": install,
            "targets": {
                name: {
                    "local_path": str(Path(info["local_path"]).expanduser()),
                    "github_repo": info["github_repo"],
                    "exists": Path(info["local_path"]).expanduser().exists(),
                }
                for name, info in targets.items()
            },
        }
        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data=plan).to_json())
        else:
            click.secho(
                f"[dry-run] Would clone {len(targets)} repos → branch '{branch}'",
                fg="cyan",
                bold=True,
            )
            for name, info in plan["targets"].items():
                status = "exists" if info["exists"] else "clone"
                click.echo(f"  {name}: {status} → {info['local_path']}")
        return

    if not as_json:
        click.secho(
            f"Cloning {len(targets)} repos → branch '{branch}'",
            fg="cyan",
            bold=True,
        )
        click.echo()

    results = {}
    for name, info in targets.items():
        local = Path(info["local_path"]).expanduser()
        clone_url = f"git@github.com:{info['github_repo']}.git"

        if local.exists():
            if not as_json:
                click.secho(f"  {name}: ", fg="yellow", nl=False)
                click.echo(f"exists at {local}")
            _checkout_branch(local, branch)
            results[name] = {"status": "exists", "path": str(local)}
        else:
            if not as_json:
                click.secho(f"  {name}: ", fg="cyan", nl=False)
                click.echo(f"cloning → {local}")
            _clone_repo(clone_url, local, branch)
            results[name] = {"status": "cloned", "path": str(local)}

        if install and local.exists():
            _pip_install(local)
            results[name]["installed"] = True

    if as_json:
        from scitex_dev import Result

        click.echo(
            Result(
                success=True,
                data={
                    "branch": branch,
                    "repos": results,
                    "total": len(results),
                },
            ).to_json()
        )
    else:
        click.echo()
        click.secho("Done.", fg="green", bold=True)


def _checkout_branch(local, branch):
    """Fetch and checkout branch in existing repo."""
    import subprocess

    try:
        subprocess.run(
            ["git", "fetch", "--all"],
            cwd=local,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "checkout", branch],
            cwd=local,
            capture_output=True,
            check=True,
        )
        click.secho(f"           → checked out '{branch}'", fg="green")
    except subprocess.CalledProcessError:
        click.secho(f"           → branch '{branch}' not available", fg="red")


def _clone_repo(clone_url, local, branch):
    """Clone repo and checkout branch."""
    import subprocess

    local.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", clone_url, str(local)],
            check=True,
        )
        subprocess.run(
            ["git", "checkout", branch],
            cwd=local,
            capture_output=True,
            check=True,
        )
        click.secho(f"           → cloned, on '{branch}'", fg="green")
    except subprocess.CalledProcessError as e:
        click.secho(f"           → failed: {e}", fg="red")


def _pip_install(local):
    """Run pip install -e . in a directory."""
    import subprocess

    click.echo("           → pip install -e .", nl=False)
    try:
        subprocess.run(
            ["pip", "install", "-e", "."],
            cwd=local,
            capture_output=True,
            check=True,
        )
        click.secho(" ok", fg="green")
    except subprocess.CalledProcessError:
        click.secho(" failed", fg="red")


# EOF
