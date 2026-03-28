---
description: How stx.clew integrates automatically with @stx.session and stx.io — zero user code required for tracking when using the SciTeX session system.
---

# Automatic Integration

When you use `@stx.session` and `stx.io`, clew tracking is fully automatic. You never call `start_tracking` or `record_input` manually.

## How it works

The integration is wired through four hooks in `scitex.clew._integration`:

| Hook | Called by | What it does |
|------|-----------|--------------|
| `on_session_start(session_id, ...)` | `@stx.session` at startup | Creates a `SessionTracker`, opens a run record in `clew.db` |
| `on_session_close(status, exit_code, ...)` | `@stx.session` at teardown | Finalizes the tracker, computes `combined_hash`, optionally auto-registers with scitex.ai |
| `on_io_load(path, track=True)` | `stx.io.load()` | Records the loaded file as an **input** hash; ensures `clew.db` exists |
| `on_io_save(path, track=True)` | `stx.io.save()` | Records the saved file as an **output** hash |

## Session tracking lifecycle

```
@stx.session start
    └─ on_session_start()
            └─ SessionTracker.__init__()
                    └─ hash_file(script_path)   ← script hash
                    └─ db.add_run(session_id, ...)

    [script body runs]
    stx.io.load("data.csv")
        └─ on_io_load("data.csv")
                └─ tracker.record_input("data.csv")
                        └─ hash_file("data.csv")
                        └─ db.add_file_hash(role="input")
                        └─ db.find_session_by_file("data.csv", role="output")
                                └─ auto-links parent sessions

    stx.io.save(result, "results.csv")
        └─ on_io_save("results.csv")
                └─ tracker.record_output("results.csv")
                        └─ hash_file("results.csv")
                        └─ db.add_file_hash(role="output")

@stx.session end
    └─ on_session_close(status="success", exit_code=0)
            └─ tracker.finalize()
                    └─ combined_hash = sha256(inputs + script + outputs)
                    └─ db.finish_run(combined_hash=...)
            └─ [optional] auto_register with scitex.ai
```

## Auto-linking parents

When a session loads a file that was produced as an **output** of a previous session, clew automatically records that previous session as a **parent**. This builds the DAG without any explicit annotation.

```python
# Session A saves results.csv
stx.io.save(df, "results.csv")        # on_io_save records role="output"

# Session B loads results.csv
df = stx.io.load("results.csv")       # on_io_load finds Session A as producer
                                       # → Session B.parent_session = Session A
```

The DAG is therefore built implicitly through file I/O.

## Database location

The database is automatically placed at:

```
<project_root>/scitex/clew.db
```

where `<project_root>` is found by walking up from `cwd` until a `.git` or `pyproject.toml` is found.

Override with the `SCITEX_CLEW_DB_PATH` environment variable:

```bash
export SCITEX_CLEW_DB_PATH=/custom/path/clew.db
```

Or programmatically:

```python
from scitex_clew import set_db
db = set_db("/custom/path/clew.db")
```

## Auto-registration with scitex.ai

When `SCITEX_AUTO_REGISTER=1` (or `true`/`yes`) is set, session hashes are automatically submitted to the scitex.ai Clew Registry at session close. This provides server-side timestamps without extra calls.

```bash
export SCITEX_AUTO_REGISTER=1
export SCITEX_API_KEY=your-api-key
```

## Manual use without @stx.session

The hooks and tracker can be used without the session decorator:

```python
from scitex_clew import start_tracking, stop_tracking
import scitex_clew as clew

tracker = start_tracking(
    session_id="my-unique-id",
    script_path=__file__,
)

# ... load and save files manually ...
tracker.record_input("data/input.csv")
tracker.record_output("results/output.csv")

summary = stop_tracking(status="success", exit_code=0)
```

## Hook parameters

### on_session_start

```python
on_session_start(
    session_id: str,
    script_path: str | None = None,
    parent_session: str | None = None,
    verbose: bool = False,
    metadata: dict | None = None,
) -> None
```

### on_session_close

```python
on_session_close(
    status: str = "success",      # "success" | "failed" | "error"
    exit_code: int = 0,
    verbose: bool = False,
    register: bool | None = None, # None = check SCITEX_AUTO_REGISTER env var
) -> None
```

### on_io_load / on_io_save

```python
on_io_load(path: str | Path, track: bool = True) -> None
on_io_save(path: str | Path, track: bool = True) -> None
```

Both always ensure `clew.db` is initialized. Pass `track=False` to skip hash recording for a specific file.
