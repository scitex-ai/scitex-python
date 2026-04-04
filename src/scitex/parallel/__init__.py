#!/usr/bin/env python3
"""SciTeX parallel module — delegates to scitex-parallel if available."""

try:
    from scitex_parallel import run

    _BACKEND = "scitex-parallel"
except ImportError:
    from ._run import run

    _BACKEND = "local"

__all__ = [
    "run",
]

# EOF
