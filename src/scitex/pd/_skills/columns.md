---
description: Column reordering (mv, mv_to_first, mv_to_last), column concatenation into a label string (merge_columns / merge_cols), and column melting (melt_cols).
---

# Column Operations

## mv / mv_to_first / mv_to_last

Move a column (or row) to any position within a DataFrame without altering data.

```python
mv(df, key, position, axis=1) -> pd.DataFrame
mv_to_first(df, key, axis=1) -> pd.DataFrame
mv_to_last(df, key, axis=1) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | required | Input DataFrame |
| `key` | `str` | required | Column or row label to move |
| `position` | `int` | required | Target 0-based position; negative indices are resolved relative to the final length |
| `axis` | `int` | `1` | `1` = columns (default), `0` = rows |

`mv_to_first` is shorthand for `mv(df, key, 0)`.
`mv_to_last` is shorthand for `mv(df, key, -1)`.

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3], 'D': [4]})

# Move 'C' to position 1
stx.pd.mv(df, 'C', 1).columns.tolist()
# ['A', 'C', 'B', 'D']

# Bring 'D' to front
stx.pd.mv_to_first(df, 'D').columns.tolist()
# ['D', 'A', 'B', 'C']

# Send 'A' to back
stx.pd.mv_to_last(df, 'A').columns.tolist()
# ['B', 'C', 'D', 'A']

# Move a row (axis=0)
df2 = pd.DataFrame({'val': [10, 20, 30]}, index=['a', 'b', 'c'])
stx.pd.mv(df2, 'c', 0, axis=0).index.tolist()
# ['c', 'a', 'b']
```

---

## merge_columns / merge_cols

Create a new string column by combining the values of existing columns. Two modes are available: plain value concatenation (with `sep`) or labelled concatenation (with `sep1`/`sep2`).

`merge_cols` is an alias for `merge_columns`.

```python
merge_columns(df, *args, sep=None, sep1="_", sep2="-", name="merged") -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | required | Input DataFrame |
| `*args` | `str` or `list`/`tuple` of `str` | required | Column names to combine; may be given as positional arguments or a single list/tuple |
| `sep` | `str` | `None` | When provided: simple value-only concatenation with this separator; new column is named `"A_B"` (joined column names) |
| `sep1` | `str` | `"_"` | Separator between `col-value` pairs when `sep=None` |
| `sep2` | `str` | `"-"` | Separator between column name and its value when `sep=None` |
| `name` | `str` | `"merged"` | Explicit name for the new column (overrides auto-naming when `sep` is set) |

**Output column naming**

- `sep` provided + `name` left at default `"merged"` → new column is `"_".join(columns)` (e.g. `"A_B"`)
- `sep` provided + `name` given explicitly → uses that name
- `sep=None` → uses `name` (default `"merged"`)

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'A': [0, 5], 'B': [1, 6], 'C': [2, 7]})

# Plain concatenation — new column named 'A_B'
stx.pd.merge_columns(df, 'A', 'B', sep=' ')
#    A  B  C  A_B
# 0  0  1  2  0 1
# 1  5  6  7  5 6

# Labelled concatenation (default) — new column named 'merged'
stx.pd.merge_columns(df, 'A', 'B')
#    A  B  C     merged
# 0  0  1  2    A-0_B-1
# 1  5  6  7    A-5_B-6

# Pass columns as a list
stx.pd.merge_columns(df, ['A', 'B', 'C'], sep='-')
#    A  B  C  A_B_C
# 0  0  1  2  0-1-2
# 1  5  6  7  5-6-7

# Alias
stx.pd.merge_cols(df, 'A', 'C', sep='|')
```

---

## melt_cols

Melt a selected subset of columns while preserving all other identifier columns (long-format expansion).

```python
melt_cols(df, cols, id_columns=None) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | required | Input DataFrame |
| `cols` | `list[str]` | required | Columns to melt (become `variable` / `value` rows) |
| `id_columns` | `list[str]` or `None` | `None` | Columns to keep as identifiers; defaults to all columns not in `cols` |

The output contains:
- All `id_columns` repeated for each melted column
- A `variable` column with the original column name
- A `value` column with the cell value (renamed `melted_value` if `"value"` is one of the melted columns)

**Example**

```python
import scitex as stx
import pandas as pd

data = pd.DataFrame({
    'id': [1, 2],
    'name': ['Alice', 'Bob'],
    'score_1': [85, 90],
    'score_2': [92, 88],
})

result = stx.pd.melt_cols(data, cols=['score_1', 'score_2'])
#    id   name variable  value
# 0   1  Alice  score_1     85
# 1   2    Bob  score_1     90
# 2   1  Alice  score_2     92
# 3   2    Bob  score_2     88

# Restrict identifiers explicitly
result2 = stx.pd.melt_cols(data, cols=['score_1', 'score_2'], id_columns=['id'])
#    id variable  value
# 0   1  score_1     85
# ...
```

**Error handling**

Raises `ValueError` if any column in `cols` is not present in `df`.
