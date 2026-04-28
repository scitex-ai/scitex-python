#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_signal_fn.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/decorators/_signal_fn.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from functools import wraps
from typing import Any as _Any
from typing import Callable

import numpy as np

from ._converters import _return_always, is_nested_decorator, to_torch


def signal_fn(func: Callable) -> Callable:
    """Decorator for signal processing functions that converts only the first argument (signal) to torch tensor.

    This decorator is designed for DSP functions where:
    - The first argument is the signal data that should be converted to torch tensor
    - Other arguments (like sampling frequency, bands, etc.) should remain as-is
    """

    @wraps(func)
    def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
        # Skip conversion if already in a nested decorator context
        if is_nested_decorator():
            results = func(*args, **kwargs)
            return results

        # Set the current decorator context
        wrapper._current_decorator = "signal_fn"

        # Store original object for type preservation
        original_object = args[0] if args else None

        # Capture the original numpy dtype (if any) so we can restore it on
        # the way back. This protects against operations inside ``func`` that
        # silently upcast/downcast (e.g. torch ops that promote to float32).
        original_dtype = getattr(original_object, "dtype", None)
        try:
            if original_dtype is not None and not np.issubdtype(
                original_dtype, np.floating
            ):
                original_dtype = None
        except TypeError:
            original_dtype = None

        # Convert only the first argument (signal) to torch tensor
        if args:
            # Convert first argument to torch
            converted_first_arg = to_torch(args[0], return_fn=_return_always)[0][0]

            # Keep other arguments as-is
            converted_args = (converted_first_arg,) + args[1:]
        else:
            converted_args = args

        results = func(*converted_args, **kwargs)

        # Convert results back to original input types
        import torch

        def _to_np(t):
            arr = t.detach().cpu().numpy()
            # Restore original numpy dtype when caller used a real ndarray /
            # pandas / xarray with a known floating dtype.
            if original_dtype is not None and arr.dtype != original_dtype:
                arr = arr.astype(original_dtype, copy=False)
            return arr

        if isinstance(results, torch.Tensor):
            if original_object is not None:
                if isinstance(original_object, list):
                    return _to_np(results).tolist()
                elif isinstance(original_object, np.ndarray):
                    return _to_np(results)
                elif (
                    hasattr(original_object, "__class__")
                    and original_object.__class__.__name__ == "DataFrame"
                ):
                    import pandas as pd

                    return pd.DataFrame(_to_np(results))
                elif (
                    hasattr(original_object, "__class__")
                    and original_object.__class__.__name__ == "Series"
                ):
                    import pandas as pd

                    return pd.Series(_to_np(results).flatten())
                elif (
                    hasattr(original_object, "__class__")
                    and original_object.__class__.__name__ == "DataArray"
                ):
                    import xarray as xr

                    return xr.DataArray(_to_np(results))
            return results

        # Handle tuple returns (e.g., (signal, frequencies))
        elif isinstance(results, tuple):
            import torch

            converted_results = []
            for r in results:
                if isinstance(r, torch.Tensor):
                    if original_object is not None and isinstance(
                        original_object, np.ndarray
                    ):
                        converted_results.append(_to_np(r))
                    else:
                        converted_results.append(r)
                else:
                    converted_results.append(r)
            return tuple(converted_results)

        return results

    # Mark as a wrapper for detection
    wrapper._is_wrapper = True
    wrapper._decorator_type = "signal_fn"
    return wrapper


# EOF
