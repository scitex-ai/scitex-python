#!/usr/bin/env python3
"""SciTeX Linter CLI — thin wrapper delegating to `scitex-dev linter`.

The engine moved from the (archived) scitex-linter package into
`scitex_dev.linter`; this command shells out to `scitex-dev linter`
so users keep the `scitex linter <subcommand>` entry point.
"""

import subprocess
import sys

import click

try:
    import scitex_dev.linter  # noqa: F401

    HAS_LINTER_PKG = True
except ImportError:
    HAS_LINTER_PKG = False


def _require_linter_pkg():
    """Check if scitex-dev[lint] is available."""
    if not HAS_LINTER_PKG:
        click.secho(
            "scitex-dev is not installed (or scitex_dev.linter missing). "
            "Install with: pip install scitex-dev",
            fg="red",
            err=True,
        )
        sys.exit(1)


_LINTER_COMMANDS = {
    "check-files": "Check Python files for SciTeX pattern compliance",
    "format-files": "Auto-fix style-override anti-patterns (P006-P009 etc.)",
    "lint-and-run": "Lint then execute a Python script",
    "list-rules-all": "List all lint rules (engine + plugins)",
    "sweep": "Lint README + key docs across the SciTeX ecosystem",
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
    AST-based linter for SciTeX patterns (delegates to `scitex-dev linter`)

    \b
    Commands (from scitex-dev linter):
      check-files     Lint Python / .ipynb / .md / .rst files
      format-files    Auto-fix style-override anti-patterns
      lint-and-run    Lint then execute a Python script
      list-rules-all  List engine + plugin rules
      sweep           Lint README + docs across the ecosystem
      mcp             MCP server commands

    \b
    Examples:
      scitex linter check-files script.py
      scitex linter check-files ./src/ --severity error
      scitex linter lint-and-run experiment.py --strict
      scitex linter list-rules-all --category path
      scitex linter sweep --strict

    \b
    For full help:
      scitex linter --help-recursive
      scitex-dev linter --help-recursive
    """
    args_list = list(args)

    if args_list == ["--json"]:
        from scitex_dev import Result

        click.echo(
            Result(
                success=True,
                data={"package": "scitex-dev[lint]", "commands": _LINTER_COMMANDS},
            ).to_json()
        )
        return

    if not args_list:
        click.echo(ctx.get_help())
        return

    _require_linter_pkg()

    cmd = ["scitex-dev", "linter"] + args_list
    sys.exit(subprocess.call(cmd))


# EOF
