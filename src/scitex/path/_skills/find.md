---
description: Recursive file/directory search and git root discovery. find_file, find_dir, find_git_root.
---

# File and Directory Finding

## find_file

Search a directory tree for files whose name matches a glob pattern.

```python
find_file(root_dir: str | Path, exp: str | list[str]) -> list[Path]
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `root_dir` | `str` or `Path` | Root directory to search from |
| `exp` | `str` or `list[str]` | Glob pattern(s) to match against file names (e.g. `"*.csv"`, `["*.csv", "*.tsv"]`) |

**Returns** `list[Path]` — matching file paths, unsorted.

**Notes**
- Searches recursively via `Path.rglob("*")`.
- Automatically excludes paths containing `/lib/`, `/env/`, or `/build/`.
- Multiple patterns in `exp` are OR-combined.

**Examples**

```python
import scitex as stx

# Find all CSV files under ./data
csv_files = stx.path.find_file("./data", "*.csv")

# Find multiple extensions at once
data_files = stx.path.find_file("./data", ["*.csv", "*.tsv", "*.npy"])

# Find Python files in the current project
py_files = stx.path.find_file(".", "*.py")
for p in sorted(py_files):
    print(p)
```

---

## find_dir

Search a directory tree for sub-directories whose name matches a glob pattern.

```python
find_dir(root_dir: str | Path, exp: str | list[str]) -> list[Path]
```

Same signature and behavior as `find_file`, but matches directories instead of files.

**Examples**

```python
import scitex as stx

# Find all output directories
out_dirs = stx.path.find_dir(".", "*_out")

# Find versioned result directories
result_dirs = stx.path.find_dir("./results", "run_*")
```

---

## find_git_root

Return the root directory of the current git repository.

```python
find_git_root() -> Path
```

**Returns** `Path` — absolute path to the git repository root.

**Raises** `git.exc.InvalidGitRepositoryError` if the current working directory is not inside a git repository.

**Requires** the `gitpython` package (`pip install gitpython`).

**Example**

```python
import scitex as stx

root = stx.path.find_git_root()
print(root)
# Path('/home/user/proj/my-project')

# Useful for building project-relative paths regardless of cwd
config_path = root / "config" / "settings.yaml"
```
