---
description: Variable inspection utilities in stx.gen — var_info for type/shape introspection, the ArrayLike type alias, and describe for summary statistics on DataFrames.
---

# Data Inspection

---

## var_info

Returns a dictionary with type and structural information about any variable.

```python
var_info(variable: Any) -> dict
```

> **Note:** Requires `torch`, `xarray`. Returns `None` when torch is not installed (imported from `_type.py` or `_var_info.py`).

**Returned keys** (depending on input type):

| Key | Condition | Description |
|-----|-----------|-------------|
| `"type"` | always | `type(variable).__name__` |
| `"length"` | `hasattr(variable, "__len__")` | `len(variable)` |
| `"shape"` | ndarray, DataFrame, Series, DataArray, Tensor | `.shape` tuple |
| `"dimensions"` | same as above, or nested list | number of dimensions |

For nested lists, the shape and depth are inferred by traversing `variable[0]` recursively.

```python
import numpy as np
import scitex as stx

data = np.array([[1, 2], [3, 4]])
stx.gen.var_info(data)
# {'type': 'ndarray', 'length': 2, 'shape': (2, 2), 'dimensions': 2}

stx.gen.var_info(42)
# {'type': 'int'}

stx.gen.var_info([1, 2, 3])
# {'type': 'list', 'length': 3}

stx.gen.var_info([[1, 2], [3, 4]])
# {'type': 'list', 'length': 2, 'shape': (2, 2), 'dimensions': 2}
```

---

## ArrayLike

A `typing.Union` type alias grouping all common array-like types.

```python
from scitex.gen import ArrayLike

# Equivalent to:
# Union[list, tuple, np.ndarray, pd.Series, pd.DataFrame, xr.DataArray, torch.Tensor]
```

Use in function annotations to accept any numeric container:

```python
def process(data: ArrayLike) -> np.ndarray:
    ...
```

> **Note:** Defined in both `_type.py` and `_var_info.py`; the import in `__init__.py` tries `_type.py` first, then `_var_info.py`.

---

## describe

Computes summary statistics for a DataFrame or array.

```python
describe(df, method="mean_std", round_factor=3, axis=0) -> dict
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `df` | required | `pd.DataFrame` or array-like (coerced with `pd.DataFrame(df)`) |
| `method` | `"mean_std"` | One of `"mean_std"`, `"mean_ci"`, `"median_iqr"` |
| `round_factor` | `3` | Decimal places for rounding |
| `axis` | `0` | Axis along which to compute |

**Return value by method:**

| `method` | Keys returned |
|----------|--------------|
| `"mean_std"` | `{"n", "mean", "std"}` |
| `"mean_ci"` | `{"n", "mean", "ci"}` where `ci = 1.96 * std / sqrt(n)` |
| `"median_iqr"` | `{"n", "median", "iqr"}` |

NaN values are silently excluded from computations (`nanmean`, `nanstd`, `notna().sum()`).

```python
import pandas as pd
import scitex as stx

data = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [10, 20, 30, 40, 50]})

stx.gen.describe(data, method="mean_std")
# {'n': A    5\nB    5, 'mean': A     3.0\nB    30.0, 'std': ...}

stx.gen.describe(data, method="mean_ci")
# {'n': ..., 'mean': ..., 'ci': ...}

stx.gen.describe(data, method="median_iqr")
# {'n': ..., 'median': ..., 'iqr': ...}
```

> **Note:** `describe` is in `misc.py` but not currently listed in `__all__`. Access via `stx.gen.describe` or import directly from `scitex.gen.misc`.
