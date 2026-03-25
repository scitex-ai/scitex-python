---
name: stx.events — Emit and Query Events
description: Emit named events with payloads and query the latest state or history.
---

# stx.events — Emit and Query Events

The event bus stores each emitted event as a JSON state file in `~/.scitex/events/` and appends it to a rotating `history.jsonl` log. If `SCITEX_API_KEY` is set the event is also POSTed to the cloud API (best-effort, never raises).

## emit

```python
from scitex.events import emit

event = emit(
    "test_complete",        # event_type: arbitrary string
    project="figrecipe",    # required
    status="success",       # "success" or "failure"
    payload={               # arbitrary dict
        "exit_code": 0,
        "module": "stats",
    },
    source="local",         # "local", "hpc", or "ci"
)

print(event.type)       # "test_complete"
print(event.timestamp)  # ISO-8601 string, auto-generated
```

Files written:
- `~/.scitex/events/test_complete_latest.json` — latest state for this type
- `~/.scitex/events/history.jsonl` — append-only log (rotated at 1000 lines)

## latest

```python
from scitex.events import latest

# Latest event of a specific type
ev = latest("test_complete")
# Returns dict or None

# Most recent event across all types
ev = latest()
```

## history

```python
from scitex.events import history

recent = history(limit=20)  # list of dicts, newest first
for ev in recent:
    print(ev["type"], ev["status"], ev["timestamp"])
```

## Cloud forwarding

Set environment variables before calling `emit`:

```bash
export SCITEX_API_KEY=your_api_key
export SCITEX_API_URL=https://scitex.ai/api/events/  # optional, this is the default
```

When `SCITEX_API_KEY` is set, `emit` POSTs to the cloud API with `Authorization: Bearer <key>`. Failures are silently swallowed — the local state file is always written regardless.
