#!/usr/bin/env python3
# File: src/scitex/etc/__init__.py
"""SciTeX etc module — delegates to scitex-etc (single source of truth)."""

from scitex_etc import count, wait_key

__all__ = ["wait_key", "count"]

# EOF
