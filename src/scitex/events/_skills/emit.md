---
name: events-emit
description: Fire structured events with emit(), read the latest event of a given type with latest(), and browse the full event log with history().
---

# Emitting Events

## emit

Fire an event, writing to `~/.scitex/events/{type}_latest.json` and appending to `~/.scitex/events/history.jsonl`. If `SCITEX_API_KEY` is set, POSTs to the cloud API (best-effort).

```python
emit(
    event_type: str,
    project: str,
    status: str = "success",   # "success" | "failure"
    payload: dict | None = None,
    source: str = "local",     # "local" | "hpc" | "ci"
) -> Event
```

```python
import scitex as stx

# Signal that tests passed
stx.events.emit(
    "test_complete",
    project="my_analysis",
    status="success",
    payload={"exit_code": 0, "duration_s": 42},
    source="local",
)

# Signal an HPC job failure
stx.events.emit(
    "job_failed",
    project="my_analysis",
    status="failure",
    payload={"job_id": "12345", "reason": "OOM"},
    source="hpc",
)
```

---

## latest

Return the most-recently-emitted event of a given type.

```python
latest(event_type: str) -> dict | None
```

```python
import scitex as stx

ev = stx.events.latest("test_complete")
if ev:
    print(ev["status"], ev["payload"])
```

---

## history

Return a list of all events (newest first), optionally filtered by type.

```python
history(event_type: str | None = None, limit: int = 100) -> list[dict]
```

```python
import scitex as stx

# All recent events
all_events = stx.events.history(limit=50)

# Only test events
test_history = stx.events.history("test_complete", limit=20)
```
