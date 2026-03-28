---
description: Core verification functions for stx.clew — status overview, per-session hash check, file provenance chain tracing, and full multi-target DAG verification.
---

# Core Verification

## status

Returns a git-status-like summary of all tracked runs.

```python
status() -> dict
```

**Returns**

```python
{
    "verified_count": int,
    "mismatch_count": int,
    "missing_count": int,
    "mismatched": [{"session_id": str, "files": [str]}],
    "missing":    [{"session_id": str, "files": [str]}],
}
```

**Example**

```python
import scitex as stx

result = stx.clew.status()
print(result["verified_count"])    # number of runs with all hashes matching
print(result["mismatched"])        # sessions whose output files have changed
```

---

## run

Verify a specific session run by comparing stored file hashes against current disk state.

```python
run(session_id: str, from_scratch: bool = False) -> RunVerification
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | `str` | required | Session identifier (e.g. `"2025Y-11M-18D-09h12m03s_HmH5"`) |
| `from_scratch` | `bool` | `False` | If `True`, re-execute the script and compare (delegates to `rerun`). If `False`, hash comparison only (fast). |

**Returns — `RunVerification` dataclass**

| Attribute | Type | Description |
|-----------|------|-------------|
| `session_id` | `str` | The session identifier |
| `script_path` | `str or None` | Path to the script that was run |
| `status` | `VerificationStatus` | `VERIFIED`, `MISMATCH`, `MISSING`, or `UNKNOWN` |
| `files` | `list[FileVerification]` | Per-file verification results |
| `combined_hash_expected` | `str or None` | Hash stored at session close |
| `combined_hash_current` | `str or None` | Hash recomputed now |
| `level` | `VerificationLevel` | `CACHE` (hash check) or `RERUN` |
| `.is_verified` | `bool` | `True` if status is `VERIFIED` |
| `.inputs` | `list[FileVerification]` | Input file results only |
| `.outputs` | `list[FileVerification]` | Output file results only |
| `.mismatched_files` | `list[FileVerification]` | Files whose hash changed |
| `.missing_files` | `list[FileVerification]` | Files that no longer exist on disk |

**`FileVerification` fields**

| Attribute | Type | Description |
|-----------|------|-------------|
| `path` | `str` | File path |
| `role` | `str` | `"input"` or `"output"` |
| `expected_hash` | `str` | 32-char SHA256 stored at run time |
| `current_hash` | `str or None` | Hash recomputed now |
| `status` | `VerificationStatus` | Per-file status |
| `.is_verified` | `bool` | `True` if status is `VERIFIED` |

**Example**

```python
import scitex as stx

result = stx.clew.run("2025Y-11M-18D-09h12m03s_HmH5")
if result.is_verified:
    print("All outputs intact")
else:
    for f in result.mismatched_files:
        print(f"Changed: {f.path}")
```

---

## chain

Trace a file back through all sessions that produced it, verifying each one.

```python
chain(target: str) -> ChainVerification
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | `str` | required | Absolute or relative path to the target file |

**Returns — `ChainVerification` dataclass**

| Attribute | Type | Description |
|-----------|------|-------------|
| `target_file` | `str` | Resolved absolute path |
| `runs` | `list[RunVerification]` | Ordered from root to leaf |
| `status` | `VerificationStatus` | Overall chain status |
| `.is_verified` | `bool` | `True` if all runs verified |
| `.failed_runs` | `list[RunVerification]` | Runs that failed verification |

**Example**

```python
import scitex as stx

chain = stx.clew.chain("results/figure1.png")
print(f"Chain length: {len(chain.runs)}")
if not chain.is_verified:
    for r in chain.failed_runs:
        print(f"Failed: {r.session_id} ({r.status.value})")
```

---

## dag

Verify a full computation DAG for one or more target files, or for all registered claims.

```python
dag(targets=None, claims=False) -> DAGVerification
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `targets` | `list[str] or None` | `None` | List of target file paths |
| `claims` | `bool` | `False` | If `True`, build DAG from all registered claims instead |

**Returns — `DAGVerification` dataclass**

| Attribute | Type | Description |
|-----------|------|-------------|
| `target_files` | `list[str]` | Resolved target file paths |
| `runs` | `list[RunVerification]` | All runs in the DAG |
| `edges` | `list[tuple[str, str]]` | `(parent_session_id, child_session_id)` pairs |
| `status` | `VerificationStatus` | Overall DAG status |
| `topological_order` | `list[str]` | Session IDs in execution order |
| `.is_verified` | `bool` | `True` if all runs verified |
| `.failed_runs` | `list[RunVerification]` | Runs that failed verification |

**Example**

```python
import scitex as stx

# Verify specific targets
result = stx.clew.dag(["results/figure1.png", "results/table1.csv"])
print(f"DAG: {len(result.runs)} runs, {len(result.edges)} edges")
print(f"Status: {result.status.value}")

# Verify all claims
result = stx.clew.dag(claims=True)
```

---

## Verification Levels

Three levels of verification exist, ordered by confidence:

| Level | Enum | Speed | Description |
|-------|------|-------|-------------|
| L1 | `VerificationLevel.CACHE` | Fast | Compare stored hashes vs current files on disk |
| L2 | `VerificationLevel.RERUN` | Slow | Re-execute pipeline in sandbox and compare outputs |
| L3 | `VerificationLevel.REGISTERED` | Slow + network | L2 + hash registered with server-side timestamp on scitex.ai |

`run()` and `chain()` use L1 by default. `rerun()` uses L2.

## Verification Statuses

| Enum value | Meaning |
|------------|---------|
| `VERIFIED` | All file hashes match |
| `MISMATCH` | One or more output files have changed |
| `MISSING` | One or more output files no longer exist on disk |
| `UNKNOWN` | No records found or session not yet finalized |
