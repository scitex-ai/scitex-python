#!/usr/bin/env python3
# Timestamp: 2026-01-29
# File: src/scitex/cli/scholar/_crossref_scitex.py
"""CrossRef-SciTeX CLI - Thin wrapper delegating to crossref-local.

This module provides access to the local CrossRef database (167M+ papers)
by delegating directly to crossref-local CLI without any modifications.
"""

from __future__ import annotations

import sys

import click


@click.command(
    "crossref-scitex",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option("--help-recursive", is_flag=True, help="Show help for all commands")
@click.pass_context
def crossref_scitex(ctx, help_recursive):
    """CrossRef-SciTeX database search (167M+ papers).

    \b
    Thin wrapper for crossref-local. All arguments passed directly.
    Run 'crossref-local --help' for full options.

    \b
    Examples:
        scitex scholar crossref-scitex search "deep learning" --abstracts
        scitex scholar crossref-scitex search-by-doi 10.1038/nature12373
        scitex scholar crossref-scitex status
        scitex scholar crossref-scitex cache query "neural networks"
    """
    try:
        from crossref_local.cli import cli as crossref_cli
    except ImportError:
        click.secho(
            "crossref-local not installed. Install with: pip install crossref-local",
            fg="red",
        )
        sys.exit(1)

    # Handle --help-recursive by delegating to crossref-local
    args = ctx.args
    if help_recursive:
        args = ["--help-recursive"]

    # Delegate all arguments to crossref-local CLI
    sys.exit(crossref_cli.main(args, standalone_mode=False))


# EOF
