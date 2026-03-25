# Environment Detection with stx.context

`stx.context` detects whether code is running in a Jupyter notebook, IPython console, plain Python script, or interactive Python session.

## detect_environment

Returns one of five string values:

```python
from scitex.context import detect_environment

env = detect_environment()
# Returns: "jupyter" | "ipython" | "script" | "interactive" | "unknown"
```

Detection logic (checked in order):

1. If `ipykernel` is in `sys.modules` and `get_ipython()` returns a `ZMQInteractiveShell` → `"jupyter"`
2. If `get_ipython()` returns a `TerminalInteractiveShell` → `"ipython"`
3. If `sys.argv[0]` ends with `.py` → `"script"`
4. If `sys.ps1` is defined → `"interactive"`
5. Otherwise → `"unknown"`

## Convenience Predicates

```python
from scitex.context import is_notebook, is_ipython, is_script

# True only for Jupyter notebook (ZMQInteractiveShell)
is_notebook()

# True for both Jupyter and IPython console
is_ipython()

# True only when running as a .py script
is_script()
```

## get_output_directory

Returns an appropriate output path based on the current environment:

```python
from scitex.context import get_output_directory

# In a script: <script_dir>/<script_name>_out/<path>
# In Jupyter: <cwd>/notebook_outputs/<path>
# In IPython: /tmp/<user>/ipython/<path>
# Absolute paths are returned as-is

output_path, use_temp = get_output_directory("results/data.csv")
```

The second return value (`use_temp`) is `True` when using a temporary directory (IPython / interactive sessions).

## suppress_output / quiet

Context managers that redirect stdout and stderr to `/dev/null`:

```python
from scitex.context import suppress_output, quiet

with suppress_output():
    print("This will not appear")
    import_noisy_library()

# quiet is an alias for suppress_output
with quiet():
    noisy_function()

# Pass suppress=False to conditionally disable suppression
verbose = True
with suppress_output(suppress=not verbose):
    do_work()
```

## Notebook Path Utilities

```python
from scitex.context import (
    get_notebook_path,
    get_notebook_name,
    get_notebook_directory,
    get_notebook_info_simple,
)

path = get_notebook_path()       # Absolute path to current .ipynb file
name = get_notebook_name()       # Filename without .ipynb extension
directory = get_notebook_directory()  # Directory containing the notebook
info = get_notebook_info_simple()     # Dict with path, name, directory
```

These return `None` (or empty dict) when not running in a Jupyter notebook.
