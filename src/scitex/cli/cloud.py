#!/usr/bin/env python3
# File: src/scitex/cli/cloud.py
"""
SciTeX Cloud CLI - Thin wrapper delegating to scitex-cloud package.

All commands are delegated to scitex-cloud CLI for maintainability.
"""

import subprocess
import sys

import click

# Check if scitex-cloud package is available
try:
    import scitex_cloud  # noqa: F401

    HAS_CLOUD = True
except ImportError:
    HAS_CLOUD = False


def _require_cloud_pkg():
    """Check if scitex-cloud package is available."""
    if not HAS_CLOUD:
        click.secho(
            "scitex-cloud package not installed. "
            "Install with: pip install scitex-cloud",
            fg="red",
            err=True,
        )
        sys.exit(1)


_CLOUD_COMMANDS = {
    "completion": "Shell completion (bash, zsh, fish)",
    "context": "Cloud context tools (get, eval, action)",
    "deploy": "Deploy SciTeX Cloud",
    "docker": "Docker container management",
    "gitea": "Gitea/git operations (clone, create, push, pull, pr, issue)",
    "logs": "View service logs",
    "mcp": "MCP server commands (start, doctor, list-tools)",
    "setup": "Setup environment",
    "ssh": "SSH to cloud instance",
    "ssh-copy-id": "Register SSH key with cloud instance",
    "status": "Show deployment status",
    "list-python-apis": "List Python APIs",
}


@click.command(
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": True,
        "allow_extra_args": True,
        "allow_interspersed_args": False,
    },
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cloud(ctx, args):
    r"""Cloud operations and deployment (delegates to scitex-cloud).

    \b
    Commands (from scitex-cloud):
      completion       Shell completion (bash, zsh, fish)
      context          Cloud context tools (get, eval, action)
      deploy           Deploy SciTeX Cloud
      docker           Docker container management
      gitea            Gitea/git operations (clone, create, push, pull, pr, issue)
      logs             View service logs
      mcp              MCP server commands (start, doctor, list-tools)
      setup            Setup environment
      ssh              SSH to cloud instance
      ssh-copy-id      Register SSH key with cloud instance
      status           Show deployment status
      list-python-apis List Python APIs

    \b
    Examples:
      scitex cloud ssh                     # SSH into cloud workspace
      scitex cloud ssh-copy-id             # Register SSH key
      scitex cloud gitea clone user/repo
      scitex cloud mcp start
      scitex cloud status

    \b
    For full help:
      scitex cloud --help
      scitex-cloud --help
    """
    args_list = list(args)

    # Handle bare --json: list subcommands as Result JSON
    if args_list == ["--json"]:
        from scitex_dev import Result

        click.echo(
            Result(
                success=True,
                data={"package": "scitex-cloud", "commands": _CLOUD_COMMANDS},
            ).to_json()
        )
        return

    if not args_list:
        click.echo(ctx.get_help())
        return

    _require_cloud_pkg()

    # Delegate to scitex-cloud CLI
    cmd = ["scitex-cloud"] + args_list
    sys.exit(subprocess.call(cmd))


# EOF
