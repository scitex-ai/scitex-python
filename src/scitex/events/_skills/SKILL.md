---
name: stx.events
description: Async event bus for emitting and querying events across CLI, HPC, and cloud processes.
---

# stx.events

The `stx.events` module provides a general-purpose async event system for scientific workflows. Events are stored locally as state files and optionally forwarded to the cloud API via webhook, enabling cross-process communication between CLI, HPC jobs, and web services.

## Python API

```python
import scitex as stx

# Emit an event
stx.events.emit(
    "test_complete",
    project="figrecipe",
    status="success",
    payload={"exit_code": 0, "module": "stats"}
)

# Get the latest event of a type
event = stx.events.latest("test_complete")
print(event["project"], event["status"])

# Get event history
history = stx.events.history("test_complete", limit=10)

# List available event types
types = stx.events.list_types()
info = stx.events.get_type_info("test_complete")

# Event schema
event: stx.events.Event = stx.events.latest("job_finished")
```

## Key Features

- `emit(event_type, **payload)` — emit a named event with arbitrary payload
- `latest(event_type)` — retrieve the most recent event of a type
- `history(event_type, limit)` — retrieve event history
- `list_types()` / `get_type_info(type)` — discover available event types
- `Event` — typed event schema dataclass
- Local state files + optional cloud API forwarding
