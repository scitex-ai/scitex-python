#!/usr/bin/env python3
# Timestamp: "2025-05-01 09:21:23 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/types/_ArrayLike.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/types/_ArrayLike.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import List as _List
from typing import Tuple as _Tuple
from typing import Union as _Union

import numpy as _np
import pandas as _pd

try:
    import xarray as _xr

    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    _xr = None


def _get_torch_tensor_type():
    """Lazily import torch.Tensor to avoid circular imports."""
    try:
        import torch

        return torch.Tensor
    except (ImportError, RuntimeError):
        # If torch is not available or has import issues, return None
        return type(None)


if XARRAY_AVAILABLE:
    ArrayLike = _Union[
        _List,
        _Tuple,
        _np.ndarray,
        _pd.Series,
        _pd.DataFrame,
        _xr.DataArray,
    ]
else:
    ArrayLike = _Union[
        _List,
        _Tuple,
        _np.ndarray,
        _pd.Series,
        _pd.DataFrame,
    ]


def is_array_like(obj) -> bool:
    """Check if object is array-like.

    Returns
    -------
        bool: True if object is array-like, False otherwise.
    """
    # First check against non-torch types
    base_types = [_List, _Tuple, _np.ndarray, _pd.Series, _pd.DataFrame]
    if XARRAY_AVAILABLE:
        base_types.append(_xr.DataArray)

    if isinstance(obj, tuple(base_types)):
        return True

    # Check torch tensor lazily to avoid circular imports
    try:
        import torch

        return torch.is_tensor(obj)
    except (ImportError, RuntimeError):
        return False


# EOF
