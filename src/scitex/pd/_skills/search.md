---
name: pd-search
description: Locate p-value columns by name pattern (find_pval) and extract a scalar from a column that should be constant (get_unique).
---

# Value Search

## find_pval

Identify which columns (or dict keys) hold p-values by matching names against the pattern `p[-_]?val(ue)?` (case-insensitive). Names containing `"stars"` are excluded so significance-star columns are not confused with raw p-values.

```python
find_pval(data, multiple=True) -> str | list[str] | None
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `pd.DataFrame`, `np.ndarray`, `list`, or `dict` | required | Data structure to inspect |
| `multiple` | `bool` | `True` | `True` → return all matching names as a list; `False` → return only the first match as a string (or `None`) |

**Dispatch behaviour**

- `pd.DataFrame` → scans `df.columns`
- `dict` → scans dict keys
- `list` / `np.ndarray` whose first element is a `dict` → scans that dict's keys
- Other types → raises `ValueError`

**Internal helper** `_find_pval_col(df, multiple=False)` is also exported for direct DataFrame use.

**Examples**

```python
import scitex as stx
import pandas as pd

df = pd.DataFrame({'p_value': [0.05], 'pval': [0.01], 'p_stars': ['*'], 'other': [1]})

# All matches
stx.pd.find_pval(df)
# ['p_value', 'pval']   ← 'p_stars' is excluded by the (?!.*stars) negative lookahead

# First match only
stx.pd.find_pval(df, multiple=False)
# 'p_value'

# Dict input
d = {'pvalue': 0.05, 'effect_size': 0.3}
stx.pd.find_pval(d)
# ['pvalue']

# Typical workflow: find column, then apply correction
col = stx.pd.find_pval(results_df, multiple=False)
if col:
    corrected = results_df[col] * len(results_df)  # Bonferroni
```

---

## get_unique

Return the single unique value from a column, or a default value when the column is missing or contains more than one distinct value. Useful when a grouped DataFrame is expected to have a constant metadata column (e.g. subject ID, session label).

```python
get_unique(df, column, default=None, raise_on_multiple=False) -> any
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | required | DataFrame to inspect |
| `column` | `str` | required | Column name to check |
| `default` | `any` | `None` | Value returned when the column is absent or has multiple unique values |
| `raise_on_multiple` | `bool` | `False` | If `True`, raises `ValueError` when > 1 unique value exists; raises `KeyError` for missing column |

**Logic**

1. Column absent → return `default` (or raise `KeyError` if `raise_on_multiple=True`)
2. Exactly one unique value → return it
3. Multiple unique values → return `default` (or raise `ValueError` if `raise_on_multiple=True`)

The error message for multiple values includes the first five unique values for debugging.

**Examples**

```python
import scitex as stx
import pandas as pd

# Constant column — returns the single value
df = pd.DataFrame({'subject': ['S01', 'S01', 'S01'], 'value': [1, 2, 3]})
stx.pd.get_unique(df, 'subject')
# 'S01'

# Mixed column — returns default
df2 = pd.DataFrame({'subject': ['S01', 'S02'], 'value': [1, 2]})
stx.pd.get_unique(df2, 'subject', default='mixed')
# 'mixed'

# Missing column
stx.pd.get_unique(df, 'session', default='unknown')
# 'unknown'

# Strict mode
stx.pd.get_unique(df2, 'subject', raise_on_multiple=True)
# ValueError: Column 'subject' has 2 unique values: ['S01', 'S02']

# Typical per-group metadata extraction
for _, group in df.groupby('subject'):
    subject_id = stx.pd.get_unique(group, 'subject', raise_on_multiple=True)
    process(subject_id, group)
```
