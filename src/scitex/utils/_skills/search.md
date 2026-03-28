---
description: Regex-based multi-pattern search over a list of strings, returning matched indices and values.
---

# stx.utils.search

Search one or more regex patterns over a collection of strings. Returns matched indices and matched values, with optional boolean-array output and an exactness toggle.

## Signature

```python
search(
    patterns: str | list[str] | np.ndarray | pd.Series | pd.Index,
    strings:  str | list[str] | np.ndarray | pd.Series | pd.Index,
    only_perfect_match: bool = False,
    as_bool: bool = False,
    ensure_one: bool = False,
) -> tuple[list[int] | np.ndarray, list[str]]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `patterns` | str or sequence | required | Pattern(s) to search for. Standard Python regex syntax. |
| `strings` | str or sequence | required | Strings to search in. Accepts str, list, ndarray, pd.Series, pd.Index. |
| `only_perfect_match` | bool | False | If True, require exact string equality instead of `re.search` |
| `as_bool` | bool | False | If True, return a boolean ndarray instead of an index list |
| `ensure_one` | bool | False | If True, raise AssertionError unless exactly one match is found |

### Returns

A 2-tuple `(indices_or_bool, matched_strings)`:

- When `as_bool=False` (default): `(list[int], list[str])` — indices are naturally sorted via `natsorted`.
- When `as_bool=True`: `(np.ndarray[bool], list[str])` — length equals `len(strings)`.

## Behaviour details

- Multiple patterns are OR-combined: a string is included if it matches any pattern.
- `re.search` is used (substring match), so `"orange"` matches `"orange_juice"`.
- Input sequences are normalised internally — numpy arrays, pandas Series/Index, and dict key-views all work.
- Returned indices are deduplicated and sorted with `natsort` for natural ordering.

## Examples

### Single pattern

```python
import scitex as stx

strings = ["apple", "orange", "apple_juice", "banana", "orange_juice"]

idx, matched = stx.utils.search("orange", strings)
# idx     -> [1, 4]
# matched -> ["orange", "orange_juice"]
```

### Multiple patterns

```python
idx, matched = stx.utils.search(["orange", "banana"], strings)
# idx     -> [1, 3, 4]
# matched -> ["orange", "banana", "orange_juice"]
```

### Boolean output

```python
mask, matched = stx.utils.search("orange", strings, as_bool=True)
# mask -> array([False, True, False, False, True])
filtered = [s for s, m in zip(strings, mask) if m]
```

### Exact match only

```python
idx, matched = stx.utils.search("orange", strings, only_perfect_match=True)
# idx     -> [1]
# matched -> ["orange"]    (orange_juice excluded)
```

### Enforce single match

```python
# Useful when you expect exactly one result
idx, matched = stx.utils.search("^banana$", strings, ensure_one=True)
# Raises AssertionError if 0 or 2+ matches
```

### Searching pandas columns

```python
import pandas as pd

df = pd.DataFrame({"ch": ["Fz", "Cz", "Pz", "Fp1", "Fp2"]})
idx, matched = stx.utils.search("^F", df["ch"])
# idx     -> [0, 3, 4]
# matched -> ["Fz", "Fp1", "Fp2"]
```

### Searching numpy arrays

```python
import numpy as np

labels = np.array(["train_loss", "val_loss", "train_acc", "val_acc"])
idx, matched = stx.utils.search("val", labels)
# idx     -> [1, 3]
# matched -> ["val_loss", "val_acc"]
```
