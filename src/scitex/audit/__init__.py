#!/usr/bin/env python3
"""SciTeX audit module — delegates to scitex-audit if available."""

try:
    from scitex_audit import audit

    _BACKEND = "scitex-audit"
except ImportError:
    from ._runner import audit

    _BACKEND = "local"

__all__ = ["audit"]

# EOF
