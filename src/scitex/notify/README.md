# scitex.notify

Multi-backend notification system for SciTeX. Sends alerts via audio (TTS), phone calls (Twilio), email, desktop notifications, Emacs, browser popups, and webhooks.

## Quick Start

```python
import scitex

# Alert with automatic fallback (audio -> emacs -> matplotlib -> email)
scitex.notify.alert("Task complete!")

# Phone call via Twilio
scitex.notify.call("Wake up! Your experiment finished.")

# Specify backend explicitly
scitex.notify.alert("Error in pipeline", backend="email", level="error")

# Multiple backends
scitex.notify.alert("Critical failure", backend=["audio", "email", "twilio"])

# Check available backends
scitex.notify.available_backends()
# ['audio', 'emacs', 'twilio', ...]
```

## Backends

| Backend | Description | Requirements |
|---------|-------------|--------------|
| `audio` | Text-to-Speech | `scitex-audio` package |
| `twilio` | Phone call | Twilio account + env vars |
| `email` | SMTP email | SMTP server config |
| `emacs` | Minibuffer message | Running Emacs server |
| `desktop` | System notification | Windows/macOS |
| `matplotlib` | Visual popup | `matplotlib` |
| `playwright` | Browser popup | `playwright` |
| `webhook` | HTTP POST | Webhook URL |

## Phone Calls (Twilio)

### Setup

```bash
export SCITEX_NOTIFY_TWILIO_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export SCITEX_NOTIFY_TWILIO_TOKEN="your_auth_token"
export SCITEX_NOTIFY_TWILIO_FROM="+1xxxxxxxxxx"   # Your Twilio number
export SCITEX_NOTIFY_TWILIO_TO="+61xxxxxxxxxx"     # Your phone number
```

### Usage

```python
import scitex

# Simple call
scitex.notify.call("Build finished!")

# Call twice to bypass iOS silent mode (30s apart)
scitex.notify.call("Wake up!", repeat=2)

# Call with Twilio Studio Flow
scitex.notify.call("Alert!", flow_sid="FWxxxxxxx")
```

### Bypassing Silent Mode (iOS)

To receive calls while in Do Not Disturb / silent mode:

1. Save the Twilio number as a contact (e.g., "SciTeX Alert")
2. **Settings -> Focus -> Do Not Disturb -> Allow Repeated Calls** -> ON
3. Use `repeat=2` -- the second call within 3 minutes bypasses silent mode

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_NOTIFY_DEFAULT_BACKEND` | Default backend | `audio` |
| `SCITEX_NOTIFY_TWILIO_SID` | Twilio Account SID | -- |
| `SCITEX_NOTIFY_TWILIO_TOKEN` | Twilio Auth Token | -- |
| `SCITEX_NOTIFY_TWILIO_FROM` | Twilio phone number | -- |
| `SCITEX_NOTIFY_TWILIO_TO` | Destination phone | -- |
| `SCITEX_NOTIFY_TWILIO_FLOW` | Studio Flow SID | -- |

### YAML Config (`~/.scitex/config.yaml`)

```yaml
notify:
  default_backend: audio
  backend_priority:
    - audio
    - emacs
    - email
  level_backends:
    info: [audio]
    warning: [audio, emacs]
    error: [audio, emacs, email]
    critical: [audio, emacs, email, twilio]
```

## Fallback Priority

When no backend is specified, `alert()` tries backends in order until one succeeds:

1. **audio** -- TTS (fast, non-blocking)
2. **emacs** -- Minibuffer message
3. **matplotlib** -- Visual popup
4. **playwright** -- Browser popup
5. **email** -- Email (slowest, most reliable)

Note: `twilio` is never in the fallback chain -- phone calls are explicit only via `call()` or `backend="twilio"`.

## API Reference

```python
# Send notification with fallback
scitex.notify.alert(
    message: str,
    title: str = None,
    backend: str | list[str] = None,
    level: str = "info",        # info, warning, error, critical
    fallback: bool = True,
    **kwargs,
) -> bool

# Make phone call (no fallback)
scitex.notify.call(
    message: str,
    title: str = None,
    level: str = "info",
    to_number: str = None,      # Override default
    repeat: int = 1,            # Call multiple times (bypass silent mode)
    **kwargs,
) -> bool

# Async versions
await scitex.notify.alert_async(...)
await scitex.notify.call_async(...)

# List available backends
scitex.notify.available_backends() -> list[str]
```

## MCP Tools

Available via `scitex mcp serve`:

| Tool | Description |
|------|-------------|
| `notify` | Send notification via backend(s) |
| `notify_by_level` | Send using level-configured backends |
| `list_notification_backends` | List all backends and status |
| `available_notification_backends` | List working backends |
| `get_notification_config` | Get current configuration |
