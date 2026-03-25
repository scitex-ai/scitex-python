---
description: Legacy notify() and notify_async() wrappers in scitex.compat that emit DeprecationWarning and delegate to scitex.notify.alert().
---

# Legacy Aliases

## notify

Deprecated wrapper for `scitex.notify.alert`.

```python
from scitex.compat import notify

notify("Job done")
# DeprecationWarning: scitex.compat.notify is deprecated.
# Use scitex.notify.alert instead.
```

## notify_async

Deprecated async wrapper for `scitex.notify.alert_async`.

```python
import asyncio
from scitex.compat import notify_async

asyncio.run(notify_async("Async job complete."))
# DeprecationWarning: scitex.compat.notify_async is deprecated.
# Use scitex.notify.alert_async instead.
```

## Migration

| Old | New |
|-----|-----|
| `stx.compat.notify(msg)` | `stx.notification.alert(msg)` |
| `await stx.compat.notify_async(msg)` | `await stx.notification.alert_async(msg)` |
