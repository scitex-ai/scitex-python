#!/usr/bin/env python3
"""Security audit CLI."""

from __future__ import annotations

import sys

import click


@click.group(invoke_without_command=True)
@click.argument("path", default=".", required=False, type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.option("--save", "-s", type=click.Path(), help="Save report to file.")
@click.option(
    "--check",
    "-c",
    "checks",
    multiple=True,
    type=click.Choice(["python", "shell", "deps", "github"]),
    help="Run specific checks only.",
)
@click.pass_context
def audit(ctx, path, as_json, save, checks):
    """Security audit for SciTeX projects.

    \b
    Runs available security tools:
      python  - Bandit (dangerous patterns)
      shell   - ShellCheck (shell script issues)
      deps    - pip-audit (known CVEs)
      github  - GitHub security alerts

    \b
    Examples:
      scitex audit                      # Audit current directory
      scitex audit . --json             # JSON output
      scitex audit . --save report.json # Save report
      scitex audit . -c python -c shell # Python + shell only
    """
    if ctx.invoked_subcommand is not None:
        return

    from scitex.audit import audit as do_audit
    from scitex.audit._format import format_json, format_text

    results = do_audit(
        path=path,
        checks=list(checks) if checks else None,
        output_file=save,
    )

    if as_json:
        click.echo(format_json(results))
    else:
        click.echo(format_text(results))

    # Exit code: 1 if any findings
    has_findings = any(r.get("status") == "findings" for r in results.values())
    if has_findings:
        sys.exit(1)


@audit.command()
def status():
    """Show which audit tools are installed."""
    import shutil

    tools = {
        "bandit": ("python", "pip install bandit"),
        "shellcheck": ("shell", "apt install shellcheck"),
        "pip-audit": ("deps", "pip install pip-audit"),
        "gh": ("github", "https://cli.github.com/"),
    }

    click.secho("Audit Tool Status", bold=True)
    for tool, (check_name, install_hint) in tools.items():
        path = shutil.which(tool)
        if path:
            badge = click.style("INSTALLED", fg="green")
            click.echo(f"  {badge}  {tool} ({check_name})")
        else:
            badge = click.style("MISSING", fg="yellow")
            click.echo(f"  {badge}  {tool} ({check_name}) — install: {install_hint}")


@audit.command()
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
def install(dry_run):
    """Install missing audit tools (bandit, pip-audit)."""
    import shutil
    import subprocess

    pip_tools = []
    if not shutil.which("bandit"):
        pip_tools.append("bandit")
    if not shutil.which("pip-audit"):
        pip_tools.append("pip-audit")

    if dry_run:
        if pip_tools:
            click.secho("[dry-run] Would install via pip:", fg="cyan")
            for tool in pip_tools:
                click.echo(f"  pip install {tool}")
        else:
            click.echo(
                "[dry-run] All pip-installable tools already installed — nothing to do."
            )
        if not shutil.which("shellcheck"):
            click.secho(
                "[dry-run] Would need manual install: sudo apt install shellcheck",
                fg="cyan",
            )
        return

    if pip_tools:
        click.echo(f"Installing: {', '.join(pip_tools)}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + pip_tools,
            check=True,
        )
        click.secho(f"Installed: {', '.join(pip_tools)}", fg="green")
    else:
        click.echo("All pip-installable tools already installed.")

    if not shutil.which("shellcheck"):
        click.secho(
            "\nShellCheck requires system install: sudo apt install shellcheck",
            fg="yellow",
        )


# EOF
