---
name: clew-rerun
description: Sandbox re-execution verification for stx.clew — rerun a single session, an entire DAG, or all sessions backing manuscript claims, then compare outputs byte-for-byte.
---

# Rerun Verification

Re-execution verification (L2) actually runs the script in a subprocess and compares the new outputs against the originally stored hashes. Original output directories are never overwritten.

---

## rerun

Re-execute a session in a sandbox and compare outputs to stored hashes.

```python
rerun(
    target: str | list[str],
    timeout: int = 300,
    cleanup: bool = True,
) -> RunVerification | list[RunVerification]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | `str` or `list[str]` | required | Session ID, script path, or artifact path. A list runs each independently. |
| `timeout` | `int` | `300` | Maximum execution time per session in seconds |
| `cleanup` | `bool` | `True` | Remove sandbox output directory after comparison |

**Target resolution order**

1. Exact `session_id` match in the database
2. Script path → latest run that executed this script
3. Artifact path → latest run whose output includes this file

**Returns**

`RunVerification` (or `list[RunVerification]` if `target` is a list). The `.level` attribute is `VerificationLevel.RERUN`. The `.is_verified_from_scratch` property is `True` when `is_verified` and `level == RERUN`.

**Example**

```python
import scitex as stx

# Verify by session ID
result = stx.clew.rerun("2025Y-11M-18D-09h12m03s_HmH5")
print(result.is_verified_from_scratch)   # True if all outputs reproduced

# Verify by artifact path (finds the session that produced this file)
result = stx.clew.rerun("results/figure1.png")

# Verify multiple sessions in one call
results = stx.clew.rerun(["results/fig1.png", "results/fig2.png"])
```

---

## rerun_dag

Rerun the entire computation DAG in topological order (roots executed first).

```python
rerun_dag(
    targets: list[str] | None = None,
    timeout: int = 300,
    cleanup: bool = True,
) -> DAGVerification
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `targets` | `list[str] or None` | `None` | Target output file paths whose upstream DAG to rerun. If `None`, reruns the entire project DAG (all runs in database). |
| `timeout` | `int` | `300` | Maximum execution time per session in seconds |
| `cleanup` | `bool` | `True` | Remove sandbox output directories after each rerun |

**Behavior**

- Sessions are re-executed in topological order (upstream first).
- Each session is run with its **originally stored inputs**, not the freshly rerun upstream outputs.
- Failures propagate forward: if a parent session fails, all child sessions are also marked failed.

**Returns — `DAGVerification`**

```python
result = stx.clew.rerun_dag(["results/figure1.png"])
print(f"Status: {result.status.value}")
print(f"Order: {result.topological_order}")
for r in result.failed_runs:
    print(f"Failed: {r.session_id}")
```

---

## rerun_claims

Rerun all sessions that produced files referenced by registered claims.

```python
rerun_claims(
    file_path: str | None = None,
    claim_type: str | None = None,
    timeout: int = 300,
    cleanup: bool = True,
) -> DAGVerification
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str or None` | `None` | Filter claims by manuscript file path |
| `claim_type` | `str or None` | `None` | Filter by claim type: `statistic`, `figure`, `table`, `text`, `value` |
| `timeout` | `int` | `300` | Maximum execution time per session in seconds |
| `cleanup` | `bool` | `True` | Remove sandbox output directories after each rerun |

**Behavior**

Collects unique `source_file` paths from matching claims, resolves each to its producer session, then delegates to `rerun_dag` with those files as targets.

**Example**

```python
import scitex as stx

# Rerun everything backing the manuscript
result = stx.clew.rerun_claims()

# Rerun only sessions that back figure claims
result = stx.clew.rerun_claims(claim_type="figure")

# Rerun only sessions backing claims in a specific file
result = stx.clew.rerun_claims(file_path="paper/paper.tex")

print(result.status.value)    # "verified" | "mismatch" | "missing" | "unknown"
```

---

## Comparison logic

Output files are matched by **filename** (not full path), so sandbox outputs in a different directory are still matched to their originals. A file is `VERIFIED` only if its SHA256 hash (first 32 chars) is identical.
