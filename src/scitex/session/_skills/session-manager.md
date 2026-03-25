---
name: stx.session — SessionManager
description: The SessionManager class for tracking concurrent sessions, with create/close/query interface and global singleton access.
---

# SessionManager

`SessionManager` (defined in `_manager.py`) tracks running and closed sessions in a
process-level dictionary. It is used internally by `start()` and `close()` but is
also available for advanced use cases such as multi-session scripts or monitoring.

## Class API

```python
class SessionManager:
    def __init__(self) -> None: ...

    def create_session(
        self,
        session_id: str,
        config: Dict[str, Any],
        script_path: str = None,
    ) -> None: ...

    def close_session(
        self,
        session_id: str,
        status: str = "success",
        exit_code: int = 0,
    ) -> None: ...

    def get_active_sessions(self) -> Dict[str, Any]: ...
    def get_session(self, session_id: str) -> Dict[str, Any]: ...
    def list_sessions(self) -> Dict[str, Any]: ...
```

## Session Record Format

Each entry in `active_sessions` is a dict:

```python
{
    "config": <CONFIG DotDict>,
    "start_time": datetime(...),
    "status": "running" | "closed",
    "script_path": "/path/to/script.py",
    # Added by close_session():
    "end_time": datetime(...),
    "exit_code": 0,
}
```

## `get_active_sessions()`

Returns only entries where `status == "running"`:

```python
manager = stx.session.SessionManager()
active = manager.get_active_sessions()
# {'2025Y-11M-18D-07h53m37s_Z5MR': {'config': ..., 'status': 'running', ...}}
```

## `list_sessions()`

Returns a copy of all sessions (active and closed):

```python
all_sessions = manager.list_sessions()
```

## Global Singleton

A module-level `_session_manager` instance is created in `_manager.py`.
`start()` and `close()` use this singleton automatically. Access it with:

```python
from scitex.session._manager import get_global_session_manager
manager = get_global_session_manager()
```

Or create an independent instance:

```python
manager = stx.session.SessionManager()
```

Note: user-created instances are independent of the global one used by lifecycle
functions.

## clew Integration

`create_session()` and `close_session()` silently call `scitex.clew.on_session_start`
and `scitex.clew.on_session_close` if `scitex.clew` is importable. These are the
hooks for the verification/claim tracking system. Failures are silently caught so
that the session still functions when `scitex.clew` is unavailable.

## Use Case: Checking for Running Sessions

```python
from scitex.session._manager import get_global_session_manager

manager = get_global_session_manager()
active = manager.get_active_sessions()
if active:
    print(f"Active sessions: {list(active.keys())}")
```
