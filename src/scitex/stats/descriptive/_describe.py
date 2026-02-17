#!/usr/bin/env python3
# Timestamp: "2025-12-27 (refactored)"
# File: scitex/stats/descriptive/_describe.py
"""
Comprehensive descriptive statistics.

Uses torch when available (preserves tensor type), falls back to numpy.
"""

from __future__ import annotations

import os
from typing import List, Optional, Tuple, Union

import numpy as np

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)

# Optional torch support
try:
    import torch

    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

from ._nan import (
    nancount,
    nankurtosis,
    nanmax,
    nanmean,
    nanmin,
    nanq25,
    nanq50,
    nanq75,
    nanskewness,
    nanstd,
    nanvar,
)
from ._real import kurtosis, mean, q25, q50, q75, skewness, std


def _is_torch_tensor(x):
    """Check if x is a torch tensor."""
    return HAS_TORCH and isinstance(x, torch.Tensor)


def _normalize_axis(axis, dim):
    """Normalize axis/dim parameter."""
    return dim if dim is not None else axis


def verify_non_leakage(
    x,
    dim: Optional[Union[int, Tuple[int, ...]]] = None,
):
    """Verify that statistics computation doesn't leak information across samples.

    Parameters
    ----------
    x : array-like
        Input data
    dim : int or tuple, optional
        Dimension(s) along which to verify

    Returns
    -------
    bool
        True if no leakage detected
    """
    described, _ = describe(x, dim=(1, 2))
    x_first = x[:1] if _is_torch_tensor(x) else np.asarray(x)[:1]
    described_first, _ = describe(x_first, dim=dim)

    if _is_torch_tensor(x):
        assert described_first.shape == described[:1].shape, (
            f"Shape mismatch: {described_first.shape} != {described[:1].shape}"
        )
        torch.testing.assert_close(
            described_first,
            described[:1],
            rtol=1e-5,
            atol=1e-8,
            msg="Statistics leak information across samples",
        )
    else:
        assert described_first.shape == described[:1].shape, (
            f"Shape mismatch: {described_first.shape} != {described[:1].shape}"
        )
        np.testing.assert_allclose(
            described_first,
            described[:1],
            rtol=1e-5,
            atol=1e-8,
            err_msg="Statistics leak information across samples",
        )
    return True


_DEFAULT_FUNCS = ["mean", "std", "kurtosis", "skewness", "q25", "median", "q75"]


def describe(
    x,
    axis: int = -1,
    dim: Optional[Union[int, Tuple[int, ...]]] = None,
    keepdims: bool = False,
    funcs: Union[List[str], str] = None,
    device=None,
    batch_size: int = -1,
) -> Tuple[np.ndarray, List[str]]:
    """Compute descriptive statistics.

    Parameters
    ----------
    x : array-like
        Input data (numpy array or torch tensor)
    axis : int, default=-1
        Deprecated. Use dim instead
    dim : int or tuple of ints, optional
        Dimension(s) along which to compute statistics
    keepdims : bool, default=False
        Whether to keep reduced dimensions
    funcs : list of str or "all", optional
        Statistical functions to compute. Clean names (mean, std, median,
        etc.) use nan-safe implementations. Legacy nan-prefixed names
        (nanmean, nanstd, etc.) are also accepted. If None, uses default:
        ["mean", "std", "kurtosis", "skewness", "q25", "median", "q75"].
    device : optional
        Device for torch tensors (ignored for numpy)
    batch_size : int, default=-1
        Batch size for processing (currently unused)

    Returns
    -------
    Tuple[ndarray or Tensor, List[str]]
        Computed statistics stacked along last dimension and their names
    """
    if funcs is None:
        funcs = _DEFAULT_FUNCS

    dim = _normalize_axis(axis, dim)
    dim = (dim,) if isinstance(dim, int) else tuple(dim) if dim is not None else None

    # Clean names map to nan-safe functions (recommended).
    # Legacy nan-prefixed names and strict (non-nan) names also available.
    func_candidates = {
        # Clean names -> nan-safe (default, recommended)
        "mean": nanmean,
        "std": nanstd,
        "var": nanvar,
        "kurtosis": nankurtosis,
        "skewness": nanskewness,
        "q25": nanq25,
        "median": nanq50,
        "q75": nanq75,
        "max": nanmax,
        "min": nanmin,
        "count": nancount,
        # Strict (non-nan-safe) variants
        "mean_strict": mean,
        "std_strict": std,
        "kurtosis_strict": kurtosis,
        "skewness_strict": skewness,
        "q25_strict": q25,
        "q50_strict": q50,
        "q75_strict": q75,
        # Legacy nan-prefixed names (backward compat)
        "nanmean": nanmean,
        "nanstd": nanstd,
        "nanvar": nanvar,
        "nankurtosis": nankurtosis,
        "nanskewness": nanskewness,
        "nanq25": nanq25,
        "nanq50": nanq50,
        "nanq75": nanq75,
        "nanmax": nanmax,
        "nanmin": nanmin,
        "nancount": nancount,
    }

    func_names = funcs
    if funcs == "all":
        # Use clean names for "all" mode
        all_clean = [
            "mean",
            "std",
            "var",
            "kurtosis",
            "skewness",
            "q25",
            "median",
            "q75",
            "max",
            "min",
            "count",
        ]
        _funcs = [func_candidates[f] for f in all_clean]
        func_names = all_clean
    else:
        _funcs = [func_candidates[ff] for ff in func_names]

    calculated = [ff(x, dim=dim, keepdims=keepdims) for ff in _funcs]

    if _is_torch_tensor(x):
        return torch.stack(calculated, dim=-1), func_names
    else:
        return np.stack(calculated, axis=-1), func_names


# EOF
