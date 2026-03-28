---
description: Extract cells from .ipynb files and convert notebooks to script format.
---

# stx.notebook — Parse and Convert Notebooks

`stx.notebook` uses stdlib `json` only — no `nbformat` dependency.

## parse_notebook

Parse a `.ipynb` file into a list of all cell dicts.

```python
from scitex.notebook import parse_notebook, get_code_cells, get_notebook_name

cells = parse_notebook("experiment.ipynb")
# [
#   {"index": 0, "cell_id": "abc123", "cell_type": "markdown", "source": "# Title"},
#   {"index": 1, "cell_id": "def456", "cell_type": "code",     "source": "import ..."},
#   ...
# ]

code_cells = get_code_cells("experiment.ipynb")
# Only cells where cell_type == "code"

name = get_notebook_name("experiment.ipynb")
# "experiment"   (stem, no extension)
```

Each cell dict contains:
- `index` — position in the notebook
- `cell_id` — notebook cell ID (or `"cell_N"` if absent)
- `cell_type` — `"code"`, `"markdown"`, or `"raw"`
- `source` — joined source string

## convert_notebook

Convert a notebook to a different output format.

```python
from scitex.notebook import convert_notebook

# Export as a flat Python script (cell order)
convert_notebook("experiment.ipynb", format="script")
# Writes experiment.py alongside the notebook

# Export as DAG-ordered script (see dag-compile.md)
convert_notebook("experiment.ipynb", format="dag")
```

## CLI

```bash
python -m scitex.notebook parse experiment.ipynb
python -m scitex.notebook convert experiment.ipynb --format script
```
