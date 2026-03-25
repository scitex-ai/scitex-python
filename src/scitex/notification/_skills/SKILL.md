---
name: stx.notification
description: Multi-backend notification system for alerts, calls, and SMS with automatic fallback ordering.
---

# stx.notification

The `stx.notification` module provides a multi-backend notification system for scientific workflow alerts. It supports desktop notifications, SMS, and phone calls with configurable fallback ordering when backends are unavailable.

## Python API

```python
import scitex as stx

# Send an alert notification (tries backends in order)
stx.notification.alert("Experiment complete! Accuracy: 0.95")
await stx.notification.alert_async("Training finished")

# Make a phone call
stx.notification.call("+1-555-0123", "Experiment failed, check logs")
await stx.notification.call_async("+1-555-0123", "message")

# Send SMS
stx.notification.sms("+1-555-0123", "Results saved to output/")
await stx.notification.sms_async("+1-555-0123", "message")

# Check available backends
backends = stx.notification.available_backends()

# Default fallback order
print(stx.notification.DEFAULT_FALLBACK_ORDER)
```

## Key Features

- `alert(message)` / `alert_async(message)` — send notification via best available backend
- `call(number, message)` / `call_async` — automated phone call notification
- `sms(number, message)` / `sms_async` — SMS notification
- `available_backends()` — list installed and configured notification backends
- `DEFAULT_FALLBACK_ORDER` — configured priority order of backends
- Thin re-export over `scitex-notification` standalone package
- Both sync and async interfaces for all notification types
