---
name: stx.dict
description: Dictionary utilities including dot-access, flattening, merging, and listed dict factories.
---

# stx.dict

The `stx.dict` module provides utilities for working with Python dictionaries in scientific computing contexts. Key features include dot-notation access, recursive flattening, safe merging, and listed dict patterns.

## Python API

```python
import scitex as stx

# Dot-notation dictionary access
d = stx.dict.DotDict({"model": {"lr": 1e-3, "epochs": 100}})
print(d.model.lr)      # 1e-3
d.model.lr = 5e-4

# Flatten nested dict
flat = stx.dict.flatten({"a": {"b": {"c": 1}}, "d": 2})
# -> {"a.b.c": 1, "d": 2}

# Listed dict (dict of lists)
ld = stx.dict.listed_dict(["loss", "acc"])
ld["loss"].append(0.5)
ld["acc"].append(0.9)

# Pop keys (remove and return values)
values = stx.dict.pop_keys(d, ["key1", "key2"])

# Safe merge (raises on key conflicts)
merged = stx.dict.safe_merge(dict1, dict2)

# Convert to string representation
s = stx.dict.to_str({"a": 1, "b": [1, 2, 3]})

# Replace values matching a pattern
updated = stx.dict.replace(d, old_value=None, new_value=0.0)
```

## Key Features

- `DotDict` — dictionary with dot-notation access (`d.key.subkey`)
- `flatten(d, sep=".")` — recursively flatten nested dict to flat key-value pairs
- `listed_dict(keys)` — create a dict of lists for accumulating values
- `pop_keys(d, keys)` — remove and return multiple keys at once
- `safe_merge(d1, d2)` — merge dicts, raising on duplicate keys
- `to_str(d)` — human-readable string representation
- `replace(d, old, new)` — replace all values matching a pattern
