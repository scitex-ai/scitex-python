---
description: Runtime environment detection in stx.gen — IPython/script detection (is_ipython, is_script), installed package listing (list_packages). Re-exports from stx.context are also available under stx.gen for backward compatibility.
---

# Environment Detection

---

## is_ipython

Returns `True` when running inside an IPython session (Jupyter notebook, IPython shell, IPdb).

```python
is_ipython() -> bool
```

Implementation checks for the existence of `__IPYTHON__` in the global namespace.

```python
import scitex as stx

if stx.gen.is_ipython():
    stx.gen.less(long_output)   # page with `less` in IPython
else:
    print(long_output)
```

---

## is_script

Returns `True` when running as a plain Python script (not inside IPython).

```python
is_script() -> bool
```

Equivalent to `not is_ipython()`.

```python
if stx.gen.is_script():
    # running as a regular script
    import argparse
    ...
```

---

## list_packages

Lists all installed Python packages and their importable modules. Uses `importlib.metadata` internally.

```python
list_packages(
    max_depth: int = 1,
    root_only: bool = True,
    skip_errors: bool = True,
    verbose: bool = False,
) -> pd.DataFrame
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_depth` | `1` | Depth of module traversal per package |
| `root_only` | `True` | Only list root-level modules (faster) |
| `skip_errors` | `True` | Silently skip packages that error on import |
| `verbose` | `False` | Print errors for failed packages |

Returns a `pd.DataFrame` with a `"Name"` column. Common packages (numpy, pandas, torch, etc.) are listed first. Known problematic packages (`nvidia`, `cuda`, `pillow`, etc.) are skipped.

```python
import scitex as stx

df = stx.gen.list_packages(root_only=True)
print(df.head(10))
#             Name
# 0   numpy.array
# 1   numpy.mean
# ...
```

Delegates to `scitex.introspect.list_api` per package.

---

## Context re-exports (backward compatibility)

The following functions are re-exported from `scitex.context` for backward compatibility. **Prefer using `stx.context.*` directly in new code.**

| Name | Preferred location |
|------|--------------------|
| `detect_environment()` | `stx.context.detect_environment` |
| `is_notebook()` | `stx.context.is_notebook` |
| `get_notebook_path()` | `stx.context.get_notebook_path` |
| `get_notebook_name()` | `stx.context.get_notebook_name` |
| `get_notebook_directory()` | `stx.context.get_notebook_directory` |
| `get_notebook_info_simple()` | `stx.context.get_notebook_info_simple` |
| `get_output_directory()` | `stx.context.get_output_directory` |

```python
# Old code (still works, triggers no warning currently)
stx.gen.is_notebook()

# Preferred
stx.context.is_notebook()
```
