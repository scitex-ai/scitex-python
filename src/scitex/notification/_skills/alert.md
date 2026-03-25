---
name: notification-alert
description: Send notifications to all available backends with alert() and alert_async(). Supports message, title, and urgency level parameters.
---

# Alerts

## alert

Send a notification through all configured backends.

```python
alert(
    message: str,
    title: str = "SciTeX",
    urgency: str = "normal",  # "low" | "normal" | "critical"
) -> None
```

Iterates through `DEFAULT_FALLBACK_ORDER` and delivers via every backend that is currently reachable.

**Examples**

```python
import scitex as stx

# Notify when a long training run finishes
stx.notification.alert("Training complete. Loss = 0.023")

# With a custom title and urgency
stx.notification.alert(
    "GPU memory exceeded threshold!",
    title="Resource Warning",
    urgency="critical",
)
```

Typical usage at the end of a `@stx.session` script:

```python
@stx.session
def main(CONFIG=stx.INJECTED, logger=stx.INJECTED):
    # ... long computation ...
    stx.notification.alert("main.py finished", title="SciTeX Session")
    return 0
```

---

## alert_async

Async variant for use inside `asyncio` event loops.

```python
await alert_async(message, title="SciTeX", urgency="normal")
```

```python
import asyncio
import scitex as stx

async def run():
    # ... async work ...
    await stx.notification.alert_async("Async job complete.")

asyncio.run(run())
```
