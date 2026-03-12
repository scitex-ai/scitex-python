#!/usr/bin/env python3
"""
SciTeX Writer CLI - Thin wrapper delegating to scitex-writer package.

All commands are delegated to scitex-writer CLI for maintainability.
"""

import subprocess
import sys

import click

# Check if scitex-writer package is available
try:
    import scitex_writer

    HAS_WRITER_PKG = True
except ImportError:
    HAS_WRITER_PKG = False


def _require_writer_pkg():
    """Check if scitex-writer package is available."""
    if not HAS_WRITER_PKG:
        click.secho(
            "scitex-writer package not installed. "
            "Install with: pip install scitex-writer",
            fg="red",
            err=True,
        )
        sys.exit(1)


_WRITER_COMMANDS = {
    "compile": "Compile LaTeX to PDF",
    "bib": "Bibliography management",
    "tables": "Table management",
    "figures": "Figure management",
    "guidelines": "IMRAD writing guidelines",
    "prompts": "AI prompts (Asta integration)",
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
def writer(ctx, args):
    """
    Manuscript writing and LaTeX compilation (delegates to scitex-writer)

    \b
    Commands (from scitex-writer):
      compile     Compile LaTeX to PDF
      bib         Bibliography management
      tables      Table management
      figures     Figure management
      guidelines  IMRAD writing guidelines
      prompts     AI prompts (Asta integration)
      mcp         MCP server commands

    \b
    Examples:
      scitex writer compile manuscript ./my-paper
      scitex writer bib list ./my-paper
      scitex writer tables add ./my-paper data.csv
      scitex writer figures list ./my-paper
      scitex writer guidelines get abstract
      scitex writer prompts asta ./my-paper --section introduction

    \b
    For full help:
      scitex writer --help
      scitex-writer --help
    """
    args_list = list(args)

    if args_list == ["--json"]:
        from scitex_dev import Result

        click.echo(
            Result(
                success=True,
                data={"package": "scitex-writer", "commands": _WRITER_COMMANDS},
            ).to_json()
        )
        return

    if not args_list:
        click.echo(ctx.get_help())
        return

    _require_writer_pkg()

    # Delegate to scitex-writer CLI
    cmd = ["scitex-writer"] + args_list
    sys.exit(subprocess.call(cmd))


# EOF
