#!/usr/bin/env python3
# File: scitex/audit/__init__.py

"""
SciTeX Audit Module

Unified security scanning by orchestrating bandit (Python), shellcheck (shell),
pip-audit (deps), and GitHub alerts.

Usage:
    from scitex.audit import audit

    results = audit(".")
    results = audit(".", checks=["python", "shell"])
"""

from __future__ import annotations

from ._runner import audit

__all__ = ["audit"]

# EOF
