# Dictionary Utilities (stx.dict)

Utility functions for common dictionary operations in scientific computing workflows.

## flatten

Recursively flatten a nested dict to a flat key-value dict, joining keys with a separator:

```python
from scitex.dict import flatten

nested = {"a": {"b": {"c": 1}}, "d": 2}
flat = flatten(nested, sep="_")
# {"a_b_c": 1, "d": 2}

# Lists and tuples are indexed
nested2 = {"x": [10, 20, 30]}
flat2 = flatten(nested2)
# {"x_0": 10, "x_1": 20, "x_2": 30}

# Custom separator
flat3 = flatten({"outer": {"inner": 42}}, sep=".")
# {"outer.inner": 42}
```

## listed_dict

Create a `defaultdict(list)` pre-initialized with given keys — useful for accumulating values in a loop:

```python
from scitex.dict import listed_dict

# Without keys — auto-creates lists on first access
d = listed_dict()
d["loss"].append(0.5)
d["acc"].append(0.9)

# With pre-defined keys
keys = ["loss", "acc", "lr"]
d = listed_dict(keys)
for epoch in range(10):
    d["loss"].append(compute_loss())
    d["acc"].append(compute_acc())
    d["lr"].append(current_lr)

# d["loss"] is a regular list
import numpy as np
mean_loss = np.mean(d["loss"])
```

## safe_merge

Merge multiple dicts, raising `ValueError` if any keys overlap:

```python
from scitex.dict import safe_merge

d1 = {"a": 1, "b": 2}
d2 = {"c": 3, "d": 4}

merged = safe_merge(d1, d2)
# {"a": 1, "b": 2, "c": 3, "d": 4}

# Raises ValueError on key conflict
d3 = {"b": 99}
safe_merge(d1, d3)  # ValueError: Overlapping keys found
```

## pop_keys

Remove specified keys from a list (returns a filtered list, not a dict):

```python
from scitex.dict import pop_keys

keys = ["a", "b", "c", "d", "e"]
result = pop_keys(keys, ["b", "d"])
# ["a", "c", "e"]
```

Note: this operates on a list of keys, not a dict. It is useful for filtering column name lists before DataFrame operations.

## replace

Replace all values matching a pattern in a dict:

```python
from scitex.dict import replace

d = {"a": None, "b": 1, "c": None}
updated = replace(d, old_value=None, new_value=0.0)
# {"a": 0.0, "b": 1, "c": 0.0}
```

## to_str

Convert a dict to a readable string representation:

```python
from scitex.dict import to_str

s = to_str({"a": 1, "b": [1, 2, 3], "c": {"nested": True}})
print(s)
```
