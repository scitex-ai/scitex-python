---
name: stx.compat
description: Backward compatibility shim — deprecated API aliases with migration warnings.
---

# stx.compat

The `stx.compat` module provides backward compatibility aliases for deprecated SciTeX APIs and the `deprecated()` decorator for marking functions in your own code.

## Sub-skills

- [deprecated-decorator.md](deprecated-decorator.md) — `deprecated()` decorator, provided wrappers (`notify`, `notify_async`), deprecation timeline

## Quick Reference

```python
from scitex.compat import deprecated, notify

# Mark your own function as deprecated
@deprecated("new_function_name", removal_version="3.0")
def old_function(*args, **kwargs):
    return new_function(*args, **kwargs)

# Provided compat wrapper (delegates to stx.notify.alert)
notify("message")  # emits DeprecationWarning
```

## Exports

| Name | Type | Description |
|------|------|-------------|
| `deprecated` | decorator | Mark functions as deprecated with migration guidance |
| `notify` | function | Deprecated alias for `stx.notify.alert()` |
| `notify_async` | coroutine | Deprecated alias for `stx.notify.alert_async()` |
