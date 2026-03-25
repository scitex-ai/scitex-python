---
description: Reconstruct the actual execution dependency graph from clew DB timestamps and export as Mermaid diagram or topologically-ordered Python script.
---

# stx.notebook — DAG Compilation

Jupyter notebooks can be run in arbitrary cell order. SciTeX records actual execution timestamps in the clew DB, then reconstructs the true dependency DAG from shared input/output files.

## compile_notebook

Query the clew DB for all `@stx.session` runs associated with a notebook, sort by timestamp, and build a dependency DAG.

```python
from scitex.notebook import compile_notebook

compiled = compile_notebook("experiment.ipynb")
# CompiledNotebook(
#     notebook_path="/.../experiment.ipynb",
#     execution_order=["sess-001", "sess-002", "sess-003"],
#     dag={"sess-001": ["sess-003"], "sess-002": [], "sess-003": []},
#     runs=[{...}, {...}, {...}],
# )
```

If no runs are found in the clew DB, returns a `CompiledNotebook` with empty fields.

## CompiledNotebook.to_mermaid

Generate a Mermaid DAG diagram showing execution flow.

```python
print(compiled.to_mermaid())
```

```
graph TD
    sess_001["sess-001<br/>2024-01-15 10:30:45"]
    sess_002["sess-002<br/>2024-01-15 10:31:12"]
    sess_003["sess-003<br/>2024-01-15 10:35:00"]
    sess_001 --> sess_003
```

Each node shows the session ID and its timestamp. Edges represent file-based dependencies: session A → session B means A produced a file that B consumed.

## CompiledNotebook.to_script

Export as a topologically-sorted Python script.

```python
script = compiled.to_script()
print(script)
```

```python
#!/usr/bin/env python3
"""Auto-compiled from notebook execution history."""

import scitex as stx


@stx.session
def step_00_sess_001():
    """Session: sess-001"""
    # Original script: /path/to/experiment.ipynb
    pass

step_00_sess_001()

@stx.session
def step_01_sess_003():
    """Session: sess-003"""
    # Original script: /path/to/experiment.ipynb
    pass

step_01_sess_003()
```

Steps are ordered by topological sort (Kahn's algorithm with timestamp as tiebreaker). Cyclic dependencies emit a `UserWarning` and fall back to timestamp order.

## DAG edge logic

`sess-A → sess-B` is added when:
- sess-A wrote a file (tracked in clew as `role="output"`)
- sess-B read that same file (tracked as `role="input"`)
- sess-A and sess-B are different sessions

Self-loops are excluded. The DAG is built from the full IO hash records in the clew DB.
