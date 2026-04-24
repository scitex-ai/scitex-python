#!/usr/bin/env python3
"""SciTeX compat module — delegates to scitex-compat."""

from scitex_compat import deprecated, notify, notify_async

__all__ = [
    "deprecated",
    "notify",
    "notify_async",
]

# EOF
