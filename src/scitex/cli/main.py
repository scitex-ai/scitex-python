#!/usr/bin/env python3
"""SciTeX CLI Main Entry Point."""

# Suppress httplib2/pyparsing deprecation warnings BEFORE any imports
# These come from system httplib2 using old pyparsing API (not our code)
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*deprecated.*use.*",
    category=DeprecationWarning,
    module=r"httplib2\..*",
)

import os
import sys

import click


class LazyGroup(click.Group):
    """Click group that lazily imports subcommands on demand.

    Subcommands are only imported when actually invoked, not during
    help display or tab completion. This makes CLI startup instant.
    """

    def __init__(self, *args, lazy_subcommands=None, **kwargs):
        super().__init__(*args, **kwargs)
        # {name: (module_path, attr_name, short_help)}
        self._lazy_subcommands = lazy_subcommands or {}

    def list_commands(self, ctx):
        """List all available commands."""
        base = super().list_commands(ctx)
        lazy = sorted(self._lazy_subcommands.keys())
        return sorted(set(base + lazy))

    def get_command(self, ctx, cmd_name):
        """Get a command by name, loading lazily if needed."""
        if cmd_name in self._lazy_subcommands:
            return self._load_lazy(cmd_name)
        return super().get_command(ctx, cmd_name)

    def format_commands(self, ctx, formatter):
        """Show help without importing lazy subcommands."""
        commands = []
        for name in self.list_commands(ctx):
            if name in self._lazy_subcommands:
                _, _, help_text = self._lazy_subcommands[name]
                commands.append((name, help_text))
            else:
                cmd = super().get_command(ctx, name)
                if cmd is None:
                    continue
                help_text = cmd.get_short_help_str(limit=150)
                commands.append((name, help_text))

        if commands:
            limit = formatter.width - 6 - max(len(c[0]) for c in commands)
            rows = [(name, h[:limit]) for name, h in commands]
            with formatter.section("Commands"):
                formatter.write_dl(rows)

    def _load_lazy(self, cmd_name):
        import importlib

        module_path, attr_name, _ = self._lazy_subcommands[cmd_name]
        mod = importlib.import_module(module_path)
        return getattr(mod, attr_name)


_LAZY_SUBCOMMANDS = {
    "app": ("scitex_app._cli._app", "app", "Create and manage SciTeX apps."),
    "audio": ("scitex.cli.audio", "audio", "Audio tools and text-to-speech."),
    "audit": ("scitex.cli.audit", "audit", "Security auditing tools."),
    "browser": ("scitex.cli.browser", "browser", "Browser automation tools."),
    "capture": ("scitex.cli.capture", "capture", "Screenshot capture tools."),
    "clew": ("scitex.cli.clew", "clew", "Verification and reproducibility."),
    "cloud": ("scitex.cli.cloud", "cloud", "Cloud storage operations."),
    "config": ("scitex.cli.config", "config", "Configuration management."),
    "container": (
        "scitex.cli.container",
        "container",
        "Container management (Apptainer/Singularity).",
    ),
    "convert": ("scitex.cli.convert", "convert", "File format conversion."),
    "dataset": ("scitex.cli.dataset", "dataset", "Dataset discovery and management."),
    "dev": ("scitex.cli.dev", "dev", "Developer tools."),
    "docs": ("scitex.cli.docs", "docs", "Browse and search SciTeX documentation."),
    "event": ("scitex.cli.event", "event", "Event bus for async task results."),
    "introspect": ("scitex.cli.introspect", "introspect", "Code introspection tools."),
    "linter": ("scitex.cli.linter", "linter", "SciTeX linter."),
    "mcp": ("scitex.cli.mcp", "mcp", "MCP server management."),
    "notification": (
        "scitex.cli.notification",
        "notification",
        "Notification and alerting tools.",
    ),
    "notify": (
        "scitex.cli.notification",
        "notification",
        "Notification and alerting tools.",
    ),  # backward compat alias
    "notebook": ("scitex.cli.notebook", "notebook", "Jupyter notebook tools."),
    "pkg": ("scitex.cli.pkg", "pkg", "Package management (venv drift audit)."),
    "plt": ("scitex.cli.plt", "plt", "Plotting tools."),
    "repro": ("scitex.cli.repro", "repro", "Reproducibility tools."),
    "resource": ("scitex.cli.resource", "resource", "Resource management."),
    "scholar": ("scitex.cli.scholar", "scholar", "Scholar CLI commands."),
    "security": ("scitex.cli.security", "security", "Security scanning tools."),
    "skills": ("scitex.cli.skills", "skills", "Browse skills across the ecosystem."),
    "social": ("scitex.cli.social", "social", "Social media tools."),
    "stats": ("scitex.cli.stats", "stats", "Statistical analysis tools."),
    "template": ("scitex.cli.template", "template", "Project templates."),
    "tex": ("scitex.cli.tex", "tex", "LaTeX tools."),
    "tunnel": ("scitex.cli.tunnel", "tunnel", "SSH reverse tunnel for NAT traversal."),
    "verify": ("scitex.cli.clew", "clew", "Verification (alias for clew)."),
    "web": ("scitex.cli.web", "web", "Web utilities."),
    "writer": ("scitex.cli.writer", "writer", "Manuscript writing tools."),
}


