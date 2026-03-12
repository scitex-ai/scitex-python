#!/usr/bin/env python3
"""
SciTeX Dataset CLI - Thin wrapper delegating to scitex-dataset package.

All commands are delegated to scitex-dataset CLI for maintainability.
"""

import subprocess
import sys

import click

# Check if scitex-dataset package is available
try:
    import scitex_dataset  # noqa: F401

    HAS_DATASET_PKG = True
except ImportError:
    HAS_DATASET_PKG = False


def _require_dataset_pkg():
    """Check if scitex-dataset package is available."""
    if not HAS_DATASET_PKG:
        click.secho(
            "scitex-dataset package not installed. "
            "Install with: pip install scitex-dataset",
            fg="red",
            err=True,
        )
        sys.exit(1)


_DATASET_COMMANDS = {
    "openneuro": "Fetch datasets from OpenNeuro (BIDS neuroimaging)",
    "dandi": "Fetch datasets from DANDI Archive (NWB)",
    "physionet": "Fetch datasets from PhysioNet (EEG/ECG)",
    "db": "Local database for fast searching",
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
def dataset(ctx, args):
    r"""
    Scientific dataset discovery (delegates to scitex-dataset).

    \b
    Commands (from scitex-dataset):
      openneuro   Fetch datasets from OpenNeuro (BIDS neuroimaging)
      dandi       Fetch datasets from DANDI Archive (NWB)
      physionet   Fetch datasets from PhysioNet (EEG/ECG)
      db          Local database for fast searching
      mcp         MCP server commands

    \b
    Examples:
      scitex dataset openneuro -n 100 -o datasets.json
      scitex dataset dandi -v
      scitex dataset db build
      scitex dataset db search "alzheimer EEG"
      scitex dataset mcp list-tools

    \b
    For full help:
      scitex dataset --help
      scitex-dataset --help
    """
    args_list = list(args)

    if args_list == ["--json"]:
        from scitex_dev import Result

        click.echo(
            Result(
                success=True,
                data={"package": "scitex-dataset", "commands": _DATASET_COMMANDS},
            ).to_json()
        )
        return

    if not args_list:
        click.echo(ctx.get_help())
        return

    _require_dataset_pkg()

    # Delegate to scitex-dataset CLI
    cmd = ["scitex-dataset"] + args_list
    sys.exit(subprocess.call(cmd))


# EOF
