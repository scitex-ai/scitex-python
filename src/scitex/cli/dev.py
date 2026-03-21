#!/usr/bin/env python3
"""SciTeX Developer CLI — delegates entirely to scitex-dev.

Single source of truth: ``scitex dev`` == ``scitex-dev``.
"""

from scitex_dev._cli import main as dev

__all__ = ["dev"]