@click.group(
    cls=LazyGroup,
    lazy_subcommands=_LAZY_SUBCOMMANDS,
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option()
@click.option("--help-recursive", is_flag=True, help="Show help for all commands")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def cli(ctx, help_recursive, as_json):
    """
    Integrated Scientific Research Platform (SciTeX).

    \b
    Examples:
      scitex config list                    # Show configured paths
      scitex cloud clone user/project       # Clone from cloud
      scitex scholar bibtex papers.bib      # Manage papers
      scitex audio speak "Hello"            # Text-to-speech
      scitex mcp list-tools                 # List MCP tools
      scitex mcp start                      # Start MCP server

    \b
    Enable tab-completion:
      scitex completion          # Auto-install for your shell
      scitex completion --show   # Show installation instructions
    """
    ctx.ensure_object(dict)["as_json"] = as_json
    if help_recursive:
        if as_json:
            from . import help_recursive_to_json

            help_recursive_to_json(ctx, cli)
        else:
            _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, cli)
        else:
            click.echo(ctx.get_help())


def _get_all_command_paths(group, prefix=""):
    """Recursively get all command paths from a Click group."""
    paths = []
    for name in sorted(group.list_commands(None) or []):
        cmd = group.get_command(None, name)
        if cmd is None:
            continue
        full_path = f"{prefix} {name}".strip() if prefix else name
        paths.append((full_path, cmd))
        if isinstance(cmd, click.MultiCommand):
            paths.extend(_get_all_command_paths(cmd, full_path))
    return paths


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    # Show main CLI help first
    click.secho("━━━ scitex ━━━", fg="cyan", bold=True)
    click.echo(cli.get_help(ctx))

    # Show help for each command using Click's internal help generation
    command_paths = _get_all_command_paths(cli)
    for cmd_path, cmd in command_paths:
        click.echo()
        click.secho(f"━━━ scitex {cmd_path} ━━━", fg="cyan", bold=True)
        # Create a new context for this command
        with click.Context(cmd, info_name=cmd_path, parent=ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


def _detect_shell() -> str | None:
    """Auto-detect current shell."""
    shell_env = os.environ.get("SHELL", "")
    if "bash" in shell_env:
        return "bash"
    elif "zsh" in shell_env:
        return "zsh"
    elif "fish" in shell_env:
        return "fish"
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


@cli.group(invoke_without_command=True)
@click.pass_context
def completion(ctx):
    """
    Shell completion for scitex CLI.

    \b
    Commands:
      scitex completion install   # Install completion (default)
      scitex completion status    # Check installation status
      scitex completion bash      # Show bash completion script
      scitex completion zsh       # Show zsh completion script

    \b
    Quick install:
      scitex completion install
    """
    if ctx.invoked_subcommand is None:
        # Default to install
        ctx.invoke(completion_install)


@completion.command("install")
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False),
    help="Shell type (auto-detected if not provided).",
)
def completion_install(shell):
    """
    Install shell completion for scitex CLI.

    \b
    Examples:
      scitex completion install           # Auto-detect shell
      scitex completion install --shell bash
    """
    if not shell:
        shell = _detect_shell()
        if not shell:
            click.secho(
                "Could not auto-detect shell. Please specify with --shell option.",
                fg="red",
                err=True,
            )
            sys.exit(1)

    shell = shell.lower()
    rc_file = _get_rc_file(shell)
    completion_script = _generate_completion_script(shell)

    if not completion_script:
        click.secho("scitex CLI not found in PATH.", fg="red", err=True)
        sys.exit(1)

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


@completion.command("bash")
def completion_bash():
    """Show bash completion script."""
    script = _generate_completion_script("bash")
    if script:
        click.echo(script)
    else:
        click.secho("scitex CLI not found in PATH.", fg="red", err=True)
        sys.exit(1)


@completion.command("zsh")
def completion_zsh():
    """Show zsh completion script."""
    script = _generate_completion_script("zsh")
    if script:
        click.echo(script)
    else:
        click.secho("scitex CLI not found in PATH.", fg="red", err=True)
        sys.exit(1)


@completion.command("fish")
def completion_fish():
    """Show fish completion script."""
    script = _generate_completion_script("fish")
    if script:
        click.echo(script)
    else:
        click.secho("scitex CLI not found in PATH.", fg="red", err=True)
        sys.exit(1)


@cli.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List all scitex Python APIs (alias for: scitex introspect api scitex)."""
    from .introspect import api

    ctx.invoke(
        api,
        dotted_path="scitex",
        verbose=verbose,
        max_depth=max_depth,
        as_json=as_json,
    )


if __name__ == "__main__":
    cli()
