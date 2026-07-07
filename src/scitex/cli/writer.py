#!/usr/bin/env python3
"""Umbrella mount for the scitex-writer CLI (doctrine §5b re-export shim).

``scitex_writer._cli`` exposes BOTH ``main`` (a plain ``def main(argv)``
console-script function) and ``main_group`` (the click ``Group``). The
registry-driven probe used to pick up ``main`` — a function has no
``make_context``, so ``scitex writer --help`` crashed with
``AttributeError``. This explicit wrapper re-exports the click group,
which is the single source of truth for the writer command surface.
"""

import click

try:
    from scitex_writer._cli import main_group as _main
except ImportError:
    _main = None

if _main is not None:
    writer = _main
    writer.name = "writer"  # prog-name fragment shown under `scitex`
else:

    @click.command("writer")
    def writer():
        """scitex-writer not installed."""
        click.secho("Install with: pip install scitex-writer", fg="red")
        raise SystemExit(1)


# EOF
