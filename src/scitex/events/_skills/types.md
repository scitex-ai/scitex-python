---
description: List registered event type names with list_types(), get metadata for a specific type with get_type_info(), and use the Event dataclass for type-checked event construction.
---

# Event Types

## list_types

Return all registered event type names.

```python
list_types() -> list[str]
```

```python
import scitex as stx

print(stx.events.list_types())
# ['test_complete', 'job_failed', 'session_start', 'session_end', ...]
```

---

## get_type_info

Return metadata for a specific event type.

```python
get_type_info(event_type: str) -> dict
```

```python
import scitex as stx

info = stx.events.get_type_info("test_complete")
print(info)
# {'name': 'test_complete', 'description': '...', 'payload_schema': {...}}
```

---

## Event

Dataclass representing a single event instance.

```python
from scitex.events import Event

ev = Event(
    type="test_complete",
    project="my_analysis",
    status="success",
    payload={"exit_code": 0},
    source="local",
)
print(ev.type, ev.status)
```

Fields: `type`, `project`, `status`, `payload`, `source`, `timestamp` (auto-set).
