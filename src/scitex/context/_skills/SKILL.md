---
name: stx.context
description: Runtime environment detection (notebook/IPython/script) and output suppression utilities.
---

# stx.context

The `stx.context` module provides utilities for detecting the current Python runtime environment and managing output suppression.

## Sub-skills

- [environment-detection.md](environment-detection.md) — `detect_environment`, `is_notebook`, `is_ipython`, `is_script`, `get_output_directory`, `suppress_output`/`quiet`, notebook path utilities

## Quick Reference

```python
from scitex.context import (
    detect_environment,
    is_notebook, is_ipython, is_script,
    get_output_directory,
    suppress_output, quiet,
    get_notebook_path, get_notebook_name, get_notebook_directory,
)

env = detect_environment()   # "jupyter" | "ipython" | "script" | "interactive" | "unknown"

if is_notebook():
    path = get_notebook_path()

out_dir, use_temp = get_output_directory("results/data.csv")

with suppress_output():      # quiet() is an alias
    noisy_function()
```

## Environment Return Values

| Value | Condition |
|-------|-----------|
| `"jupyter"` | ZMQInteractiveShell (ipykernel running) |
| `"ipython"` | TerminalInteractiveShell |
| `"script"` | `sys.argv[0]` ends with `.py` |
| `"interactive"` | `sys.ps1` defined |
| `"unknown"` | None of the above |
