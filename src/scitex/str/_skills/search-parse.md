---
description: Pattern search in string lists (grep, search), bidirectional f-string parsing (parse), and template-based placeholder replacement (replace).
---

# Search and Parsing

---

## grep

Search for a regex pattern in a list of strings. Returns matching indices and values.

```python
grep(str_list: list, search_key: str) -> Tuple[List[int], List[str]]
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `str_list` | `list[str]` | List of strings to search |
| `search_key` | `str` | Regex pattern (passed to `re.search`) |

**Returns** `(indices, matched_strings)` — both lists are in the original order.

**Examples**

```python
import scitex as stx

stx.str.grep(['apple', 'banana', 'cherry'], 'a')
# ([0, 1], ['apple', 'banana'])

stx.str.grep(['apple', 'orange', 'apple_juice', 'banana', 'orange_juice'], 'orange')
# ([1, 4], ['orange', 'orange_juice'])

stx.str.grep(['cat', 'dog', 'elephant'], 'e')
# ([2], ['elephant'])
```

Note: `search_key` is used as a regex, so special regex characters must be escaped if literal matching is needed.

---

## search

Extended pattern search supporting multiple patterns, boolean output, exact-match mode, and natural-sort ordering of results.

```python
search(
    patterns,
    strings,
    only_perfect_match: bool = False,
    as_bool: bool = False,
    ensure_one: bool = False,
) -> Tuple[Union[List[int], np.ndarray], List[str]]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `patterns` | str / list / ndarray / Series | required | One or more patterns to search for |
| `strings` | str / list / ndarray / Series / pd.Index | required | Pool of strings to search in |
| `only_perfect_match` | `bool` | `False` | Require exact equality (`==`) instead of `re.search` |
| `as_bool` | `bool` | `False` | Return `np.ndarray[bool]` for indices instead of `List[int]` |
| `ensure_one` | `bool` | `False` | Assert exactly one match; raises `AssertionError` otherwise |

**Returns** `(indices_or_bool, matched_strings)`

- Indices are de-duplicated and sorted with `natsort.natsorted`.
- Accepts `np.ndarray`, `pd.Series`, `xr.DataArray`, `dict_keys`, `list`, `tuple`, `pd.Index` for both `patterns` and `strings`.

**Examples**

```python
import scitex as stx

strings = ['apple', 'orange', 'apple_juice', 'banana', 'orange_juice']

# Single pattern
stx.str.search('orange', strings)
# ([1, 4], ['orange', 'orange_juice'])

# Multiple patterns
stx.str.search(['orange', 'banana'], strings)
# ([1, 3, 4], ['orange', 'banana', 'orange_juice'])

# Boolean output
mask, matched = stx.str.search('orange', strings, as_bool=True)
# mask: array([False,  True, False, False,  True])

# Exact match only
stx.str.search('orange', strings, only_perfect_match=True)
# ([1], ['orange'])

# Assert single result
stx.str.search('banana', strings, ensure_one=True)
# ([3], ['banana'])
```

---

## parse

Bidirectional f-string parser — extracts named variables from a path or string given a pattern, or vice versa.

```python
parse(
    string_or_fstring: str,
    fstring_or_string: str,
) -> DotDict[str, Union[str, int]]
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `string_or_fstring` | `str` | Either the concrete string or the pattern |
| `fstring_or_string` | `str` | Either the pattern or the concrete string |

**Returns** `DotDict` (dot-accessible dict) mapping placeholder names to extracted values.

**Behavior**

- Tries parsing in both directions automatically; raises `ValueError` only if both fail.
- Integer-looking captured values are converted to `int`.
- Duplicate placeholders with inconsistent values raise `ValueError`.
- Format specifiers in patterns (e.g. `{id:03d}`) are stripped before matching.
- Pattern strings optionally wrapped in `"..."` or `f"..."` quotes are unwrapped.

**Placeholders** use `{name}` syntax; each captures `[^/]+` (everything up to the next `/`).

**Examples**

```python
import scitex as stx

# Forward: string then pattern
result = stx.str.parse(
    "./data/Patient_23_002",
    "./data/Patient_{id}"
)
# {'id': '23_002'}
result.id   # '23_002'  (DotDict attribute access)

# Works in reverse too (pattern then string)
result = stx.str.parse(
    "./data/Patient_{id}",
    "./data/Patient_23_002"
)
# {'id': '23_002'}

# Multiple placeholders
result = stx.str.parse(
    "./data/Patient_042/Data_2024_01_15",
    "./data/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}"
)
# {'patient_id': 42, 'YYYY': 2024, 'MM': 1, 'DD': 15}

# Inconsistent duplicate raises ValueError
# "./data/Patient_042/Hour_042" vs "./data/Patient_{id}/Hour_{id}"
# → ValueError: Inconsistent values for placeholder 'id'
```

---

## replace

Replace `{key}` placeholders in a template string using a dictionary.

```python
replace(
    string: str,
    replacements: Optional[Union[str, Dict[str, str]]] = None,
) -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `string` | `str` | required | Template string with `{key}` placeholders |
| `replacements` | `str` / `dict` / `None` | `None` | Replacement values; if a plain `str`, returns that string directly; if `None`, returns `string` unchanged |

**Raises** `TypeError` if `string` is not a `str`, or if `replacements` is not a `str`, `dict`, `DotDict`, or `None`.

**Examples**

```python
import scitex as stx

stx.str.replace("Hello, {name}!", {"name": "World"})
# 'Hello, World!'

stx.str.replace("Original string", "New string")
# 'New string'    (replacements is a str → returned directly)

stx.str.replace("Value: {x}", {"x": "42"})
# 'Value: 42'

stx.str.replace("Hello, {name}! You are {age} years old.", {"name": "Alice", "age": "30"})
# 'Hello, Alice! You are 30 years old.'

stx.str.replace("No placeholders here", None)
# 'No placeholders here'

# DotDict input works too (from stx.str.parse output)
result = stx.str.parse("./data/run_007", "./data/run_{run_id}")
stx.str.replace("Results from run {run_id}", result)
# 'Results from run 007'
```
