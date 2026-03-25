---
description: Miscellaneous path utilities — getsize (file size in bytes), this_path / get_this_path (caller script path), get_data_path_from_a_package (package data files).
---

# Miscellaneous Path Utilities

---

## getsize

Get the size of a file in bytes.

```python
getsize(path: str | Path) -> int | float
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` or `Path` | Path to the file |

**Returns** `int` — file size in bytes, or `float('nan')` (`np.nan`) if the file does not exist.

**Example**

```python
import scitex as stx

size = stx.path.getsize("large_dataset.h5")
if size is not float('nan'):
    print(f"File size: {size:,} bytes ({size / 1e6:.1f} MB)")

# Non-existent file returns np.nan
import numpy as np
size = stx.path.getsize("missing_file.csv")
print(np.isnan(size))   # True
```

---

## this_path / get_this_path

Return the filesystem path of the **calling** script.

```python
this_path(ipython_fake_path: str = "/tmp/fake.py") -> Path
```

`get_this_path` is an alias for `this_path`.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ipython_fake_path` | `str` | `"/tmp/fake.py"` | Path to return when running inside IPython/Jupyter (where `__file__` is unavailable) |

**Returns** `Path` — absolute path to the script that called `this_path()`.

**Notes**
- Uses `inspect.stack()` to find the caller's filename.
- When called from within IPython or Jupyter (detected by `"ipython"` in the filename), returns `ipython_fake_path` instead.
- Equivalent to `Path(__file__)` in a normal script, but works from any call depth and handles IPython gracefully.

**Examples**

```python
import scitex as stx

# In /home/user/proj/analysis.py:
script = stx.path.this_path()
# Path('/home/user/proj/analysis.py')

# Use to build sibling paths robustly
config = stx.path.this_path().parent / "config.yaml"

# Custom IPython fallback
script = stx.path.this_path(ipython_fake_path="/tmp/notebook_session.py")
```

---

## get_data_path_from_a_package

Locate a data file that ships with an installed Python package.

```python
get_data_path_from_a_package(package_str: str, resource: str) -> Path
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `package_str` | `str` | Importable package name (e.g. `"my_package"`) |
| `resource` | `str` | Filename of the resource inside the package's `data/` directory |

**Returns** `Path` — absolute path to the resource file.

**Raises**
- `ImportError` — if the package cannot be found via `importlib`.
- `FileNotFoundError` — if the resource does not exist under the package's `data/` directory.

**Data directory resolution**

The function walks up from the package's `__init__.py` location until it finds the `src/` directory boundary, then looks for a `data/` sibling:

```
<repo>/
    src/
        my_package/
            __init__.py
    data/
        reference.csv    <- located here
```

**Example**

```python
import scitex as stx

# Retrieve a bundled reference file from an installed package
ref_path = stx.path.get_data_path_from_a_package("my_package", "reference.csv")
import pandas as pd
df = pd.read_csv(ref_path)
```
