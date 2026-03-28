---
name: stx.notebook
description: Jupyter notebook verification, compilation to DAG-ordered scripts, and reproducibility checking.
---

# stx.notebook — Skills Index

Verify, compile, and convert Jupyter notebooks. Reconstructs the actual execution dependency DAG from clew DB timestamps — "do what you want, organize later."

## Sub-skills

| File | Description |
|------|-------------|
| [parse-and-convert.md](parse-and-convert.md) | parse_notebook, get_code_cells, get_notebook_name, convert_notebook |
| [dag-compile.md](dag-compile.md) | compile_notebook, CompiledNotebook.to_mermaid(), to_script(), DAG edge logic |
| [verify.md](verify.md) | verify_notebook (clew session results), check_notebook (untracked IO scan) |

## Quick Reference

```python
from scitex.notebook import (
    parse_notebook, get_code_cells,
    compile_notebook, convert_notebook,
    verify_notebook, check_notebook,
)

cells = parse_notebook("experiment.ipynb")
compiled = compile_notebook("experiment.ipynb")
print(compiled.to_mermaid())   # Mermaid DAG
print(compiled.to_script())    # Topologically-ordered .py

results = verify_notebook("experiment.ipynb")
issues = check_notebook("experiment.ipynb")
```
