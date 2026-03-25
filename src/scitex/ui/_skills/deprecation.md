---
name: ui-deprecation
description: scitex.ui is a backward-compatibility shim. alert(), alert_async(), and available_backends() all emit DeprecationWarning and delegate to scitex.notify equivalents.
---

# scitex.ui — Deprecation Shim

`scitex.ui` was the original notification module. It now emits `DeprecationWarning` on every call and delegates to `scitex.notify`.

## Migration

| Old (deprecated) | New |
|-----------------|-----|
| `stx.ui.alert(msg)` | `stx.notification.alert(msg)` |
| `stx.ui.alert_async(msg)` | `stx.notification.alert_async(msg)` |
| `stx.ui.available_backends()` | `stx.notification.available_backends()` |

## Old API (still functional, emits warning)

```python
import scitex as stx

# These work but emit DeprecationWarning
stx.ui.alert("Job done")           # → delegates to stx.notification.alert
stx.ui.available_backends()        # → delegates to stx.notification.available_backends
```

## Preferred API

```python
import scitex as stx

stx.notification.alert("Job done")
stx.notification.available_backends()
```
