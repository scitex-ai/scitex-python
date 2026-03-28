---
description: Mark functions as deprecated with the deprecated() decorator. The wrapped function emits DeprecationWarning with the new name and planned removal version on every call.
---

# Deprecation Decorator

## deprecated

Decorator factory that wraps a function to emit `DeprecationWarning` when called.

```python
deprecated(new_name: str, removal_version: str = "2.0") -> Callable
```

```python
from scitex.compat import deprecated

@deprecated("stx.repro.RandomStateManager", removal_version="3.0")
def fix_seeds(seed=42):
    """Old API — use RandomStateManager instead."""
    from scitex.repro import RandomStateManager
    return RandomStateManager(seed=seed)

# Calling fix_seeds() emits:
# DeprecationWarning: fix_seeds is deprecated.
# Use stx.repro.RandomStateManager instead.
# Will be removed in v3.0.
```

The original function's `__name__`, `__doc__`, and `__wrapped__` are preserved via `functools.wraps`.
