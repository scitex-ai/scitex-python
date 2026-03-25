---
description: Compile a Jupyter notebook into a DAG-ordered Python script with compile_notebook(). The CompiledNotebook object supports to_mermaid() for visualization and to_script() for export.
---

# Notebook Compilation

## compile_notebook

Parse cell execution timestamps, reconstruct the dependency DAG, and return a `CompiledNotebook`.

Key insight: notebooks can be executed in any cell order. SciTeX records actual execution order via timestamps, then organizes into a DAG for reproducible replay.

```python
compile_notebook(path: str) -> CompiledNotebook
```

```python
import scitex as stx

compiled = stx.notebook.compile_notebook("experiment.ipynb")
```

---

## CompiledNotebook

Object representing a DAG-compiled notebook.

```python
compiled.to_mermaid() -> str
    # Return a Mermaid.js DAG diagram string

compiled.to_script() -> str
    # Return DAG-ordered Python source code

compiled.cell_order     # list of cell indices in DAG order
compiled.dependencies   # dict mapping cell → set of dependency cells
```

```python
import scitex as stx

compiled = stx.notebook.compile_notebook("experiment.ipynb")

# Visualize the execution DAG
print(compiled.to_mermaid())

# Export as a reproducible Python script
script = compiled.to_script()
with open("experiment_compiled.py", "w") as f:
    f.write(script)
```
