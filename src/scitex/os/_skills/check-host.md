---
description: Hostname-based guards — check_host / is_host return a boolean, verify_host exits the process when the current machine does not match.
---

# Host Checking

`stx.os` provides three functions built on `socket.gethostname()` for asserting or querying which machine the current process is running on. All three accept a plain keyword string and perform a substring match against the full hostname.

## Functions

```python
check_host(keyword: str) -> bool
is_host(keyword: str) -> bool          # alias for check_host
verify_host(keyword: str) -> None      # exits with sys.exit(1) on mismatch
```

### check_host / is_host

Return `True` when `keyword` appears anywhere in the current hostname, `False` otherwise. `is_host` is a direct alias — they are the same object.

```python
check_host(keyword) -> bool
is_host(keyword)    -> bool
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword` | `str` | Substring to search for inside `socket.gethostname()` |

**Returns** `bool`

### verify_host

Print a success or failure message, then call `sys.exit(1)` if the hostname does not contain `keyword`. Use this at the top of scripts that must only run on a designated machine (e.g. a specific HPC node).

```python
verify_host(keyword) -> None
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword` | `str` | Substring that must appear in `socket.gethostname()` |

**Side effects**
- Prints `"Host verification successed for keyword: <keyword>"` on match (note: original source spells "successed")
- Prints `"Host verification failed for keyword: <keyword>"` and calls `sys.exit(1)` on mismatch

## Examples

```python
import scitex as stx

# Boolean query — safe, never exits
if stx.os.is_host("titan"):
    print("Running on the titan cluster")

if stx.os.check_host("laptop"):
    # development-only code path
    debug_mode = True

# Hard guard — process exits immediately if not on crest
stx.os.verify_host("crest")

# Typical pattern: gate expensive setup behind host check
if stx.os.is_host("gpu-node"):
    import torch
    device = torch.device("cuda")
else:
    device = "cpu"
```

## Behaviour Details

- Match is a **substring check** (`keyword in socket.gethostname()`), not an exact match
  - `is_host("titan")` returns `True` for hostname `"titan01.hpc.example.com"`
- Case-sensitive: `is_host("TITAN")` will not match `"titan01"`
- `verify_host` calls `sys.exit(1)` — the process terminates with a non-zero exit code, which is visible to shell scripts and CI pipelines
