---
name: dev-code-analysis
description: Analyze Python code call flows with _analyze_code_flow() and reload a module in-place with _reload() for iterative development.
---

# Code Analysis

These are internal development utilities in `scitex.dev`. They do not have a public stable API but are useful for SciTeX ecosystem development.

## _analyze_code_flow

Parse a Python file or directory and return a call graph dict.

```python
from scitex.dev import _analyze_code_flow

graph = _analyze_code_flow("src/scitex/io/__init__.py")
# Returns: {'functions': [...], 'calls': {fn: [called_fns]}}
```

---

## _reload

Reload a Python module in-place (hot-reload during interactive development).

```python
from scitex.dev import _reload
import scitex.plt as plt_mod

_reload(plt_mod)  # re-imports the module without restarting the interpreter
```

Useful in Jupyter notebooks when iterating on a module under development.

---

## _pyproject

Access pyproject.toml metadata for the current package.

```python
from scitex.dev import _pyproject

meta = _pyproject.get_metadata("scitex")
print(meta["version"])
```
