#!/usr/bin/env python3
"""
SciTeX App — Unified file storage SDK for local + cloud apps.

Thin re-export layer. All code lives in the standalone ``scitex-app`` package.

Public API (3 functions)::

    scitex.app.get_files("./project")         # auto-detect backend
    scitex.app.register_backend("s3", factory) # register custom backend
    scitex.app.FilesBackend                    # protocol type
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Re-export everything from the standalone scitex-app package
# ---------------------------------------------------------------------------
from scitex_app import *  # noqa: F401,F403  — 3 public names
from scitex_app import (  # noqa: F401
    FilesBackend,
    get_files,
    register_backend,
)

__all__ = [
    "FilesBackend",
    "get_files",
    "register_backend",
]

# EOF
