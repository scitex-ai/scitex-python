#!/usr/bin/env python3
"""SciTeX types module — delegates to scitex-types if available."""

try:
    from scitex_types import (
        ArrayLike,
        ColorLike,
        is_array_like,
        is_list_of_type,
        is_listed_X,
    )

    _BACKEND = "scitex-types"
except ImportError:
    from ._ArrayLike import ArrayLike, is_array_like
    from ._ColorLike import ColorLike
    from ._is_listed_X import is_list_of_type, is_listed_X

    _BACKEND = "local"

__all__ = [
    "ArrayLike",
    "ColorLike",
    "is_array_like",
    "is_list_of_type",
    "is_listed_X",
]

# EOF
