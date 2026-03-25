---
name: os-mv
description: Move a file or directory to a destination path, auto-creating the destination directory tree if it does not exist.
---

# File Moving — mv

`stx.os.mv` is a thin wrapper around `shutil.move` that also calls `os.makedirs` on the target path before moving, so the destination directory is always created automatically.

## Function

```python
mv(src: str, tgt: str) -> None
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `src` | `str` | Source path — file or directory to move |
| `tgt` | `str` | Destination **directory** path; created with `exist_ok=True` if absent |

**Returns** `None`

**Side effects**
- Calls `os.makedirs(tgt, exist_ok=True)` unconditionally before the move
- On success: prints `"\nMoved from <src> to <tgt>"`
- On `OSError`: prints `"\nError: <error>"` and sets an internal `successful = False` flag (the flag is not returned)

> Note: `tgt` is treated as a **directory** — `os.makedirs(tgt)` is always called on it. `shutil.move` then places `src` inside that directory. If you pass a full file path as `tgt`, the final component becomes a sub-directory, not the new filename.

## Examples

```python
import scitex as stx

# Move a single file into an existing or new directory
stx.os.mv("results/run_01/data.csv", "archive/2024/")
# Prints: "\nMoved from results/run_01/data.csv to archive/2024/"
# File lands at: archive/2024/data.csv

# Move an entire directory subtree
stx.os.mv("experiments/tmp_run", "experiments/completed/")
# experiments/completed/tmp_run/ is created

# Destination is auto-created — no need to mkdir beforehand
stx.os.mv("output.pkl", "long/nested/new/dir/")
# long/nested/new/dir/ is created, then output.pkl is moved inside it
```

## Behaviour Details

- `os.makedirs(tgt, exist_ok=True)` is called even when `tgt` already exists — this is safe and has no side effects in that case
- The underlying `shutil.move` handles both same-filesystem renames (fast) and cross-filesystem copies+deletes (slower) transparently
- On `OSError` the function does **not** re-raise; it prints the error message and continues — callers cannot detect failure via return value or exception. If failure detection is needed, check for the file's presence at the destination after calling `mv`
- Silent failure is the current behaviour; do not rely on `mv` returning a success indicator
