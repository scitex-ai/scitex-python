# Deprecating Functions with stx.compat

The `stx.compat` module provides the `deprecated()` decorator for marking your own functions as deprecated, along with backward-compatible wrappers for old SciTeX APIs.

## deprecated() decorator

```python
from scitex.compat import deprecated

@deprecated("new_function_name", removal_version="3.0")
def old_function(*args, **kwargs):
    return new_function(*args, **kwargs)

# Calling old_function emits:
# DeprecationWarning: old_function is deprecated.
#   Use new_function_name instead.
#   Will be removed in v3.0.
```

The decorator uses `functools.wraps` so the wrapper preserves `__name__`, `__doc__`, and other attributes of the original function.

## Provided Compatibility Wrappers

### notify / notify_async

```python
from scitex.compat import notify, notify_async

# Deprecated — calls stx.notify.alert() with a DeprecationWarning
notify("Process complete")

# Async version — calls stx.notify.alert_async()
import asyncio
asyncio.run(notify_async("Job done"))
```

Both emit `DeprecationWarning` and delegate to the current `scitex.notify` module.

## Deprecation Timeline

| Phase | Behavior |
|-------|---------|
| v1.x | Old APIs still work, DeprecationWarning emitted |
| v2.x | Old APIs removed; use new APIs directly |

## Writing Your Own Deprecated Wrapper

Pattern for migrating a function while keeping backward compatibility:

```python
from scitex.compat import deprecated

# New implementation
def load_config(path, **kwargs):
    """Load configuration from YAML."""
    ...

# Backward-compatible alias
@deprecated("load_config", removal_version="2.0")
def read_config(path, **kwargs):
    return load_config(path, **kwargs)
```
