---
name: pd-shape
description: Convert between wide matrix format and long (x, y, z) row format using to_xyz, from_xyz, and to_xy.
---

# Shape Transformation

Three functions form a complementary trio for switching between wide (pivot/heatmap) and long (triplet) DataFrame layouts.

## to_xyz

Converts a wide DataFrame (matrix / heatmap layout) to long format. Each cell becomes one row with columns `x` (row index), `y` (column name), and `z` (value).

```python
to_xyz(data_frame) -> pd.DataFrame
```

The output column names inherit from `data_frame.index.name` (→ `x` axis) and `data_frame.columns.name` (→ `y` axis). If those names are `None`, `"x"` and `"y"` are used.

**Example**

```python
import scitex as stx
import pandas as pd

wide = pd.DataFrame(
    {'col_A': [1, 2], 'col_B': [3, 4]},
    index=['row_0', 'row_1']
)
long = stx.pd.to_xyz(wide)
#        x      y  z
# 0  row_0  col_A  1
# 1  row_1  col_A  2
# 2  row_0  col_B  3
# 3  row_1  col_B  4
```

---

## from_xyz

Converts a long-format DataFrame (triplets) back to a wide pivot table (heatmap layout). This is the inverse of `to_xyz`.

```python
from_xyz(data_frame, x=None, y=None, z=None, square=False) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_frame` | `pd.DataFrame` | required | Long-format input with x, y, z columns |
| `x` | `str` | `"x"` | Column used as pivot columns axis |
| `y` | `str` | `"y"` | Column used as pivot index axis |
| `z` | `str` | `"z"` | Column used as values |
| `square` | `bool` | `False` | If `True`, forces a square output by unioning index and column labels; missing cells are filled with `0` |

Missing cells are filled with `0` via `fillna(0)`. When multiple rows share the same (x, y) pair the first occurrence wins (`aggfunc="first"`).

**Example**

```python
import scitex as stx
import pandas as pd

long = pd.DataFrame({
    'x': ['A', 'B', 'A'],
    'y': ['X', 'X', 'Y'],
    'z': [0.01, 0.05, 0.1]
})
wide = stx.pd.from_xyz(long)
# y     A     B
# x
# X  0.01  0.05
# Y  0.10  0.00   ← missing cell filled with 0

# Square output (union of A, B and X, Y labels):
stx.pd.from_xyz(long, square=True)
```

**Custom column names**

```python
df = pd.DataFrame({'row': ['r1', 'r2'], 'col': ['c1', 'c1'], 'val': [10, 20]})
stx.pd.from_xyz(df, x='col', y='row', z='val')
```

---

## to_xy

Converts a *square* wide DataFrame to long format. Behaves similarly to `to_xyz` but requires the DataFrame to be square (`shape[0] == shape[1]`) and reconciles mismatched index/column labels before expanding.

```python
to_xy(data_frame) -> pd.DataFrame
```

**Constraint:** input must be square. If index and columns differ, one must be a default integer range — that range is replaced by the other.

**Output columns:** `["x", "y", "z"]`

**Example**

```python
import scitex as stx
import pandas as pd
import numpy as np

square = pd.DataFrame(
    np.array([[1, 2], [3, 4]]),
    index=['A', 'B'],
    columns=['A', 'B']
)
result = stx.pd.to_xy(square)
#    x  y  z
# 0  A  A  1
# 1  B  A  3
# 2  A  B  2
# 3  B  B  4
```

---

## Workflow: round-trip

```python
import scitex as stx

# Start from wide
wide = stx.pd.from_xyz(long_df)          # long → wide
long_again = stx.pd.to_xyz(wide)         # wide → long

# For symmetric matrices use to_xy instead of to_xyz
```
