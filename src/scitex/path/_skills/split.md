---
description: Decompose a file path into its directory, stem, and extension components with split().
---

# Path Splitting

## split

Decompose a file path into three components: parent directory, stem (filename without extension), and suffix (extension including the dot).

```python
split(fpath: str | Path) -> tuple[Path, str, str]
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `fpath` | `str` or `Path` | File path to decompose |

**Returns** `(directory: Path, stem: str, extension: str)`

| Component | Type | Example for `"../data/01/day1/tt8-2.mat"` |
|-----------|------|-------------------------------------------|
| directory | `Path` | `Path('../data/01/day1')` |
| stem | `str` | `'tt8-2'` |
| extension | `str` | `'.mat'` |

**Notes**
- A thin wrapper around `Path.parent`, `Path.stem`, and `Path.suffix`.
- Returns an empty string for extension when there is no suffix (e.g. `"Makefile"`).

**Examples**

```python
import scitex as stx

# Basic decomposition
dirname, fname, ext = stx.path.split("../data/01/day1/tt8-2.mat")
print(dirname)   # Path('../data/01/day1')
print(fname)     # 'tt8-2'
print(ext)       # '.mat'

# Rebuild the original path
original = dirname / (fname + ext)

# Common use: change extension
dirname, stem, _ = stx.path.split("/results/model_v001.pkl")
new_path = dirname / (stem + ".json")
# Path('/results/model_v001.json')

# No extension
dirname, stem, ext = stx.path.split("/home/user/Makefile")
print(ext)   # ''

# Absolute path
dirname, stem, ext = stx.path.split("/home/user/data/file.csv")
print(dirname)   # Path('/home/user/data')
print(stem)      # 'file'
print(ext)       # '.csv'
```
