#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 14:58:43 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_converters.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/decorators/_converters.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import functools
import warnings
from typing import Any as _Any
from typing import Callable, Dict, Tuple, Union

import numpy as np

"""
Core conversion utilities for handling data type transformations.
Provides consistent conversion between NumPy, PyTorch, Pandas, and other formats.
"""


class ConversionWarning(UserWarning):
    pass


# Configure warnings
warnings.simplefilter("always", ConversionWarning)


@functools.lru_cache(maxsize=None)
def _cached_warning(message: str) -> None:
    """Cache warnings to avoid repetition."""
    warnings.warn(message, category=ConversionWarning)


def _conversion_warning(old: _Any, new) -> None:
    """Generate standardized type conversion warning."""
    message = (
        f"Converted from {type(old).__name__} to {type(new).__name__} ({new.device}). "
        f"Consider using {type(new).__name__} ({new.device}) as input for faster computation."
    )
    _cached_warning(message)


def _try_device(tensor, device: str):
    """Try to move tensor to specified device with graceful fallback."""
    import torch

    if not isinstance(tensor, torch.Tensor):
        return tensor

    if tensor.device.type == device:
        return tensor

    try:
        return tensor.to(device)
    except RuntimeError as error:
        if "cuda" in str(error).lower() and device == "cuda":
            warnings.warn("CUDA memory insufficient, falling back to CPU.", UserWarning)
            return tensor.cpu()
        raise error


def is_torch(*args: _Any, **kwargs: _Any) -> bool:
    """Check if any input is a PyTorch tensor."""
    import torch

    return any(isinstance(arg, torch.Tensor) for arg in args) or any(
        isinstance(val, torch.Tensor) for val in kwargs.values()
    )


def is_cuda(*args: _Any, **kwargs: _Any) -> bool:
    """Check if any input is a CUDA tensor."""
    import torch

    return any((isinstance(arg, torch.Tensor) and arg.is_cuda) for arg in args) or any(
        (isinstance(val, torch.Tensor) and val.is_cuda) for val in kwargs.values()
    )


def _return_always(*args: _Any, **kwargs: _Any) -> Tuple[Tuple, Dict]:
    """Always return args and kwargs as a tuple of (args, kwargs)."""
    return args, kwargs


def _return_if(*args: _Any, **kwargs: _Any) -> Union[Tuple, Dict, None]:
    """Return args and/or kwargs depending on what's provided."""
    if args and kwargs:
        return args, kwargs
    elif args:
        return args
    elif kwargs:
        return kwargs
    else:
        return None


def to_torch(
    *args: _Any,
    return_fn: Callable = _return_if,
    device: str = None,
    **kwargs: _Any,
) -> _Any:
    """Convert various data types to PyTorch tensors."""
    import torch

    if device is None:
        device = kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")

    def _float_dtype_for(arr: _Any):
        """Pick a torch float dtype that preserves the precision of arr.

        - float64 numpy/pandas/xarray inputs -> torch.float64
        - float16 inputs -> torch.float16
        - float32 / integer / unknown -> torch.float32 (current default)
        """
        import torch

        np_dtype = getattr(arr, "dtype", None)
        if np_dtype is not None:
            try:
                if np.issubdtype(np_dtype, np.floating):
                    if np_dtype == np.float64:
                        return torch.float64
                    if np_dtype == np.float16:
                        return torch.float16
                    return torch.float32
            except TypeError:
                pass
        return torch.float32

    def _to_torch(data: _Any) -> _Any:
        """Internal conversion function for various data types."""
        import pandas as pd
        import torch

        # Check for None
        if data is None:
            return None

        # Don't convert scalars (int, float, bool, str) - they should remain as is
        if isinstance(data, (int, float, bool, str)):
            return data

        # Handle collections
        if isinstance(data, (tuple, list)):
            # Check if it's a tuple/list of integers (like dimensions)
            if all(isinstance(item, int) for item in data):
                return data  # Keep as is for dimension tuples

            # Check if it's a numeric array-like structure
            try:
                # Promote via numpy first so that mixed-precision inputs follow
                # numpy promotion rules (float64 wins over float32, etc.).
                np_view = np.asarray(data)
                target_dtype = _float_dtype_for(np_view)
                new_data = torch.as_tensor(np_view).to(target_dtype)
                new_data = _try_device(new_data, device)
                if device == "cuda":
                    _conversion_warning(data, new_data)
                return new_data
            except:
                # If conversion fails, process items individually and return as tensor if possible
                converted_items = [_to_torch(item) for item in data if item is not None]
                # Try to stack if all items are tensors
                if converted_items and all(
                    isinstance(item, torch.Tensor) for item in converted_items
                ):
                    try:
                        # Stack tensors along a new dimension
                        return torch.stack(converted_items)
                    except:
                        # Return as list if stacking fails
                        return converted_items
                return converted_items

        # Handle pandas types
        if isinstance(data, (pd.Series, pd.DataFrame)):
            np_view = data.to_numpy()
            target_dtype = _float_dtype_for(np_view)
            new_data = torch.as_tensor(np_view).squeeze().to(target_dtype)
            new_data = _try_device(new_data, device)
            if device == "cuda":
                _conversion_warning(data, new_data)
            return new_data

        # Handle arrays
        if isinstance(data, np.ndarray):
            target_dtype = _float_dtype_for(data)
            new_data = torch.as_tensor(data).to(target_dtype)
            new_data = _try_device(new_data, device)
            if device == "cuda":
                _conversion_warning(data, new_data)
            return new_data

        # Handle xarray

        if (
            hasattr(data, "__class__")
            and data.__class__.__module__ == "xarray.core.dataarray"
            and data.__class__.__name__ == "DataArray"
        ):
            np_view = np.array(data)
            target_dtype = _float_dtype_for(np_view)
            new_data = torch.as_tensor(np_view).to(target_dtype)
            new_data = _try_device(new_data, device)
            if device == "cuda":
                _conversion_warning(data, new_data)
            return new_data

        # Return as is for other types
        return data

    # Process args and kwargs
    converted_args = [_to_torch(arg) for arg in args if arg is not None]
    converted_kwargs = {
        key: _to_torch(val) for key, val in kwargs.items() if val is not None
    }

    # Handle axis/dim parameter conversion
    # Only convert axis to dim if dim is not already present
    if "axis" in converted_kwargs and "dim" not in converted_kwargs:
        converted_kwargs["dim"] = converted_kwargs.pop("axis")

    # Return in the specified format
    return return_fn(*converted_args, **converted_kwargs)


