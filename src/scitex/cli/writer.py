#!/usr/bin/env python3
"""SciTeX Writer CLI — re-exports the standalone group as ``scitex writer``.

Single source of truth: ``scitex_writer._cli.main``. We import that
group directly and re-bind it as ``writer`` so help text, grammar,
sub-trees, and any future commands stay in one place.

Per general/03_interface_02_cli/05a_umbrella-passthrough.md (§5b).
"""

from __future__ import annotations

import click

try:
    # main_group is the click.Group (line 76 of scitex_writer._cli.__init__);
    # `main` is a wrapper function that's also exposed but not a Group.
    from scitex_writer._cli import main_group as _writer_main

    HAS_WRITER_PKG = True
except ImportError:
    HAS_WRITER_PKG = False
    _writer_main = None


if HAS_WRITER_PKG:
    writer = _writer_main
    writer.name = "writer"
else:

    @click.command(
        "writer",
        context_settings={"help_option_names": ["-h", "--help"]},
    )
    def writer():
        """scitex-writer is not installed."""
        click.secho(
            "scitex-writer package not installed. "
            "Install with: pip install scitex-writer",
            fg="red",
            err=True,
        )
        raise SystemExit(1)


# EOF
