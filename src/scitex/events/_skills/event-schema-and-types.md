---
name: stx.events — Event Schema and Known Types
description: The Event dataclass and the registry of predefined event types.
---

# stx.events — Event Schema and Known Types

## Event Dataclass

`Event` is a plain dataclass that captures all fields emitted to the bus.

```python
from scitex.events import Event

event = Event(
    type="job_done",
    project="my_project",
    status="success",        # default "success"
    payload={"job_id": "12345", "host": "gpu01"},
    source="hpc",            # default "local"
    # timestamp auto-generated if not provided
)

d = event.to_dict()          # JSON-serializable dict
event2 = Event.from_dict(d)  # round-trip
```

Fields:
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | str | required | Event type string |
| `project` | str | required | Project name |
| `status` | str | `"success"` | `"success"` or `"failure"` |
| `payload` | dict | `{}` | Arbitrary event data |
| `source` | str | `"local"` | `"local"`, `"hpc"`, or `"ci"` |
| `timestamp` | str | auto | ISO-8601 string |

## Known Event Types

Five predefined event types are registered with expected payload keys:

```python
from scitex.events import list_types, get_type_info

print(list_types())
# ['build_result', 'job_done', 'scholar_done', 'stats_done', 'test_complete']

info = get_type_info("test_complete")
# {
#   "description": "Test suite completed (local or HPC)",
#   "payload_keys": ["exit_code", "module", "log_tail"]
# }
```

| Type | Description | Expected payload keys |
|------|-------------|----------------------|
| `test_complete` | Test suite completed | `exit_code`, `module`, `log_tail` |
| `job_done` | HPC/Slurm job finished | `job_id`, `host`, `state` |
| `build_result` | LaTeX manuscript build | `doc_type`, `success`, `errors` |
| `scholar_done` | Scholar fetch/enrichment | `count`, `failed`, `project` |
| `stats_done` | Long statistical computation | `test_name`, `p_value`, `duration` |

Unknown types are accepted — the registry is informational only.
