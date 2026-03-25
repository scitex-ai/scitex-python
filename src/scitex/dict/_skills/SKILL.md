---
name: stx.dict
description: Dictionary utilities — dot-access DotDict, flattening, safe merging, listed dict, and value replacement.
---

# stx.dict

The `stx.dict` module provides utilities for working with Python dictionaries in scientific computing contexts.

## Sub-skills

- [dotdict.md](dotdict.md) — `DotDict` class: attribute-style access, standard dict methods, serialization, tab completion
- [dict-utilities.md](dict-utilities.md) — `flatten`, `listed_dict`, `safe_merge`, `pop_keys`, `replace`, `to_str`

## Quick Reference

```python
import scitex as stx

# Dot-notation dictionary access
d = stx.dict.DotDict({"model": {"lr": 1e-3, "epochs": 100}})
print(d.model.lr)      # 1e-3
d.model.lr = 5e-4
plain = d.to_dict()

# Flatten nested dict
flat = stx.dict.flatten({"a": {"b": {"c": 1}}})
# {"a_b_c": 1}

# Accumulate values by key
ld = stx.dict.listed_dict(["loss", "acc"])
ld["loss"].append(0.5)

# Safe merge (raises on conflicts)
merged = stx.dict.safe_merge(dict1, dict2)

# Remove keys from a list
remaining = stx.dict.pop_keys(["a", "b", "c"], ["b"])
# ["a", "c"]
```

## Exports

| Name | Type | Description |
|------|------|-------------|
| `DotDict` | class | Dict with attribute access and recursive nesting |
| `flatten` | function | Flatten nested dict with separator joining |
| `listed_dict` | function | `defaultdict(list)` with optional pre-defined keys |
| `pop_keys` | function | Filter a list of keys |
| `safe_merge` | function | Merge dicts, raising on key conflicts |
| `to_str` | function | Human-readable string representation |
| `replace` | function | Replace values matching a pattern |
