---
name: stx.clew
description: Hash-based verification system for reproducible science. Tracks session runs, records file provenance via SHA256 hashes, builds dependency DAGs, links manuscript claims to computations, and stamps verification state with external timestamps. Use when you need to verify that scientific outputs are reproducible and traceable.
user-invocable: true
---

# stx.clew

Hash-based verification for reproducible scientific workflows. Zero external dependencies (pure stdlib + sqlite3). When used inside `@stx.session`, tracking is fully automatic.

## Sub-skills

### Core Verification
- [verification.md](verification.md) — `status`, `run`, `chain`, `dag`: overview, per-session hash check, file provenance tracing, multi-target DAG verification

### Rerun Verification
- [rerun.md](rerun.md) — `rerun`, `rerun_dag`, `rerun_claims`: sandbox re-execution to confirm outputs are byte-for-byte reproducible

### Claims
- [claims.md](claims.md) — `add_claim`, `list_claims`, `verify_claim`: link manuscript assertions (statistics, figures, tables) to their backing computations

### Stamping
- [stamping.md](stamping.md) — `stamp`, `list_stamps`, `check_stamp`: create external temporal proofs of verification state (file, RFC 3161, scitex.ai cloud)

### Hashing Utilities
- [hashing.md](hashing.md) — `hash_file`, `hash_directory`: standalone SHA256 utilities for individual files or whole directory trees

### Visualization
- [visualization.md](visualization.md) — `mermaid`: generate Mermaid DAG diagrams for verification state

### Automatic Integration
- [integration.md](integration.md) — how `@stx.session` and `stx.io` hook into clew automatically without any user code

### Examples and Database
- [examples-db.md](examples-db.md) — `init_examples`, `stats`, `list_runs`: scaffold example pipelines, inspect the SQLite database

### CLI
- [cli.md](cli.md) — `clew status`, `clew list`, `clew verify`, `clew stats`, `clew mermaid`

### MCP Tools
- [mcp.md](mcp.md) — `clew_status`, `clew_list`, `clew_run`, `clew_chain`, `clew_dag`, `clew_mermaid`, `clew_rerun_dag`, `clew_rerun_claims`
