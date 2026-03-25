---
description: Normalize a path string — resolve ./ and ../ references, collapse double slashes, and replace spaces with underscores. clean().
---

# Path Cleaning

## clean

Normalize a path string by resolving dot references, collapsing redundant slashes, and replacing spaces with underscores.

```python
clean(path_string: str | os.PathLike) -> str
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path_string` | `str` or path-like | Path string to normalize |

**Returns** `str` — the cleaned path string.

**Transformations applied (in order)**

1. Path-like objects (`os.PathLike`) are converted to `str`.
2. Spaces are replaced with underscores.
3. `os.path.normpath` resolves `./`, `../`, and trailing separators.
4. Any remaining `//` sequences are collapsed to `/`.
5. A trailing `/` is preserved if the original string ended with `/` (directory indicator).

**Examples**

```python
import scitex as stx

# Resolve . and .. references
stx.path.clean('/home/user/./folder/../file.txt')
# '/home/user/file.txt'

# Collapse double slashes
stx.path.clean('path/./to//file.txt')
# 'path/to/file.txt'

# Replace spaces with underscores
stx.path.clean('path with spaces')
# 'path_with_spaces'

# Preserve trailing slash for directories
stx.path.clean('/data/project/')
# '/data/project/'

# Empty string returns empty string
stx.path.clean('')
# ''

# Works with pathlib Path objects
from pathlib import Path
stx.path.clean(Path('/home/user/./data'))
# '/home/user/data'
```

**Common use cases**

```python
import scitex as stx

# Clean a user-provided path before using it
user_input = input("Enter output directory: ")   # "my results/"
out_dir = stx.path.clean(user_input)             # "my_results/"

# Clean a dynamically built path
import os
base = "/project"
subdir = "run 01"
fpath = os.path.join(base, subdir, "./output/../final.csv")
clean_path = stx.path.clean(fpath)
# '/project/run_01/final.csv'
```
