---
name: stx.clew
description: Hash-based verification system for reproducible science with DAG tracking and manuscript claims.
---

# stx.clew

The `stx.clew` module provides hash-based verification for reproducible scientific workflows. It tracks experiment runs, verifies file provenance, builds dependency DAGs, and links manuscript claims to their backing computations.

## Python API

```python
import scitex as stx

# Git-status-like overview of verification status
stx.clew.status()

# Verify a single run (hash check)
result = stx.clew.run(session_id)

# Trace a file back to its source chain
chain = stx.clew.chain("results/output.csv")

# Verify full computation DAG
dag_result = stx.clew.dag(["results/figure1.png", "results/table1.csv"])

# Re-execute and compare in sandbox
stx.clew.rerun("results/output.csv")

# Register a manuscript assertion
stx.clew.add_claim(
    claim="Group A > Group B (p < 0.05)",
    session_id="abc123",
    figure="figure3.png"
)

# List and verify claims
claims = stx.clew.list_claims()
stx.clew.verify_claim(claim_id="claim_001")

# Compute file hashes
h = stx.clew.hash_file("data/raw.csv")
h_dir = stx.clew.hash_directory("data/")

# Generate Mermaid DAG diagram
mermaid_code = stx.clew.mermaid(["results/figure1.png"])
```

## Key Features

- `status()` — overview of all tracked runs and their verification state
- `run(session_id)` — verify a session's output hashes match recorded values
- `chain(file)` / `dag(targets)` — trace provenance and verify full dependency graphs
- `rerun(target)` / `rerun_dag(targets)` — sandbox re-execution for verification
- `add_claim` / `list_claims` / `verify_claim` — link manuscript assertions to computations
- `stamp` / `list_stamps` / `check_stamp` — temporal proof of computation
- `hash_file` / `hash_directory` — SHA256 hashing utilities
