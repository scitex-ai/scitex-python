#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project template cloning and setup."""

from ._clone_project import clone_project
from ._scholar_writer_integration import (
    setup_scholar_writer_integration,
    ensure_integration,
)

__all__ = [
    "clone_project",
    "setup_scholar_writer_integration",
    "ensure_integration",
]

# EOF
