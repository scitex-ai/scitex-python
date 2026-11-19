#!/usr/bin/env python3
"""Security audit CLI.

Canonical commands (noun/verb convention):

    scitex audit-security [PATH]      run the security tools on PATH
    scitex audit-tool status          which audit tools are installed
    scitex audit-tool install         install the missing pip tools

The old ``scitex audit [PATH]``, ``scitex audit status`` and
``scitex audit install`` keep working through the hidden ``audit``
forwarder below, which prints a one-line deprecation note to stderr.
"""

from __future__ import annotations

import json
import sys

import click

from ._deprecation import REMOVE_IN

_TOOLS = {
    "bandit": ("python", "pip install bandit"),
    "shellcheck": ("shell", "apt install shellcheck"),
    "pip-audit": ("deps", "pip install pip-audit"),
    "gh": ("github", "https://cli.github.com/"),
}


@click.command("audit-security")
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
def audit_security(path, as_json, save, checks):
    """Security audit for SciTeX projects (exit 1 when anything is found).

    \b
    Runs available security tools:
      python  - Bandit (dangerous patterns)
      shell   - ShellCheck (shell script issues)
      deps    - pip-audit (known CVEs)
      github  - GitHub security alerts

    \b
    Examples:
      scitex audit-security                      # Audit current directory
      scitex audit-security . --json             # JSON output
      scitex audit-security . --save report.json # Save report
      scitex audit-security . -c python -c shell # Python + shell only
    """
    from scitex_audit._format import format_json, format_text

    from scitex.audit import audit as do_audit

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


@click.group("audit-tool", invoke_without_command=True)
@click.pass_context
def audit_tool(ctx):
    """Manage the external tools `audit-security` runs.

    \b
    Examples:
      scitex audit-tool status
      scitex audit-tool install --dry-run
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@audit_tool.command("status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def status(as_json):
    """Show which audit tools are installed.

    \b
    Examples:
      scitex audit-tool status
      scitex audit-tool status --json
    """
    import shutil

    found = {tool: shutil.which(tool) for tool in _TOOLS}
    if as_json:
        click.echo(
            json.dumps(
                {
                    tool: {
                        "check": check_name,
                        "installed": found[tool] is not None,
                        "path": found[tool],
                        "install_hint": install_hint,
                    }
                    for tool, (check_name, install_hint) in _TOOLS.items()
                }
            )
        )
        return

    click.secho("Audit Tool Status", bold=True)
    for tool, (check_name, install_hint) in _TOOLS.items():
        if found[tool]:
            badge = click.style("INSTALLED", fg="green")
            click.echo(f"  {badge}  {tool} ({check_name})")
        else:
            badge = click.style("MISSING", fg="yellow")
            click.echo(f"  {badge}  {tool} ({check_name}) — install: {install_hint}")


@audit_tool.command("install")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation (install never prompts; accepted for scripts).",
)
def install(dry_run, yes):
    """Install missing audit tools (bandit, pip-audit).

    \b
    Examples:
      scitex audit-tool install --dry-run   # Show what would be installed
      scitex audit-tool install             # pip-install the missing tools
    """
    del yes  # pip installs into the current environment without prompting
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


@click.command(
    "audit",
    hidden=True,
    add_help_option=False,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def audit(ctx):
    """(deprecated) Use `audit-security` / `audit-tool`. Removed in v3.0."""
    args = list(ctx.args)
    if args and args[0] in audit_tool.commands:
        target, prefix, display = audit_tool, args[:1], f"audit-tool {args[0]}"
        args = args[1:]
    else:
        target, prefix, display = audit_security, [], "audit-security"
    click.echo(
        f"'audit' is deprecated — use '{display}' (removed in v{REMOVE_IN})",
        err=True,
    )
    sub_ctx = target.make_context(target.name, [*prefix, *args], parent=ctx.parent)
    with sub_ctx:
        target.invoke(sub_ctx)


# Static §5 metadata (scitex-dev audit-cli): this hidden forwarder is a
# warn-phase alias. It routes `status`/`install` to `audit-tool` and
# everything else to `audit-security`, which the shared single-target
# `deprecated_alias` helper cannot express.
audit._deprecated_alias = {
    "target": "audit-security",
    "remove_in": REMOVE_IN,
    "phase": "warn",
}


# EOF
