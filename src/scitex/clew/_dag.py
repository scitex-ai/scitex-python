#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_dag.py
"""Multi-target DAG verification — delegates to _chain._dag."""

from ._chain._dag import _topological_sort, verify_dag

__all__ = ["_topological_sort", "verify_dag"]

# EOF
