---
name: stx.events
description: Async event bus for emitting and querying events across CLI, HPC, and cloud processes.
---

# stx.events — Skills Index

The `stx.events` module provides a general-purpose async event system for scientific workflows. Events are stored locally as state files in `~/.scitex/events/` and optionally forwarded to the cloud API via webhook.

## Sub-skills

| File | Description |
|------|-------------|
| [emit-and-query.md](emit-and-query.md) | Emit events, query latest state, read history, cloud forwarding |
| [event-schema-and-types.md](event-schema-and-types.md) | Event dataclass fields, predefined event type registry |

## Quick Reference

```python
from scitex.events import emit, latest, history, list_types, get_type_info, Event

# Emit
emit("test_complete", project="myproject", status="success",
     payload={"exit_code": 0})

# Query
ev = latest("test_complete")   # dict or None
recent = history(limit=10)     # list of dicts

# Discover types
list_types()                   # sorted list of known types
get_type_info("job_done")      # {"description": ..., "payload_keys": [...]}
```

## Exports

- `emit(event_type, project, status, payload, source)` → `Event`
- `latest(event_type=None)` → `dict | None`
- `history(limit=20)` → `list[dict]`
- `list_types()` → `list[str]`
- `get_type_info(event_type)` → `dict`
- `Event` — dataclass with `to_dict()` / `from_dict()`
