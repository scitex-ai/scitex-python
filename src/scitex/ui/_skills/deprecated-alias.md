---
name: stx.ui — Deprecated Notification Shim
description: scitex.ui is a deprecated shim for scitex.notify. All notification functions emit DeprecationWarning.
---

# stx.ui — Deprecated Notification Shim

`scitex.ui` re-wraps `scitex.notify` functions. Each call emits `DeprecationWarning` at call time (not import time).

## Migration

```python
# Old (triggers DeprecationWarning on each call)
import scitex as stx
stx.ui.alert("Experiment complete")
stx.ui.alert_async("Running...")
stx.ui.available_backends()

# New (preferred)
stx.notify.alert("Experiment complete")
stx.notify.alert_async("Running...")
stx.notify.available_backends()
```

## Exported wrappers

| stx.ui | stx.notify | Notes |
|---|---|---|
| `alert(*args, **kwargs)` | `notify.alert` | Synchronous notification |
| `alert_async(*args, **kwargs)` | `notify.alert_async` | Async notification |
| `available_backends()` | `notify.available_backends` | List available backends |

See `stx.notify` skills for full documentation on notification backends and configuration.
