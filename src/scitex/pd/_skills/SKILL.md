---
name: stx.pd
description: Pandas DataFrame utilities for filtering, reshaping, merging, and scientific data manipulation.
---

# stx.pd

The `stx.pd` module provides utility functions for pandas DataFrames tailored to scientific data analysis workflows. It extends pandas with helpers for indicator-based indexing, p-value column detection, melting, and coordinate-based reshaping.

## Python API

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({"x": [1,2,3], "y": [4,5,6], "p_val": [0.01, 0.05, 0.5]})

# Boolean indicator indexing
indi = stx.pd.find_indi(df, col="group", values=["A", "B"])
subset = df[indi]

# Find p-value columns automatically
p_col = stx.pd.find_pval(df)

# Force to DataFrame
df = stx.pd.force_df(my_array_or_list)

# Coordinate reshaping
df = stx.pd.from_xyz(x_array, y_array, z_matrix)
x, y, z = stx.pd.to_xyz(df)

# Get unique values as list
unique_vals = stx.pd.get_unique(df["group"])

# Melt multiple columns
melted = stx.pd.melt_cols(df, cols=["col1", "col2"], id_vars=["id"])

# Merge columns into one
merged = stx.pd.merge_cols(df, cols=["first", "last"], sep="_")

# Column reordering
df = stx.pd.mv(df, col="important_col", position=0)
df = stx.pd.mv_to_first(df, "id")
df = stx.pd.mv_to_last(df, "notes")

# Type utilities
df = stx.pd.to_numeric(df, cols=["value"])

# Suppress SettingWithCopyWarning
with stx.pd.ignore_SettingWithCopyWarning():
    df["new_col"] = df["old_col"] * 2
```

## Key Features

- `find_indi(df, col, values)` — boolean index for filtering rows
- `find_pval(df)` — auto-detect p-value column name
- `force_df(obj)` — coerce arrays/dicts/lists to DataFrame
- `from_xyz` / `to_xyz` — convert between XYZ arrays and pivot tables
- `melt_cols` / `merge_cols` / `mv` — DataFrame reshaping and column management
- `ignore_SettingWithCopyWarning` — context manager for pandas warning suppression
- `to_numeric` / `round` / `slice` / `sort` / `replace` — common data operations
