---
description: Manuscript claim registration and verification for stx.clew — link paper assertions (statistics, figures, tables) to their backing computations and verify them through the provenance chain.
---

# Claims

Claims link specific assertions in a manuscript to the computational outputs that back them. A claim is verifiable: clew checks that the source file still exists, its hash matches what was recorded, and the full dependency chain is intact.

## Claim types

| Type | Use case |
|------|----------|
| `statistic` | A numerical result (p-value, effect size, CI, etc.) |
| `figure` | A figure reference linked to a recipe/image |
| `table` | A table reference linked to a source CSV |
| `text` | A textual assertion linked to computational output |
| `value` | A specific computed value (count, percentage, etc.) |

---

## add_claim

Register a claim linking a manuscript assertion to the verification chain.

```python
add_claim(
    file_path: str,
    claim_type: str,
    line_number: int | None = None,
    claim_value: str | None = None,
    source_file: str | None = None,
    source_session: str | None = None,
) -> Claim
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Path to the manuscript file (e.g. `"paper/paper.tex"`) |
| `claim_type` | `str` | required | One of: `statistic`, `figure`, `table`, `text`, `value` |
| `line_number` | `int or None` | `None` | Line number in the manuscript |
| `claim_value` | `str or None` | `None` | The asserted value (e.g. `"p = 0.003"`) |
| `source_file` | `str or None` | `None` | Path to the file that produced this claim (e.g. `"results/stats.csv"`) |
| `source_session` | `str or None` | `None` | Session ID that produced the source. Auto-detected from `source_file` if omitted. |

**Returns — `Claim` dataclass**

| Attribute | Description |
|-----------|-------------|
| `claim_id` | Deterministic SHA256-based ID (e.g. `"claim_a1b2c3d4e5f6"`) |
| `file_path` | Resolved absolute path to manuscript |
| `line_number` | Line number, or `None` |
| `claim_type` | One of the five types |
| `claim_value` | The asserted value string |
| `source_session` | Session ID (auto-detected if `source_file` was provided) |
| `source_file` | Resolved absolute path to source file |
| `source_hash` | 32-char SHA256 of source file at registration time |
| `registered_at` | ISO timestamp |
| `status` | `"registered"`, `"verified"`, `"mismatch"`, `"missing"`, or `"partial"` |
| `.location` | Human-readable string: `"paper.tex:L42"` or just `"paper.tex"` |

**Example**

```python
import scitex as stx

# Register a statistic claim
claim = stx.clew.add_claim(
    file_path="paper/paper.tex",
    claim_type="statistic",
    line_number=142,
    claim_value="p < 0.001",
    source_file="results/stats.csv",
)
print(claim.claim_id)        # "claim_a1b2c3d4e5f6"
print(claim.source_session)  # auto-detected from source_file

# Register a figure claim
stx.clew.add_claim(
    file_path="paper/paper.tex",
    claim_type="figure",
    line_number=87,
    source_file="figures/figure3.png",
)
```

---

## list_claims

List registered claims with optional filters.

```python
list_claims(
    file_path: str | None = None,
    claim_type: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[Claim]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str or None` | `None` | Filter by manuscript file path |
| `claim_type` | `str or None` | `None` | Filter by claim type |
| `status` | `str or None` | `None` | Filter by status: `"registered"`, `"verified"`, `"mismatch"`, `"missing"`, `"partial"` |
| `limit` | `int` | `100` | Maximum number of results |

**Example**

```python
import scitex as stx

# All claims
all_claims = stx.clew.list_claims()

# Only unverified statistics
pending = stx.clew.list_claims(claim_type="statistic", status="registered")
for c in pending:
    print(f"{c.location}: {c.claim_value}")
```

---

## verify_claim

Verify a specific claim by checking its source file hash and following the provenance chain.

```python
verify_claim(claim_id_or_location: str) -> dict
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `claim_id_or_location` | `str` | A claim ID (`"claim_a1b2c3d4e5f6"`), a location string (`"paper.tex:L142"`), or a manuscript file path (returns first claim) |

**Returns**

```python
{
    "claim": {<Claim.to_dict()>},
    "source_verified": bool,    # source file hash still matches
    "chain_verified": bool,     # full dependency chain verified
    "details": [str],           # human-readable step results
}
```

**Verification steps**

1. Resolve the claim by ID or location string.
2. Check the source file exists on disk.
3. Compare current SHA256 of source file to stored `source_hash`.
4. Follow the dependency chain via `verify_chain(source_file)`.
5. Update claim `status` in database: `"verified"`, `"partial"` (source ok, chain failed), or `"mismatch"` / `"missing"`.

**Example**

```python
import scitex as stx

result = stx.clew.verify_claim("claim_a1b2c3d4e5f6")
print(result["source_verified"])   # True/False
print(result["chain_verified"])    # True/False
for detail in result["details"]:
    print(detail)

# By location string
result = stx.clew.verify_claim("paper/paper.tex:L142")
```

---

## Claim status icons (terminal output)

When claims are printed via the internal `format_claims` formatter:

| Icon | Status |
|------|--------|
| `○` | registered (not yet verified) |
| `✓` | verified |
| `✗` | mismatch |
| `?` | missing |
| `~` | partial (source ok but chain incomplete) |

---

## Full workflow example

```python
import scitex as stx

# After running your analysis pipeline, register claims
stx.clew.add_claim(
    file_path="paper/results.tex",
    claim_type="statistic",
    line_number=55,
    claim_value="Cohen's d = 0.82",
    source_file="results/effect_sizes.csv",
)
stx.clew.add_claim(
    file_path="paper/results.tex",
    claim_type="figure",
    line_number=78,
    source_file="figures/fig2_effect_sizes.png",
)

# List all claims
claims = stx.clew.list_claims(file_path="paper/results.tex")
print(f"{len(claims)} claims registered")

# Verify all claims via DAG
dag_result = stx.clew.dag(claims=True)
print(f"DAG status: {dag_result.status.value}")

# Or rerun the backing computations from scratch
rerun_result = stx.clew.rerun_claims()
print(f"Rerun status: {rerun_result.status.value}")
```
