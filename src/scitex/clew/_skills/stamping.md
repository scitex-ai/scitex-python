---
description: External temporal proof of verification state for stx.clew — stamp, list_stamps, check_stamp. Creates an independently verifiable record that your verification state was consistent at a specific point in time.
---

# Stamping

Stamps create an external temporal proof that the verification database was in a specific state at a particular time. Only cryptographic hashes are transmitted — never actual data.

## How it works

1. `stamp()` computes a **root hash** by combining the `combined_hash` of every successful run, sorted by session ID (deterministic).
2. The root hash is submitted to an external backend that attaches a trusted timestamp.
3. The stamp is stored in the database (`stamps` table).
4. `check_stamp()` recomputes the root hash from the same sessions and compares it.

## Backends

| Backend | Trust level | External dependency |
|---------|-------------|---------------------|
| `"file"` | Local only | None — writes JSON to `.scitex/stamps/` |
| `"rfc3161"` | High — standard TSA | `rfc3161ng` package (default TSA: DFN `zeitstempel.dfn.de`) |
| `"zenodo"` | Archival + DOI | Not yet implemented |
| `"scitex_cloud"` | Server-side timestamp | scitex.ai account (`SCITEX_API_KEY`) |

---

## stamp

Record a root hash with an external timestamp.

```python
stamp(
    backend: str = "file",
    service_url: str | None = None,
    session_ids: list[str] | None = None,
    output_dir: str | None = None,
) -> Stamp
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | `str` | `"file"` | One of: `"file"`, `"rfc3161"`, `"zenodo"`, `"scitex_cloud"` |
| `service_url` | `str or None` | `None` | URL for RFC 3161 TSA or scitex.ai API endpoint |
| `session_ids` | `list[str] or None` | `None` | Specific sessions to include. If `None`, includes all successful runs with a `combined_hash`. |
| `output_dir` | `str or None` | `None` | Directory for `"file"` backend stamps. Default: `<db_dir>/stamps/`. |

**Returns — `Stamp` dataclass**

| Attribute | Description |
|-----------|-------------|
| `stamp_id` | Deterministic ID: `"stamp_<sha256[:12]>"` |
| `root_hash` | SHA256 over all session combined-hashes |
| `timestamp` | ISO 8601 UTC timestamp |
| `backend` | Backend used |
| `service_url` | URL or file path of the proof |
| `response_token` | Backend-specific token (RFC 3161 token bytes as hex, or server timestamp) |
| `run_count` | Number of sessions included in the root hash |
| `metadata` | `{"session_ids": [...]}` |

**Examples**

```python
import scitex as stx

# Local file stamp (for development)
s = stx.clew.stamp()
print(f"Stamped {s.run_count} runs: {s.stamp_id}")
print(f"Root hash: {s.root_hash[:16]}...")

# RFC 3161 — requires: pip install rfc3161ng
s = stx.clew.stamp(backend="rfc3161")

# SciTeX cloud (requires SCITEX_API_KEY env var)
s = stx.clew.stamp(backend="scitex_cloud")

# Stamp only specific sessions
s = stx.clew.stamp(session_ids=["2025Y-11M-18D-09h12m03s_HmH5"])
```

---

## list_stamps

List all stamps, most recent first.

```python
list_stamps(limit: int = 20) -> list[Stamp]
```

**Example**

```python
import scitex as stx

stamps = stx.clew.list_stamps()
for s in stamps:
    print(f"{s.timestamp}  {s.stamp_id}  backend={s.backend}  runs={s.run_count}")
```

---

## check_stamp

Verify a stamp against the current verification state.

```python
check_stamp(stamp_id: str | None = None) -> dict
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stamp_id` | `str or None` | `None` | ID of stamp to check. If `None`, checks the most recent stamp. |

**Returns**

```python
{
    "stamp": {<Stamp.to_dict()>},
    "current_root_hash": str,    # root hash recomputed now
    "matches": bool,             # True if hashes match
    "details": [str],            # human-readable explanation
}
```

**Example**

```python
import scitex as stx

result = stx.clew.check_stamp()   # check the latest stamp

if result["matches"]:
    print("Verification state unchanged since stamp")
else:
    for detail in result["details"]:
        print(detail)
    # Example output:
    # "Root hash CHANGED since stamp at 2026-01-15T10:30:00+00:00"
    # "  Stamped:  a1b2c3d4e5f6g7h8..."
    # "  Current:  x9y8z7w6v5u4t3s2..."
    # "  Run count changed: 10 → 12"

# Check a specific stamp by ID
result = stx.clew.check_stamp("stamp_a1b2c3d4e5f6")
```

---

## Root hash construction

The root hash is a SHA256 over all included sessions in sorted order:

```python
hasher = sha256()
for session_id in sorted(included_session_ids):
    hasher.update(session_id.encode())
    hasher.update(combined_hash_of_session.encode())
root_hash = hasher.hexdigest()
```

This means adding new successful sessions will change the root hash (the run count is also stored and compared).
