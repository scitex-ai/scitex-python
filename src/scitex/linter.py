#!/usr/bin/env python3
"""SciTeX Linter — thin wrapper delegating to scitex_dev.linter.

Usage:
    import scitex as stx
    issues = stx.linter.lint_file("script.py")

The engine moved from the (now archived) `scitex-linter` package into
`scitex_dev.linter` as part of the per-package rule migration. This
shim re-exports the public surface so existing `stx.linter.X` callers
keep working unchanged.
"""

import os as _os

# Set branding (consumed by scitex_dev.linter for CLI prog_name etc.)
_os.environ.setdefault("SCITEX_DEV_LINTER_BRAND", "scitex.linter")
_os.environ.setdefault("SCITEX_DEV_LINTER_ALIAS", "linter")

try:
    from scitex_dev.linter.checker import lint_file, lint_source
    from scitex_dev.linter.formatter import format_issue, format_summary, to_json
    from scitex_dev.linter.rules import ALL_RULES
except ImportError:

    def lint_file(*args, **kwargs):
        raise ImportError(
            "scitex-dev is required. Install with: pip install scitex-dev"
        )

    def lint_source(*args, **kwargs):
        raise ImportError(
            "scitex-dev is required. Install with: pip install scitex-dev"
        )

    format_issue = None
    format_summary = None
    to_json = None
    ALL_RULES = {}

__all__ = [
    "lint_file",
    "lint_source",
    "format_issue",
    "format_summary",
    "to_json",
    "ALL_RULES",
]

# EOF
