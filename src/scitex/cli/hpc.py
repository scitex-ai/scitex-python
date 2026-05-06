#!/usr/bin/env python3
"""SciTeX HPC CLI — re-exports the standalone group as ``scitex hpc``.

Single source of truth: ``scitex_hpc._cli.cli``.

Per general/03_interface_02_cli/05a_umbrella-passthrough.md (§5b).
"""

from __future__ import annotations

import click

try:
    from scitex_hpc._cli import cli as _hpc_cli

    HAS_HPC_PKG = True
except ImportError:
    HAS_HPC_PKG = False
    _hpc_cli = None


if HAS_HPC_PKG:
    hpc = _hpc_cli
    hpc.name = "hpc"
else:

    @click.command(
        "hpc",
        context_settings={"help_option_names": ["-h", "--help"]},
    )
    def hpc():
        """scitex-hpc is not installed."""
        click.secho(
            "scitex-hpc package not installed. Install with: pip install scitex-hpc",
            fg="red",
            err=True,
        )
        raise SystemExit(1)


# EOF
