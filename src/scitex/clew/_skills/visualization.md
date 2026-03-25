---
description: Mermaid DAG diagram generation for stx.clew verification state — mermaid() function with session, file, and claims-based views.
---

# Visualization

`stx.clew.mermaid()` generates Mermaid flowchart code for the verification DAG, showing sessions as nodes and their dependencies as edges.

---

## mermaid

Generate a Mermaid DAG diagram.

```python
mermaid(
    session_id: str | None = None,
    target_file: str | None = None,
    target_files: list[str] | None = None,
    claims: bool = False,
    **kwargs,
) -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | `str or None` | `None` | Start DAG from this session |
| `target_file` | `str or None` | `None` | Start DAG from the session that produced this file |
| `target_files` | `list[str] or None` | `None` | Multiple target files (builds merged multi-target DAG) |
| `claims` | `bool` | `False` | If `True`, build DAG from all registered claims |

**Returns**

A string containing Mermaid flowchart syntax. Render it in any Mermaid-compatible viewer.

**Example**

```python
import scitex as stx

# DAG rooted at a specific output file
code = stx.clew.mermaid(target_file="results/figure1.png")
print(code)
# graph TD
#   A["01_load_data.py\n2025Y-11M-18D..."] --> B["02_process.py\n2025Y-11M-18D..."]
#   B --> C["03_analyze.py\n2025Y-11M-18D..."]

# DAG from a specific session
code = stx.clew.mermaid(session_id="2025Y-11M-18D-09h12m03s_HmH5")

# Multi-target DAG (merged view of all targets)
code = stx.clew.mermaid(
    target_files=["results/figure1.png", "results/table1.csv"]
)

# DAG derived from all registered claims
code = stx.clew.mermaid(claims=True)
```

---

## Rendering the diagram

Paste the output into any Mermaid renderer:

- [mermaid.live](https://mermaid.live) — browser-based, interactive
- GitHub/GitLab markdown fences: ```` ```mermaid ... ``` ````
- VS Code with the Mermaid Preview extension
- `stx.plt.diagram.compile_mermaid(code)` — render to PNG/SVG via the scitex diagram tool

**Example: render to PNG**

```python
import scitex as stx

code = stx.clew.mermaid(claims=True)

# Write to file for manual rendering
with open("dag.mmd", "w") as f:
    f.write(code)
```

---

## Internal visualization utilities

These are not part of the public `stx.clew` API but are accessible via full import:

```python
from scitex_clew import (
    format_status,           # format status dict for terminal
    format_list,             # format run list for terminal
    format_run_verification, # format a RunVerification for terminal
    format_run_detailed,     # verbose format with file details
    format_chain_verification, # format a ChainVerification for terminal
    generate_html_dag,       # generate interactive HTML visualization
    render_dag,              # render DAG using available backends
    print_verification_summary, # print summary to stdout
)
```
