---
name: clew-mcp
description: MCP tool interface for stx.clew — all clew_ tools available to AI agents via the SciTeX MCP server.
---

# MCP Tools

All clew MCP tools are registered in the SciTeX MCP server. They accept and return JSON strings.

---

## clew_status

Show verification status summary (like git status).

**Input**: none

**Output**: JSON `{"verified_count": int, "mismatch_count": int, "missing_count": int, "mismatched": [...], "missing": [...]}`

---

## clew_list

List all tracked runs with verification status.

**Input**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `50` | Maximum runs to return |
| `status_filter` | `str or None` | `None` | Filter: `"success"`, `"failed"`, `"running"`, or `None` for all |

**Output**: JSON `{"count": int, "runs": [{"session_id", "script_path", "db_status", "verification_status", "is_verified", "started_at", "finished_at"}]}`

---

## clew_run

Verify a specific session by checking all file hashes.

**Input**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session_or_path` | `str` | Session ID or path to a file (finds associated session) |

**Output**: JSON with `session_id`, `status`, `is_verified`, `files` (per-file results), `mismatched_count`, `missing_count`.

**Example**

```json
{
  "session_id": "2025Y-11M-18D-09h12m03s_HmH5",
  "status": "verified",
  "is_verified": true,
  "files": [
    {"path": "results/figure1.png", "role": "output", "status": "verified", "is_verified": true}
  ],
  "mismatched_count": 0,
  "missing_count": 0
}
```

---

## clew_chain

Verify the dependency chain for a target file.

**Input**

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_file` | `str` | Path to the target file |

**Output**: JSON with `target_file`, `status`, `is_verified`, `chain_length`, `failed_runs_count`, `runs`.

---

## clew_dag

Verify full DAG for multiple targets or claims.

**Input**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_files` | `str or None` | `None` | Comma-separated list of target file paths |
| `claims` | `bool` | `False` | If `True`, build DAG from registered claims |

**Output**: JSON `{"target_files", "status", "is_verified", "num_runs", "num_edges", "topological_order", "runs", "edges"}`

---

## clew_mermaid

Generate Mermaid DAG diagram.

**Input**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | `str or None` | `None` | Start from this session |
| `target_file` | `str or None` | `None` | Start from session that produced this file |
| `target_files` | `str or None` | `None` | Comma-separated list of target files |
| `claims` | `bool` | `False` | Build DAG from registered claims |

**Output**: JSON `{"mermaid": "graph TD\n...", "session_id": ..., "target_file": ..., ...}`

---

## clew_rerun_dag

Re-execute entire DAG in topological order and compare outputs (L2 verification).

**Input**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_files` | `str or None` | `None` | Comma-separated target paths. Omit to rerun the entire project DAG. |
| `timeout` | `int` | `300` | Max execution time per session (seconds) |

**Output**: DAGVerification JSON (same structure as `clew_dag`).

---

## clew_rerun_claims

Re-execute all sessions backing manuscript claims (L2 verification).

**Input**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str or None` | `None` | Filter claims by manuscript file path |
| `claim_type` | `str or None` | `None` | Filter: `statistic`, `figure`, `table`, `text`, `value` |
| `timeout` | `int` | `300` | Max execution time per session (seconds) |

**Output**: DAGVerification JSON.

---

## DAGVerification JSON structure

All DAG-level tools (`clew_dag`, `clew_rerun_dag`, `clew_rerun_claims`) return:

```json
{
  "target_files": ["results/figure1.png"],
  "status": "verified",
  "is_verified": true,
  "num_runs": 3,
  "num_edges": 2,
  "topological_order": ["session_A", "session_B", "session_C"],
  "runs": [
    {
      "session_id": "session_A",
      "script_path": "/path/01_load.py",
      "status": "verified",
      "is_verified": true
    }
  ],
  "edges": [
    {"parent": "session_A", "child": "session_B"},
    {"parent": "session_B", "child": "session_C"}
  ]
}
```
