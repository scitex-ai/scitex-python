---
description: Send email notifications from long-running scripts with auto-detected sender, subject, and system footer.
---

# stx.utils.notify

Send an email notification from a running Python script. Sender address, password, and recipient are read from environment variables so no credentials appear in source code. A system footer with hostname, username, script name, and scitex version is appended automatically.

## Signature

```python
notify(
    subject: str = "",
    message: str = ":)",
    file: str | None = None,
    ID: str | None = "auto",
    sender_name: str | None = None,
    recipient_email: str | None = None,
    cc: str | list[str] | None = None,
    attachment_paths: list[str] | None = None,
    verbose: bool = False,
) -> None
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `subject` | str | `""` | Email subject line (script name is prepended automatically) |
| `message` | str | `":)"` | Body text; any value is coerced to `str` |
| `file` | str or None | None | Override the detected script name in subject/footer |
| `ID` | str or None | `"auto"` | Unique message ID appended to subject; `"auto"` generates one via `scitex.repro.gen_ID` |
| `sender_name` | str or None | None | Display name for the From header |
| `recipient_email` | str or None | None | Recipient address; falls back to `SCITEX_SCHOLAR_EMAIL_RECIPIENT` env var |
| `cc` | str or list[str] or None | None | CC address(es) |
| `attachment_paths` | list[str] or None | None | Paths to attach; `.log` files are ANSI-stripped before attaching |
| `verbose` | bool | False | Print send confirmation to stdout |

## Environment variables

| Variable | Purpose |
|----------|---------|
| `SCITEX_SCHOLAR_EMAIL_NOREPLY` | Sender address (primary) |
| `SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS` | Sender address (deprecated fallback) |
| `SCITEX_EMAIL_NOREPLY` | Sender address (fallback) |
| `SCITEX_EMAIL_AGENT` | Sender address (last fallback, default `no-reply@scitex.ai`) |
| `SCITEX_SCHOLAR_EMAIL_PASSWORD` | SMTP password (primary) |
| `SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD` | SMTP password (deprecated fallback) |
| `SCITEX_EMAIL_PASSWORD` | SMTP password (fallback) |
| `SCITEX_SCHOLAR_EMAIL_RECIPIENT` | Recipient address (primary) |
| `SCITEX_SCHOLAR_TO_EMAIL_ADDRESS` | Recipient address (deprecated fallback) |

SMTP server is auto-detected from the sender address: `@gmail.com` uses `smtp.gmail.com:587`; all other addresses use the server configured via `SCITEX_SCHOLAR_FROM_EMAIL_SMTP_SERVER` (default `mail1030.onamae.ne.jp:587`).

## Auto-generated footer

Every message gets a footer block of the form:

```
------------------------------
Sent via
- Host: ywatanabe@machine01
- Script: train.py
- Source: scitex v2.26.0 (github.com/ywatanabe1989/scitex/blob/main/src/scitex/...)
------------------------------
```

## Examples

### Minimal — notify on completion

```python
import scitex as stx

# ... long training loop ...

stx.utils.notify(
    subject="Training complete",
    message=f"Final accuracy: {acc:.4f}",
)
```

### Attach a log file

```python
stx.utils.notify(
    subject="Experiment finished",
    message="See attached log.",
    attachment_paths=["experiment_out/run.log"],
    verbose=True,
)
```

### Explicit recipient and CC

```python
stx.utils.notify(
    subject="Batch job done",
    message="All 500 jobs completed successfully.",
    recipient_email="pi@lab.edu",
    cc=["student@lab.edu", "backup@lab.edu"],
)
```

### Suppress auto-generated ID

```python
stx.utils.notify(
    subject="Quick ping",
    message="Still running.",
    ID=None,   # omit ID from subject line
)
```

## Underlying send_gmail

`notify` is a convenience wrapper. For direct SMTP control use the internal `_send_gmail`:

```python
from scitex.utils._email import send_gmail

send_gmail(
    sender_gmail="agent@lab.edu",
    sender_password="...",
    recipient_email="user@lab.edu",
    subject="Direct send",
    message="Body text",
    smtp_server="smtp.lab.edu",
    smtp_port=587,
    attachment_paths=["report.pdf"],
    verbose=True,
)
```
