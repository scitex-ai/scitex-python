---
description: Convert a Jupyter notebook to another format (.py, .html, .md) with convert_notebook().
---

# Notebook Conversion

## convert_notebook

Convert a `.ipynb` file to another format.

```python
convert_notebook(
    path: str,
    to: str = "script",     # "script" | "html" | "markdown"
    output_path: str | None = None,
) -> str
```

Returns the path of the converted file.

```python
import scitex as stx

# Convert to Python script (uses nbconvert)
py_path = stx.notebook.convert_notebook("experiment.ipynb", to="script")
print(py_path)  # 'experiment.py'

# Convert to HTML report
html_path = stx.notebook.convert_notebook(
    "experiment.ipynb",
    to="html",
    output_path="report.html",
)

# Convert to Markdown
md_path = stx.notebook.convert_notebook("experiment.ipynb", to="markdown")
```
