---
description: Verify notebook reproducibility via clew DB and check for untracked IO calls.
---

# stx.notebook — Verification

Two functions cover notebook reproducibility: `verify_notebook` checks clew DB session results, and `check_notebook` scans cell source for untracked IO.

## verify_notebook

Find all clew sessions associated with the notebook and run L1 (cache) verification on each.

```python
from scitex.notebook import verify_notebook

results = verify_notebook("experiment.ipynb")
# [
#   {"session_id": "sess-001", "status": "verified", "is_verified": True,  "started_at": "2024-01-15 10:30:45"},
#   {"session_id": "sess-002", "status": "stale",    "is_verified": False, "started_at": "2024-01-15 10:31:12"},
#   {"session_id": "sess-003", "status": "error",    "is_verified": False, "error": "..."},
# ]
```

A session is associated with a notebook when its clew `metadata.notebook_path` or `script_path` matches the resolved notebook path.

`status` comes from `scitex.clew.verify_run()`. Typical values: `"verified"`, `"stale"`, `"missing"`, `"error"`.

## check_notebook

Scan code cells for `stx.io.load()` / `stx.io.save()` calls that are NOT inside an `@stx.session` function.

```python
from scitex.notebook import check_notebook

issues = check_notebook("experiment.ipynb")
# [
#   {"index": 3, "has_load": True, "has_save": False, "has_session": False},
#   {"index": 7, "has_load": False, "has_save": True,  "has_session": False},
# ]
```

Returns only cells that have untracked IO (IO call present, `@stx.session` absent). An empty list means all IO is properly tracked.

Patterns detected:
- `stx.io.load(` and `scitex.io.load(` for load calls
- `stx.io.save(` and `scitex.io.save(` for save calls
- `@stx.session` and `@scitex.session` for session decorators
