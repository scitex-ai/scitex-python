#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_db_parents.py
"""Backward-compat shim: parent/child operations live in _db_chain."""

from ._db_chain import ChainMixin as ParentsMixin

__all__ = ["ParentsMixin"]

# EOF
