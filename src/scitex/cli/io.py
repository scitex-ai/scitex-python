#!/usr/bin/env python3
"""SciTeX I/O CLI — re-exports the standalone group as ``scitex io``.

Single source of truth: ``scitex_io._cli._main.main``. We import that
group directly and re-bind it as ``io`` so help text, grammar, sub-trees,
and any future commands stay in one place.

Per general/03_interface_02_cli/05a_umbrella-passthrough.md (§5b).
"""

from __future__ import annotations

import click

try:
    from scitex_io._cli._main import main as _io_main

    HAS_IO_PKG = True
except ImportError:
    HAS_IO_PKG = False
    _io_main = None


if HAS_IO_PKG:
    # The standalone CLI is itself a ``click.Group`` (called via the
    # ``scitex-io`` console script). Re-binding it as ``io`` makes
    # ``scitex io <args>`` behave identically to ``scitex-io <args>``.
    io = _io_main
    io.name = "io"
else:

    @click.command(
        "io",
        context_settings={"help_option_names": ["-h", "--help"]},
    )
    def io():
        """scitex-io is not installed."""
        click.secho(
            "scitex-io package not installed. Install with: pip install scitex-io",
            fg="red",
            err=True,
        )
        raise SystemExit(1)


# EOF
