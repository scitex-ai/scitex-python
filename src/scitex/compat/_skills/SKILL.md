---
name: stx.compat
description: Backward compatibility shim providing deprecated API aliases with migration warnings.
---

# stx.compat

The `stx.compat` module provides backward compatibility aliases for deprecated SciTeX APIs. It wraps old function names to delegate to their new implementations while emitting `DeprecationWarning` messages to guide migration.

## Python API

```python
import scitex as stx

# Use the deprecated() decorator to mark your own functions
@stx.compat.deprecated("new_function_name", removal_version="3.0")
def old_function():
    return new_function()

# Deprecated notify (use stx.notification.alert instead)
stx.compat.notify("message")  # DeprecationWarning emitted
```

## Key Features

- `deprecated(new_name, removal_version)` — decorator to mark functions as deprecated with migration guidance
- Provides backward-compatible wrappers for UI/notification functions
- All wrappers emit `DeprecationWarning` pointing to the new API
- Deprecation timeline: v1.x has warnings, v2.x removes old APIs
