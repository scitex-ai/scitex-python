---
description: Detect whether code is running in a script, notebook, or IPython session with detect_environment(), is_notebook(), is_script(), is_ipython(). Get the appropriate output directory with get_output_directory().
---

# Environment Detection

## detect_environment

Return a string identifying the current execution context.

```python
detect_environment() -> str  # "notebook" | "ipython" | "script"
```

```python
import scitex as stx

env = stx.context.detect_environment()
print(env)  # 'script'
```

---

## is_notebook / is_ipython / is_script

Boolean predicates for common environment checks.

```python
import scitex as stx

if stx.context.is_notebook():
    print("Running in Jupyter")
elif stx.context.is_ipython():
    print("Running in IPython")
else:
    print("Running as a plain Python script")
```

---

## get_output_directory

Return the appropriate output directory based on the current environment.

In a notebook, returns the directory containing the notebook.
In a script, returns the directory containing the script.

```python
get_output_directory() -> str
```

```python
import scitex as stx

out_dir = stx.context.get_output_directory()
# Use as base path for saving outputs
stx.io.save(results, f"{out_dir}/results.csv")
```
