#!/usr/bin/env python3
"""SciTeX etc module — delegates to scitex-etc if available."""

try:
    from scitex_etc import count, wait_key

    _BACKEND = "scitex-etc"
except ImportError:
    from .wait_key import count, wait_key

    _BACKEND = "local"

__all__ = ["wait_key", "count"]

# EOF
