#!/usr/bin/env python3
"""SciTeX Dataset CLI — re-exports the standalone group as ``scitex dataset``.

Single source of truth: ``scitex_dataset._cli.main``. We import that
group directly and re-export it under the umbrella name ``dataset`` so
help text, grammar, sub-trees, and any future commands stay in one place.
"""

from __future__ import annotations

import click

try:
    from scitex_dataset._cli import main as _ds_main

    HAS_DATASET_PKG = True
except ImportError:
    HAS_DATASET_PKG = False
    _ds_main = None


if HAS_DATASET_PKG:
    # The standalone CLI is itself a ``click.Group`` (called via the
    # ``scitex-dataset`` console script). Re-binding it as ``dataset``
    # makes ``scitex dataset <args>`` behave identically to
    # ``scitex-dataset <args>``.
    dataset = _ds_main
    dataset.name = "dataset"
else:

    @click.command(
        "dataset",
        context_settings={"help_option_names": ["-h", "--help"]},
    )
    def dataset():
        """scitex-dataset is not installed."""
        click.secho(
            "scitex-dataset package not installed. "
            "Install with: pip install scitex-dataset",
            fg="red",
            err=True,
        )
        raise SystemExit(1)


# EOF
