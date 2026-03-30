#!/usr/bin/env python3
# File: src/scitex/parallel/__init__.py
"""SciTeX parallel module — delegates to scitex-parallel (single source of truth)."""

from scitex_parallel import run

__all__ = [
    "run",
]

# EOF
