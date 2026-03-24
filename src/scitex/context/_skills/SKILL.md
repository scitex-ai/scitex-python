---
name: stx.context
description: Runtime environment detection for notebooks, scripts, IPython, and output suppression.
---

# stx.context

The `stx.context` module provides utilities for detecting the current Python runtime environment (Jupyter notebook, IPython, script) and managing output suppression. It also provides notebook path resolution utilities.

## Python API

```python
import scitex as stx

# Detect current environment
env = stx.context.detect_environment()  # "notebook", "ipython", "script"
is_nb = stx.context.is_notebook()
is_ip = stx.context.is_ipython()
is_sc = stx.context.is_script()

# Get appropriate output directory
out_dir = stx.context.get_output_directory()

# Notebook path utilities
nb_path = stx.context.get_notebook_path()
nb_name = stx.context.get_notebook_name()
nb_dir = stx.context.get_notebook_directory()
nb_info = stx.context.get_notebook_info_simple()

# Suppress output
with stx.context.suppress_output():
    noisy_function()

with stx.context.quiet():
    another_noisy_function()
```

## Key Features

- `detect_environment()` — returns `"notebook"`, `"ipython"`, or `"script"`
- `is_notebook()` / `is_ipython()` / `is_script()` — boolean environment checks
- `get_output_directory()` — context-aware output path selection
- Notebook path utilities: `get_notebook_path`, `get_notebook_name`, `get_notebook_directory`
- `suppress_output()` / `quiet()` — context managers for stdout/stderr suppression
