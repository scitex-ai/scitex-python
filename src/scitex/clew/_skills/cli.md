---
description: CLI interface for stx.clew — clew status, list, verify, stats, mermaid commands.
---

# CLI Interface

Install: `pip install scitex-clew[cli]` (requires `click`).

Entry point: `clew`

```bash
clew --help
clew --version
clew --help-recursive   # show help for all sub-commands
```

---

## clew status

Git-status-like overview of the verification database.

```bash
clew status
```

**Output**: JSON with `verified_count`, `mismatch_count`, `missing_count`, `mismatched`, `missing`.

---

## clew list

List tracked runs.

```bash
clew list [--limit N]
```

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `--limit N` | `50` | Maximum number of runs to display |

**Output format**: one line per run:

```
success  2025Y-11M-18D-09h12m03s_HmH5  /path/to/script.py
failed   2025Y-11M-18D-10h05m12s_XyZ3  /path/to/other.py
```

---

## clew verify

Verify a specific run by session ID.

```bash
clew verify SESSION_ID
```

**Output**

```
[OK]   2025Y-11M-18D-09h12m03s_HmH5 (verified)
  [OK] output  results/figure1.png
  [OK] output  results/table1.csv
  [!!] output  results/stats.csv
```

Icons: `[OK]` = verified, `[!!]` = mismatch or missing.

---

## clew stats

Database statistics.

```bash
clew stats
```

**Output**: JSON with total run counts, file hash counts, etc.

---

## clew mermaid

Generate Mermaid DAG diagram code.

```bash
clew mermaid [--claims]
```

**Options**

| Flag | Description |
|------|-------------|
| `--claims` | Build DAG from all registered claims instead of full database |

**Output**: Mermaid flowchart code, printed to stdout. Pipe to a file or viewer:

```bash
clew mermaid > dag.mmd
clew mermaid --claims > claims_dag.mmd
```

---

## clew completion

Generate shell completion script.

```bash
eval "$(clew completion bash)"
eval "$(clew completion zsh)"
clew completion fish | source
```

**Supported shells**: `bash`, `zsh`, `fish`

---

## Shell quickstart

```bash
# See all tracked runs
clew list

# Check overall verification health
clew status

# Verify a specific session
clew verify 2025Y-11M-18D-09h12m03s_HmH5

# Generate DAG diagram
clew mermaid | pbcopy    # macOS: paste into mermaid.live

# Set custom DB path
SCITEX_CLEW_DB_PATH=/my/project/clew.db clew status
```
