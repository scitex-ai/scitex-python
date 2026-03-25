---
description: Discover available notification backends with available_backends() and inspect the DEFAULT_FALLBACK_ORDER list that controls delivery sequence.
---

# Notification Backends

## available_backends

Return a list of backend names whose dependencies are satisfied.

```python
available_backends() -> list[str]
```

```python
import scitex as stx

print(stx.notification.available_backends())
# ['desktop', 'audio', 'emacs']  — varies by environment
```

---

## DEFAULT_FALLBACK_ORDER

Module-level list defining the sequence in which backends are tried when calling `alert()`.

Built-in backend identifiers:

| Backend | Description |
|---------|-------------|
| `"desktop"` | OS desktop notification (`notify-send` / `osascript`) |
| `"audio"` | Audio chime via `scitex-audio` |
| `"emacs"` | Emacs message buffer notification |
| `"email"` | SMTP email (requires `SCITEX_EMAIL_*` env vars) |
| `"webhook"` | HTTP POST webhook |
| `"matplotlib"` | Matplotlib figure popup |
| `"playwright"` | Browser-based notification |
| `"twilio"` | SMS/voice via Twilio |

```python
import scitex as stx

print(stx.notification.DEFAULT_FALLBACK_ORDER)
# Modify the order for your environment:
# stx.notification.DEFAULT_FALLBACK_ORDER = ["audio", "desktop"]
```
