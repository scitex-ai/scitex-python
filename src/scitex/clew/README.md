<!-- ---
!-- Timestamp: 2026-03-11
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/README.md
!-- --- -->

# scitex.clew — Reproducibility Verification

Hash-based verification system for reproducible scientific computations.

## What It Does

Every `@stx.session` + `stx.io.load/save` call is automatically tracked.
Clew records SHA256 hashes of all inputs and outputs, links them into a
dependency DAG, and lets you verify the entire pipeline at any time.

![Verification DAG](dag.png)

*DAG states: green (verified), red (mismatch), grey (unknown)*

## Public API (19 functions)

```python
import scitex as stx

# --- Verification (daily use) ---
stx.clew.status()                     # git-status-like overview
stx.clew.run("session_id")            # verify one run (hash check)
stx.clew.chain("output.png")          # trace file back to source
stx.clew.dag(["file1.csv", "file2"])  # verify full DAG
stx.clew.rerun("session_id")          # re-execute in sandbox & compare
stx.clew.rerun_dag()                  # rerun entire project DAG
stx.clew.rerun_claims()               # rerun all claim-backing sessions
stx.clew.list_runs(limit=50)          # list tracked runs
stx.clew.stats()                      # database statistics

# --- Claims (paper submission) ---
stx.clew.add_claim(                   # register manuscript assertion
    "paper.tex", "statistic",
    line_number=42, claim_value="p = 0.003",
    source_file="stats_out/results.csv",
)
stx.clew.list_claims()                # list registered claims
stx.clew.verify_claim("claim_abc123") # verify a specific claim

# --- Stamping (temporal proof) ---
stx.clew.stamp()                      # create timestamp proof
stx.clew.list_stamps()                # list stamps
stx.clew.check_stamp()                # verify a stamp

# --- Hashing (utilities) ---
stx.clew.hash_file("data.csv")        # SHA256 of a file
stx.clew.hash_directory("output/")    # SHA256 of all files in dir

# --- Visualization ---
stx.clew.mermaid(target_file="out.csv")  # Mermaid DAG diagram

# --- Examples ---
stx.clew.init_examples("/tmp/demo")   # scaffold example pipeline
```

## Verification Levels

| Level | Symbol | Method | Speed |
|-------|--------|--------|-------|
| Cache | `✓` | Compare stored vs current SHA256 | Fast |
| Rerun | `✓✓` | Re-execute script in sandbox, compare outputs | Slow |

Reruns are **read-only**: scripts run in a sandboxed temp directory, original
outputs are never overwritten, and the sandbox is cleaned up after comparison.

## DAG Verification

Clew tracks dependencies as a Directed Acyclic Graph:

```
01_source_a ──→ source_A.csv ──┐
                               ├──→ 07_merge ──→ final.csv ──→ 08_analyze ──→ report.json
01_source_b ──→ source_B.csv ──┤
                               │
01_source_c ──→ source_C.csv ──┘
```

When any node fails verification, all downstream nodes are also marked failed.

### Rerun modes

```python
# Rerun a single session
stx.clew.rerun("session_id")

# Rerun entire project DAG in topological order
stx.clew.rerun_dag()

# Rerun only sessions backing specific targets
stx.clew.rerun_dag(["output/figure1.png"])

# Rerun all sessions that back manuscript claims
stx.clew.rerun_claims()

# Rerun claims from a specific manuscript
stx.clew.rerun_claims(file_path="paper.tex")
```

## CLI Commands

```bash
scitex clew list                         # List runs
scitex clew status                       # git-status-like summary
scitex clew run SESSION_ID               # Verify specific run
scitex clew run SESSION_ID --from-scratch # Rerun verification
scitex clew chain FILE_PATH              # Trace dependencies
scitex clew stats                        # Database statistics
```

## MCP Tools (9 tools)

| Tool | Python API |
|------|------------|
| `clew_status` | `stx.clew.status()` |
| `clew_run` | `stx.clew.run()` |
| `clew_chain` | `stx.clew.chain()` |
| `clew_dag` | `stx.clew.dag()` |
| `clew_list` | `stx.clew.list_runs()` |
| `clew_stats` | `stx.clew.stats()` |
| `clew_mermaid` | `stx.clew.mermaid()` |
| `clew_rerun_dag` | `stx.clew.rerun_dag()` |
| `clew_rerun_claims` | `stx.clew.rerun_claims()` |

## Architecture

```
scitex/clew/
├── __init__.py          # Public API (19 functions)
├── _hash.py             # SHA256 hashing utilities
├── _db.py               # SQLite database
├── _tracker.py          # Session tracking integration
├── _chain/              # Chain/DAG verification logic
├── _rerun.py            # Rerun verification (sandbox)
├── _claim.py            # Manuscript claims
├── _stamp.py            # Temporal proof stamps
├── _registry.py         # Remote Clew Registry client
├── _integration.py      # Hooks for @stx.session and stx.io
├── _visualize.py        # Mermaid/HTML DAG rendering
└── _examples.py         # Example pipeline scaffolding
```

## Examples

See [`examples/scitex/clew/`](../../../../examples/scitex/clew/) for complete working pipelines:
- **Sequential**: 3-branch pipeline merging into final analysis
- **Multi-parent**: Diamond DAG with multi-parent nodes and claims

<!-- EOF -->
