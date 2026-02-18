#!/usr/bin/env python3
# Timestamp: 2026-01-30
# File: src/scitex/writer/__init__.py

"""SciTeX Writer - LaTeX manuscript compilation system.

This module provides a thin wrapper around scitex-writer, the core manuscript
compilation package. It uses scitex branding and environment variable prefixes.

Features
--------
- LaTeX manuscript compilation
- Supplementary materials compilation
- Revision response compilation with change tracking
- BibTeX management
- Figure/table management
- Writing guidelines

Usage
-----
    import scitex as stx

    # Create or attach to a project
    writer = stx.writer.Writer("my_paper")

    # Compile manuscript
    result = writer.compile_manuscript()
    if result.success:
        print(f"PDF created: {result.output_pdf}")

    # Compile supplementary
    result = writer.compile_supplementary()

    # Compile revision with change tracking
    result = writer.compile_revision(track_changes=True)

See Also
--------
- scitex-writer: https://github.com/ywatanabe1989/scitex-writer
- scitex: https://scitex.ai
"""

import os as _os

# Set branding BEFORE importing scitex-writer
_os.environ.setdefault("SCITEX_WRITER_BRAND", "scitex.writer")
_os.environ.setdefault("SCITEX_WRITER_ALIAS", "sw")

# Check scitex-writer availability
try:
    # Re-export main class and dataclasses
    from scitex_writer import (
        CompilationResult,
        ManuscriptTree,
        RevisionTree,
        SupplementaryTree,
        Writer,
        bib,
        compile,
        ensure_workspace,
        export,
        figures,
        guidelines,
        project,
        prompts,
        tables,
    )
    from scitex_writer import __version__ as _writer_version

    WRITER_AVAILABLE = True
    __writer_version__ = _writer_version

except ImportError:
    WRITER_AVAILABLE = False
    __writer_version__ = None

    # Provide helpful error on access
    class _WriterNotAvailable:
        """Placeholder when scitex-writer is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "scitex-writer is required for scitex.writer. "
                "Install with: pip install scitex-writer"
            )

        def __getattr__(self, name):
            raise ImportError(
                "scitex-writer is required for scitex.writer. "
                "Install with: pip install scitex-writer"
            )

    Writer = _WriterNotAvailable
    CompilationResult = _WriterNotAvailable
    ManuscriptTree = _WriterNotAvailable
    SupplementaryTree = _WriterNotAvailable
    RevisionTree = _WriterNotAvailable
    bib = None
    compile = None
    ensure_workspace = None
    export = None
    figures = None
    guidelines = None
    project = None
    prompts = None
    tables = None


def has_writer() -> bool:
    """Check if scitex-writer is available.

    Returns
    -------
    bool
        True if scitex-writer is installed and importable.
    """
    return WRITER_AVAILABLE


__all__ = [
    # Availability check
    "WRITER_AVAILABLE",
    "has_writer",
    "ensure_workspace",
    "__writer_version__",
    # Main class
    "Writer",
    # Dataclasses
    "CompilationResult",
    "ManuscriptTree",
    "SupplementaryTree",
    "RevisionTree",
    # Modules
    "bib",
    "compile",
    "export",
    "figures",
    "guidelines",
    "project",
    "prompts",
    "tables",
]

# EOF
