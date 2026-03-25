---
description: ArrayLike and ColorLike type annotations, is_array_like() runtime check, and is_listed_X()/is_list_of_type() homogeneous list guards.
---

# stx.types — Type Aliases and Runtime Guards

## ArrayLike

Union type covering numpy arrays, pandas Series/DataFrame, lists, tuples, and optionally xarray DataArrays and torch Tensors.

```python
from scitex.types import ArrayLike

def process(data: ArrayLike) -> None:
    ...
```

Full definition (with xarray installed):
```
Union[list, tuple, np.ndarray, pd.Series, pd.DataFrame, xr.DataArray]
```

Without xarray: same minus `xr.DataArray`. PyTorch tensors are checked dynamically in `is_array_like()` but are not in the static Union due to optional dependency.

## ColorLike

Type alias for any matplotlib-compatible color specification.

```python
from scitex.types import ColorLike

def plot(color: ColorLike) -> None:
    ...

# Valid values:
# "red", "#FF0000", (1.0, 0.0, 0.0), (1.0, 0.0, 0.0, 1.0), [0.5, 0.5, 0.5]
```

Definition: `Union[str, Tuple[float, float, float], Tuple[float, float, float, float], List[float]]`

## is_array_like

Runtime check covering all ArrayLike types plus torch tensors.

```python
from scitex.types import is_array_like
import numpy as np
import torch

is_array_like(np.array([1, 2]))   # True
is_array_like(torch.tensor([1]))  # True
is_array_like([1, 2, 3])          # True
is_array_like((1, 2))             # True
is_array_like("hello")            # False
is_array_like(42)                 # False
```

Torch is detected via `torch.is_tensor()` with a lazy import, so it works even if torch is installed but has circular import issues.

## is_listed_X / is_list_of_type

Check that an object is a `list` and that every element belongs to the specified type(s).

```python
from scitex.types import is_listed_X, is_list_of_type

is_listed_X([1, 2, 3], int)          # True
is_listed_X([1.0, 2.0], float)       # True
is_listed_X([1, 2.0], (int, float))  # True  — multi-type
is_listed_X(["a", "b"], str)         # True
is_listed_X([1, "a"], int)           # False — mixed types
is_listed_X((1, 2), int)             # False — tuple, not list

is_list_of_type([1, 2], int)         # True — alias for is_listed_X
```

Returns `False` (not raises) on any exception during type checking.
