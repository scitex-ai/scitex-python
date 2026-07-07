#!/usr/bin/env python3
"""Shell completion for the umbrella ``scitex`` CLI — canonical noun group.

Doctrine §1b (02_cli/04_exceptions.md, amended 2026-07-07): a bare
``completion`` leaf command is banned; ``completion`` is a noun group
whose subcommands are the verbs:

    scitex completion install [--shell {bash,zsh,fish}] [--dry-run]
    scitex completion status

``completion install --dry-run`` prints the target rc file and the
completion script without touching the filesystem. It subsumes the old
``completion bash|zsh|fish`` script-dump leaves, which remain as hidden
warn-phase deprecated aliases (removed in v3.0).

Moved out of ``main.py`` (CLI-standardization slice 5) so the group is
lazily mounted like every other subcommand and the orchestrator stays
under the 512-line cap.
"""

import os
import sys

import click

_SHELLS = ("bash", "zsh", "fish")


def _detect_shell() -> str | None:
    """Auto-detect current shell."""
    shell_env = os.environ.get("SHELL", "")
    for shell in _SHELLS:
        if shell in shell_env:
            return shell
    return None


def _get_rc_file(shell: str) -> str:
    """Get shell config file path."""
    if shell == "bash":
        return os.path.expanduser("~/.bashrc")
    elif shell == "zsh":
        return os.path.expanduser("~/.zshrc")
    elif shell == "fish":
        return os.path.expanduser("~/.config/fish/config.fish")
    return ""


def _generate_completion_script(shell: str) -> str:
    """Generate completion script for scitex CLI."""
    import shutil

    cli_path = shutil.which("scitex")
    if not cli_path:
        return ""

    if shell == "bash":
        return f'# scitex tab completion\neval "$(_SCITEX_COMPLETE=bash_source {cli_path})"'
    elif shell == "zsh":
        return (
            f'# scitex tab completion\neval "$(_SCITEX_COMPLETE=zsh_source {cli_path})"'
        )
    elif shell == "fish":
        return f"# scitex tab completion\neval (env _SCITEX_COMPLETE=fish_source {cli_path})"
    return ""


def _resolve_shell(shell: str | None) -> str:
    """Resolve ``--shell`` or auto-detect; exit 1 with guidance on failure."""
    if not shell:
        shell = _detect_shell()
        if not shell:
            click.secho(
                "Could not auto-detect shell. Please specify with --shell option.",
                fg="red",
                err=True,
            )
            sys.exit(1)
    return shell.lower()


@click.group("completion")
def completion():
    """
    Shell tab-completion management.

    \b
    Commands:
      scitex completion install            # Install completion for your shell
      scitex completion install --dry-run  # Print target rc file + script only
      scitex completion status             # Check installation status
    """


@completion.command("install")
@click.option(
    "--shell",
    type=click.Choice(_SHELLS, case_sensitive=False),
    help="Shell type (auto-detected if not provided).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print the target rc file and completion script without writing.",
)
def completion_install(shell, dry_run):
    """
    Install shell completion for the scitex CLI.

    \b
    Examples:
      scitex completion install                       # Auto-detect shell
      scitex completion install --shell bash
      scitex completion install --dry-run             # Inspect, write nothing
    """
    shell = _resolve_shell(shell)
    rc_file = _get_rc_file(shell)
    completion_script = _generate_completion_script(shell)

    if not completion_script:
        click.secho("scitex CLI not found in PATH.", fg="red", err=True)
        sys.exit(1)

    if dry_run:
        click.echo(f"# would append to: {rc_file}")
        click.echo(completion_script)
        return

    # Check if already installed
    if os.path.exists(rc_file):
        with open(rc_file) as f:
            content = f.read()
            if "scitex tab completion" in content:
                click.secho(f"Completion already installed in {rc_file}", fg="yellow")
                click.echo(
                    "\nTo reinstall, first remove the existing block, then run again."
                )
                click.echo("\nTo reload, run:")
                click.secho(f"  source {rc_file}", fg="cyan")
                sys.exit(0)

    # Install
    try:
        os.makedirs(os.path.dirname(rc_file), exist_ok=True)
        with open(rc_file, "a") as f:
            f.write(f"\n{completion_script}\n")

        click.secho(f"Installed scitex completion to {rc_file}", fg="green")
        click.echo("\nTo activate, run:")
        click.secho(f"  source {rc_file}", fg="cyan")

    except Exception as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        click.echo("\nManually add to your shell config:")
        click.echo(completion_script)
        sys.exit(1)


@completion.command("status")
def completion_status():
    """
    Check shell completion installation status.

    \b
    Shows:
      - Current shell
      - Config file path
      - Installation status

    \b
    Example:
      scitex completion status
    """
    import shutil

    shell = _detect_shell() or "unknown"
    rc_file = _get_rc_file(shell) if shell != "unknown" else "N/A"

    click.secho("Shell Completion Status", fg="cyan", bold=True)
    click.echo(f"  Shell: {shell}")
    click.echo(f"  Config: {rc_file}")

    # Check if installed
    installed = False
    if rc_file != "N/A" and os.path.exists(rc_file):
        with open(rc_file) as f:
            content = f.read()
            if "scitex tab completion" in content:
                installed = True

    status = (
        click.style("installed", fg="green")
        if installed
        else click.style("not installed", fg="yellow")
    )
    click.echo(f"  Status: {status}")

    # Check if scitex is in PATH
    cli_path = shutil.which("scitex")
    path_status = (
        click.style("OK", fg="green") if cli_path else click.style("missing", fg="red")
    )
    click.echo(f"  scitex in PATH: {path_status}")

    if not installed:
        click.echo("\nTo install completion:")
        click.secho("  scitex completion install", fg="cyan")


def _register_deprecated_script_leaf(shell_name: str) -> None:
    """Hidden warn-phase alias: ``completion <shell>`` -> ``install --dry-run``.

    The old script-dump leaves keep printing the script (warn-phase
    forwards, doctrine §5 11_deprecation.md) but are hidden from help
    and warn on stderr. Removed in v3.0.
    """

    @completion.command(shell_name, hidden=True)
    def _leaf():
        f"""(deprecated) Use 'completion install --dry-run --shell {shell_name}'."""
        click.echo(
            f"'completion {shell_name}' is deprecated — use "
            f"'completion install --dry-run --shell {shell_name}' "
            f"(removed in v3.0)",
            err=True,
        )
        script = _generate_completion_script(shell_name)
        if script:
            click.echo(script)
        else:
            click.secho("scitex CLI not found in PATH.", fg="red", err=True)
            sys.exit(1)

    _leaf.short_help = (
        f"(deprecated) Use 'completion install --dry-run --shell {shell_name}'."
    )
    _leaf.help = (
        f"(deprecated) Prints the {shell_name} completion script. "
        f"Use 'completion install --dry-run --shell {shell_name}'. "
        f"Removed in v3.0."
    )
    _leaf._deprecated_alias = {
        "target": f"install --dry-run --shell {shell_name}",
        "remove_in": "3.0",
        "phase": "warn",
    }


for _shell in _SHELLS:
    _register_deprecated_script_leaf(_shell)


# EOF
