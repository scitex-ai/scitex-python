---
name: pd-conversion
description: Convert arbitrary Python objects to DataFrames (force_df) and coerce columns to numeric types (to_numeric).
---

# Data Conversion

## force_df

Converts virtually any Python object into a `pd.DataFrame`. Returns the input unchanged if it is already a DataFrame. Handles `None` as an empty DataFrame.

```python
force_df(data, filler=np.nan) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | any | required | Object to convert |
| `filler` | any | `np.nan` | Fill value for missing entries when building from an uneven dict |

**Input type handling**

| Input type | Behaviour |
|------------|-----------|
| `None` | Returns `pd.DataFrame()` |
| `pd.DataFrame` | Returned as-is (no copy) |
| `pd.Series` | `.to_frame()` |
| `np.ndarray` 1-D | Single column named `"value"` |
| `np.ndarray` 2-D | Columns 0, 1, 2, … |
| `np.ndarray` N-D | Reshaped to `(shape[0], -1)` |
| `int`, `float`, `str`, `bool` | Single row, column named `"value"` |
| `list` / `tuple` of scalars | Single column named `"value"` |
| `list` of `list`/`tuple`/`ndarray` | Multi-column DataFrame |
| `dict` | Columns from keys; unequal lengths padded with `filler` |
| Other iterable | `pd.DataFrame(list(data), columns=["value"])` |

**Examples**

```python
import scitex as stx
import numpy as np
import pandas as pd

# Scalar
stx.pd.force_df(42)
#    value
# 0     42

# 1-D array
stx.pd.force_df(np.array([1, 2, 3]))
#    value
# 0      1
# 1      2
# 2      3

# Uneven dict — short column padded with NaN
stx.pd.force_df({'A': [1, 2, 3], 'B': [4, 5]})
#    A    B
# 0  1  4.0
# 1  2  5.0
# 2  3  NaN

# DataFrame is returned unchanged
df = pd.DataFrame({'x': [1]})
assert stx.pd.force_df(df) is df
```

---

## to_numeric

Attempts to convert every column in a DataFrame to a numeric dtype. Non-convertible columns are handled according to the `errors` parameter.

```python
to_numeric(df, errors="coerce") -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | required | Input DataFrame |
| `errors` | `str` | `"coerce"` | `"coerce"` → invalid values become `NaN`; `"ignore"` → non-numeric columns kept unchanged; `"raise"` → raises on invalid values |

**Behaviour detail**

- Operates on a copy; never modifies the original.
- A column that converts entirely to `NaN` while the original had values is treated as a pure-string column:
  - `errors="ignore"` keeps it as-is.
  - `errors="coerce"` still replaces it with all-`NaN`.
- Integer columns are left as integers; no float promotion occurs for already-integer data.

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'a': ['1', '2', '3'], 'b': ['x', 'y', 'z'], 'c': [1.1, 2.2, 3.3]})

# Default: coerce — 'b' becomes NaN
stx.pd.to_numeric(df)
#      a    b    c
# 0  1.0  NaN  1.1
# 1  2.0  NaN  2.2
# 2  3.0  NaN  3.3

# ignore — pure string column 'b' kept
stx.pd.to_numeric(df, errors="ignore")
#    a  b    c
# 0  1  x  1.1
# 1  2  y  2.2
# 2  3  z  3.3
```
