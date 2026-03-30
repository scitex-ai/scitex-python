#!/usr/bin/env python3
# File: src/scitex/compat/__init__.py
"""SciTeX compat module — delegates to scitex-compat (single source of truth)."""

from scitex_compat import deprecated, notify, notify_async

__all__ = [
    "deprecated",
    "notify",
    "notify_async",
]

# EOF
