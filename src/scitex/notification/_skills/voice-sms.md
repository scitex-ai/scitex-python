---
description: Make phone calls with call() / call_async() and send SMS with sms() / sms_async() via Twilio credentials stored as environment variables.
---

# Voice and SMS

Requires Twilio credentials set as environment variables:
- `SCITEX_TWILIO_ACCOUNT_SID`
- `SCITEX_TWILIO_AUTH_TOKEN`
- `SCITEX_TWILIO_FROM_NUMBER`
- `SCITEX_TWILIO_TO_NUMBER`

---

## call / call_async

Place a voice call that reads a message.

```python
call(message: str, to: str | None = None) -> None
await call_async(message: str, to: str | None = None)
```

`to` defaults to `SCITEX_TWILIO_TO_NUMBER` if not provided.

**Example**

```python
import scitex as stx

# Call the configured recipient
stx.notification.call("Experiment finished. Check results.")
```

---

## sms / sms_async

Send a text message.

```python
sms(message: str, to: str | None = None) -> None
await sms_async(message: str, to: str | None = None)
```

**Examples**

```python
import scitex as stx

stx.notification.sms("Pipeline succeeded. 412 samples processed.")

# Async usage
import asyncio
asyncio.run(stx.notification.sms_async("GPU job done."))
```
