#!/usr/bin/env python3
"""SciTeX Linter CLI - Thin wrapper delegating to scitex-linter package."""

import subprocess
import sys

import click

try:
    import scitex_linter

    HAS_LINTER_PKG = True
except ImportError:
    HAS_LINTER_PKG = False


def _require_linter_pkg():
    """Check if scitex-linter package is available."""
    if not HAS_LINTER_PKG:
        click.secho(
            "scitex-linter package not installed. "
            "Install with: pip install scitex-linter",
            fg="red",
            err=True,
        )
        sys.exit(1)


_LINTER_COMMANDS = {
    "lint": "Lint Python files for SciTeX pattern compliance",
    "python": "Lint then execute a Python script",
    "list-rules": "List all lint rules",
    "mcp": "MCP server commands",
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
def linter(ctx, args):
    """
    AST-based linter for SciTeX patterns (delegates to scitex-linter)

    \b
    Commands (from scitex-linter):
      lint        Lint Python files for SciTeX pattern compliance
      python      Lint then execute a Python script
      list-rules  List all lint rules
      mcp         MCP server commands

    \b
    Examples:
      scitex linter lint script.py
      scitex linter lint ./src/ --severity error
      scitex linter python experiment.py --strict
      scitex linter list-rules --category path

    \b
    For full help:
      scitex linter --help-recursive
      scitex-linter --help-recursive
    """
    args_list = list(args)

    if args_list == ["--json"]:
        from scitex_dev import Result

        click.echo(
            Result(
                success=True,
                data={"package": "scitex-linter", "commands": _LINTER_COMMANDS},
            ).to_json()
        )
        return

    if not args_list:
        click.echo(ctx.get_help())
        return

    _require_linter_pkg()

    cmd = ["scitex-linter"] + args_list
    sys.exit(subprocess.call(cmd))


# EOF
