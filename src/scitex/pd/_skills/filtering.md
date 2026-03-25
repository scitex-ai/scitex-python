---
description: Row selection with multi-column conditions including NaN-safe matching (find_indi) and combined row/column slicing (slice).
---

# Filtering and Slicing

## find_indi

Find row indices where all given column conditions are satisfied simultaneously. Handles `NaN` / `None` / `pd.NA` values in both the DataFrame and the condition values.

```python
find_indi(df, conditions) -> list[int]
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | Input DataFrame |
| `conditions` | `dict[str, str | int | float | list]` | Mapping of column names to required values. A list value uses `isin`; a scalar uses `==`. `NaN`/`None` in the list or as a scalar value matches `NaN` rows. |

**Returns** a plain Python `list` of integer positional indices (`.tolist()` of the boolean mask index).

**Raises** `KeyError` if any key in `conditions` is not a column of `df`.

Returns `[]` for an empty `conditions` dict.

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3, 1], 'B': ['x', 'y', 'x', 'z']})

# Single-value condition
stx.pd.find_indi(df, {'B': 'x'})
# [0, 2]

# List condition (isin)
stx.pd.find_indi(df, {'A': [1, 2]})
# [0, 1, 3]

# Combined conditions (AND logic)
stx.pd.find_indi(df, {'A': [1, 2], 'B': 'x'})
# [0]

# NaN matching
df2 = pd.DataFrame({'A': [1, None, 3], 'B': ['x', 'x', 'y']})
stx.pd.find_indi(df2, {'A': [1, None], 'B': 'x'})
# [0, 1]  ← row with None matches because None is in the list
```

---

## slice

Slice rows and/or columns from a DataFrame in one call. Combines index-based slicing, condition-based row selection, and column selection.

```python
slice(df, conditions=None, columns=None) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | required | Input DataFrame |
| `conditions` | `builtins.slice`, `dict`, or `None` | `None` | `slice` object → `iloc`-based row slicing; `dict` → passed to `find_indi` for condition-based row selection; `None` → no row filtering |
| `columns` | `list[str]` or `None` | `None` | Columns to keep; applied after row filtering |

Always returns a copy; the original DataFrame is not modified.

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': ['x', 'y', 'x', 'y'], 'C': [10, 20, 30, 40]})

# Slice first two rows by position
stx.pd.slice(df, slice(0, 2))
#    A  B   C
# 0  1  x  10
# 1  2  y  20

# Slice by condition
stx.pd.slice(df, {'B': 'x'})
#    A  B   C
# 0  1  x  10
# 2  3  x  30

# Condition + column selection
stx.pd.slice(df, {'B': 'y'}, columns=['A', 'C'])
#    A   C
# 1  2  20
# 3  4  40

# Column selection only (no row filtering)
stx.pd.slice(df, columns=['A', 'B'])
#    A  B
# 0  1  x
# 1  2  y
# 2  3  x
# 3  4  y
```

**Relationship to find_indi**

`slice` internally delegates condition-based row selection to `find_indi`, so all NaN-safe matching rules described there apply here too.