def to_numpy(*args: _Any, return_fn: Callable = _return_if, **kwargs: _Any) -> _Any:
    """Convert various data types to NumPy arrays."""

    def _to_numpy(data: _Any) -> _Any:
        """Internal conversion function for various data types."""
        import pandas as pd
        import torch

        # Check for None
        if data is None:
            return None

        # Don't convert scalars (int, float, bool, str) - they should remain as is
        if isinstance(data, (int, float, bool, str)):
            return data

        # Handle pandas types
        if isinstance(data, (pd.Series, pd.DataFrame)):
            return data.to_numpy().squeeze()

        # Handle torch tensors
        if isinstance(data, torch.Tensor):
            return data.detach().cpu().numpy()

        # Handle lists and tuples
        if isinstance(data, (list, tuple)):
            # Check if it's a tuple/list of integers (like dimensions)
            if all(isinstance(item, int) for item in data):
                return data  # Keep as is for dimension tuples

            # Check if it's a numeric array-like structure
            try:
                # Try to convert to numpy array directly
                return np.array(data)
            except:
                # If conversion fails, process items individually
                converted_items = [_to_numpy(item) for item in data if item is not None]
                # Try to stack if all items are numpy arrays
                if converted_items and all(
                    isinstance(item, np.ndarray) for item in converted_items
                ):
                    try:
                        # Stack arrays along a new dimension
                        return np.stack(converted_items)
                    except:
                        # Return as list if stacking fails
                        return converted_items
                return converted_items

        # Return as is for other types
        return data

    # Process args and kwargs
    converted_args = [_to_numpy(arg) for arg in args if arg is not None]
    converted_kwargs = {
        key: _to_numpy(val) for key, val in kwargs.items() if val is not None
    }

    # Handle dim/axis parameter conversion
    # Only convert dim to axis if axis is not already present
    if "dim" in converted_kwargs and "axis" not in converted_kwargs:
        converted_kwargs["axis"] = converted_kwargs.pop("dim")

    # Return in the specified format
    return return_fn(*converted_args, **converted_kwargs)


def is_nested_decorator():
    """Check if we're in a nested decorator context."""
    import inspect

    frame = inspect.currentframe()
    current_decorator = None
    decorator_chain = []

    # Walk up the call stack
    while frame:
        if frame.f_code.co_name == "wrapper":
            # Check if this frame has local variables
            if frame.f_locals:
                # Try to get the self reference if it's a method
                if "self" in frame.f_locals:
                    decorator_chain.append(frame.f_locals["self"])

                # Check if the wrapper has marked itself with decorator info
                if "_current_decorator" in frame.f_locals:
                    decorator_type = frame.f_locals["_current_decorator"]
                    if current_decorator is None:
                        current_decorator = decorator_type
                    elif current_decorator != decorator_type:
                        # Found a different decorator in the chain
                        return True

        frame = frame.f_back

    # If we found more than one decorator in the chain
    return len(decorator_chain) > 1


# EOF
