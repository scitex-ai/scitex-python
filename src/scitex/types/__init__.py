#!/usr/bin/env python3
# File: src/scitex/types/__init__.py
"""SciTeX types module — delegates to scitex-types (single source of truth)."""

from scitex_types import (
    ArrayLike,
    ColorLike,
    is_array_like,
    is_list_of_type,
    is_listed_X,
)

__all__ = [
    "ArrayLike",
    "ColorLike",
    "is_array_like",
    "is_list_of_type",
    "is_listed_X",
]

# EOF
