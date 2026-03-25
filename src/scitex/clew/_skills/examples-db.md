---
description: Example pipeline scaffolding and database inspection for stx.clew — init_examples, stats, list_runs.
---

# Examples and Database

## init_examples

Copy bundled example pipeline scripts to a destination directory.

```python
init_examples(
    dest: str | Path,
    variant: str = "sequential",
) -> dict
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dest` | `str` or `Path` | required | Destination directory. Created if it does not exist. Existing scripts are overwritten. |
| `variant` | `str` | `"sequential"` | Example variant: `"sequential"` (linear pipeline A→B→C) or `"multi_parent"` (multi-root DAG with joining) |

**Returns**

```python
{
    "path": str,         # absolute path to dest
    "files": [str],      # list of copied filenames
    "file_count": int,   # number of files copied
    "variant": str,      # variant used
}
```

**Raises**

- `ValueError` if `variant` is not `"sequential"` or `"multi_parent"`
- `FileNotFoundError` if the bundled examples cannot be located

**Example**

```python
import scitex as stx

# Scaffold a sequential pipeline example
info = stx.clew.init_examples("./my_clew_demo")
print(f"Copied {info['file_count']} files to {info['path']}")
print(info['files'])
# ['01_source_a.py', '02_preprocess_a.py', '03_source_b.py',
#  '04_preprocess_b.py', '05_source_c.py', '06_preprocess_c.py',
#  '07_merge.py', '08_analyze.py', '09_demo_verification.py',
#  '10_programmatic_verification.py']

# Multi-root DAG with joining
info = stx.clew.init_examples("./clew_multiparent", variant="multi_parent")
```

**After scaffolding**, run the pipeline to populate the database:

```bash
cd my_clew_demo
python 01_source_a.py
python 02_preprocess_a.py
# ... run all scripts ...
python 09_demo_verification.py   # shows verification output
```

---

## stats

Get database statistics.

```python
stats() -> dict
```

**Returns**

A dict with counts and metadata about the verification database.

**Example**

```python
import scitex as stx

info = stx.clew.stats()
print(info)
# {"total_runs": 42, "success_runs": 40, "failed_runs": 2, ...}
```

---

## list_runs

List tracked session runs.

```python
list_runs(
    limit: int = 100,
    status: str | None = None,
) -> list[dict]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `100` | Maximum number of runs to return (most recent first) |
| `status` | `str or None` | `None` | Filter by run status: `"success"`, `"failed"`, `"running"`, or `None` for all |

**Returns**

List of dicts, each with:

| Key | Description |
|-----|-------------|
| `session_id` | Unique session identifier |
| `script_path` | Path to the script that was run |
| `script_hash` | SHA256 of script at run time |
| `started_at` | ISO timestamp |
| `finished_at` | ISO timestamp, or `None` if still running |
| `status` | `"success"`, `"failed"`, `"running"`, or `"error"` |
| `exit_code` | Process exit code |
| `parent_session` | Parent session ID, or `None` |
| `combined_hash` | Combined hash of inputs + script + outputs |
| `metadata` | JSON metadata string, or `None` |

**Example**

```python
import scitex as stx

# All recent runs
runs = stx.clew.list_runs(limit=20)
for r in runs:
    print(f"{r['status']:<8} {r['session_id']}  {r['script_path']}")

# Only failed runs
failed = stx.clew.list_runs(status="failed")
for r in failed:
    print(f"FAILED: {r['session_id']}")
```

---

## Database schema overview

The SQLite database at `<project_root>/scitex/clew.db` has these tables:

| Table | Description |
|-------|-------------|
| `runs` | One row per session: session_id, script_path, script_hash, timestamps, status, combined_hash |
| `file_hashes` | One row per file per session: session_id, file_path, hash, role (input/output) |
| `session_parents` | Junction table for multi-parent DAG: session_id, parent_session |
| `verification_results` | Historical log of verification checks: session_id, level, status, timestamp |
| `claims` | Manuscript claims: claim_id, file_path, line_number, claim_type, claim_value, source_session, source_file, source_hash |
| `stamps` | Temporal proofs: stamp_id, root_hash, timestamp, backend, response_token |
