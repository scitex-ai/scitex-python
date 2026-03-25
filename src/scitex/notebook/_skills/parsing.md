---
description: Parse a Jupyter notebook with parse_notebook(), extract only code cells with get_code_cells(), and get the notebook's stem name with get_notebook_name().
---

# Notebook Parsing

## parse_notebook

Load a `.ipynb` file and return a structured dict of all cells.

```python
parse_notebook(path: str) -> dict
```

```python
import scitex as stx

nb = stx.notebook.parse_notebook("experiment.ipynb")
print(nb.keys())        # ['metadata', 'cells', 'nbformat']
print(len(nb["cells"])) # number of cells
```

---

## get_code_cells

Extract only the code cells from a notebook dict or path.

```python
get_code_cells(nb_or_path) -> list[dict]
```

Each cell dict has: `source` (code string), `execution_count`, `outputs`.

```python
import scitex as stx

cells = stx.notebook.get_code_cells("experiment.ipynb")
for i, cell in enumerate(cells):
    print(f"Cell {i}: {cell['source'][:50]}")
```

---

## get_notebook_name

Return the notebook filename without the `.ipynb` extension.

```python
get_notebook_name(path: str) -> str
```

```python
import scitex as stx

name = stx.notebook.get_notebook_name("/home/user/experiments/analysis.ipynb")
print(name)  # 'analysis'
```
