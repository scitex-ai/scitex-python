---
description: Value replacement (replace), numeric rounding preserving non-numeric columns (round), and sort with optional custom category order (sort).
---

# Data Cleaning

## replace

Replace values in a DataFrame, with optional column scoping and regex support.

```python
replace(dataframe, old_value, new_value=None, regex=False, cols=None) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataframe` | `pd.DataFrame` | required | Input DataFrame (not modified in place) |
| `old_value` | `str` or `dict` | required | Value to replace (with `new_value`), or a mapping `{old: new, …}` |
| `new_value` | `any` | `None` | Replacement value; required when `old_value` is not a dict |
| `regex` | `bool` | `False` | Treat `old_value` keys as regex patterns |
| `cols` | `list[str]` or `None` | `None` | Columns to apply replacement to; `None` applies to all columns |

Always returns a copy; original is unchanged.

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'A': ['abc-123', 'def-456'], 'B': ['ghi-789', 'jkl-012']})

# Single replacement across all columns
stx.pd.replace(df, '-', '_')
#          A        B
# 0  abc_123  ghi_789
# 1  def_456  jkl_012

# Dict-based multi-replacement, column-scoped
stx.pd.replace(df, {'-': '_', 'abc': 'xyz'}, cols=['A'])
#          A        B
# 0  xyz_123  ghi-789
# 1  def_456  jkl-012

# Regex replacement
stx.pd.replace(df, r'\d+', 'NUM', regex=True)
#        A      B
# 0  abc-NUM  ghi-NUM
# 1  def-NUM  jkl-NUM
```

---

## round

Round all numeric columns in a DataFrame to a fixed number of decimal places, leaving non-numeric columns unchanged.

```python
round(df, factor=3) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | required | Input DataFrame |
| `factor` | `int` | `3` | Number of decimal places |

**Column-type handling**

| Column dtype | Behaviour |
|-------------|-----------|
| Datetime | Left unchanged |
| Categorical | Left unchanged |
| String / object (non-numeric) | Left unchanged |
| Boolean | Converted to `int` (0/1) |
| Integer | Left as integer (no float promotion) |
| Float | Rounded to `factor` decimal places |
| `factor=0` and all whole numbers | Converted to `int` |

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({
    'score': [1.23456, 2.34567],
    'label': ['a', 'b'],
    'count': [3, 4],
})

stx.pd.round(df, 2)
#    score label  count
# 0   1.23     a      3
# 1   2.35     b      4

stx.pd.round(df, 0)
#    score label  count
# 0      1     a      3
# 1      2     b      4
```

---

## sort

Sort a DataFrame by one or more columns, with optional custom category ordering. The sort-key columns are moved to the front of the result.

```python
sort(dataframe, by=None, ascending=True, inplace=False, kind="quicksort",
     na_position="last", ignore_index=False, key=None, orders=None) -> pd.DataFrame
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataframe` | `pd.DataFrame` | required | DataFrame to sort |
| `by` | `str` or `list[str]` or `None` | `None` | Column(s) to sort by; when `None` and `orders` is set, uses `orders.keys()` |
| `ascending` | `bool` or `list[bool]` | `True` | Sort direction |
| `inplace` | `bool` | `False` | Update original DataFrame in place (partial — index not updated correctly; prefer `False`) |
| `kind` | `str` | `"quicksort"` | Sorting algorithm passed to pandas |
| `na_position` | `str` | `"last"` | `"first"` or `"last"` for NaN placement |
| `ignore_index` | `bool` | `False` | Reset index to 0, 1, … in output |
| `key` | `callable` or `None` | `None` | Applied to values before sorting (overridden when `orders` is set) |
| `orders` | `dict[str, list]` or `None` | `None` | Custom sort order per column; creates `pd.Categorical` internally |

**Column reordering side-effect:** the columns specified in `by` are moved to the front of the returned DataFrame.

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'A': ['foo', 'bar', 'baz'], 'B': [3, 2, 1]})

# Standard ascending sort
stx.pd.sort(df, by='B')
#      B    A
# 1  1.0  baz
# ...

# Custom category order
custom = {'A': ['bar', 'baz', 'foo']}
stx.pd.sort(df, orders=custom)
#      A  B
# 1  bar  2
# 2  baz  1
# 0  foo  3

# Multi-column sort
stx.pd.sort(df, by=['A', 'B'], ascending=[True, False])
```
