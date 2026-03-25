---
name: git-init
description: Repository initialization — init_git_repo, find_parent_git, create_child_git, remove_child_git. Controls whether a project directory uses its own isolated git repo, merges into a parent repo, or preserves cloned history.
---

# Repository Initialization

## init_git_repo

Entry point that dispatches to the appropriate git strategy.

```python
init_git_repo(
    project_dir: Path,
    git_strategy: Optional[str] = "child",
) -> Optional[Path]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_dir` | `Path` | required | Project directory to initialize |
| `git_strategy` | `str` or `None` | `"child"` | Strategy to use (see below) |

**Returns** — `Path` to the git repository root, or `None` if git is disabled.

**Raises** — `ValueError` if `git_strategy` is not one of `None`, `"child"`, `"parent"`, `"origin"`.

### Strategies

| Strategy | Behaviour |
|----------|-----------|
| `None` | Git disabled. Returns `None` immediately. |
| `"child"` | Creates an isolated `.git` inside `project_dir`. Always succeeds unless a permission error occurs. |
| `"parent"` | Searches up the directory tree for an existing git repo. If found, removes any `.git` inside `project_dir` so the project becomes part of the parent. Degrades to `"child"` if no parent is found. |
| `"origin"` | Expects the directory to already have a `.git` (e.g. cloned from a template). Degrades to `"child"` if not present. |

**Examples**

```python
from pathlib import Path
import scitex as stx

# Isolated repo in the project directory
root = stx.git.init_git_repo(Path("./my_project"), git_strategy="child")
# Returns Path("./my_project")

# Let the project live inside a parent monorepo
root = stx.git.init_git_repo(Path("./workspace/experiment"), git_strategy="parent")
# Returns the parent git root if found, otherwise ./workspace/experiment

# Git disabled
root = stx.git.init_git_repo(Path("./scratch"), git_strategy=None)
# Returns None
```

---

## find_parent_git

Walk up from `project_dir.parent` looking for an enclosing git repository.

```python
find_parent_git(project_dir: Path) -> Optional[Path]
```

Returns the root `Path` of the parent repository, or `None` if none exists.

```python
parent = stx.git.find_parent_git(Path("./workspace/experiment"))
if parent:
    print(f"Found parent repo at {parent}")
```

---

## create_child_git

Initialize a fresh, isolated git repository inside `project_dir` and make an initial commit.

```python
create_child_git(project_dir: Path) -> Optional[Path]
```

- If a git repository already exists at `project_dir`, it is left untouched (tree-structure validation is run instead).
- Returns `project_dir` on success, `None` on `PermissionError` or other `OSError`.

```python
root = stx.git.create_child_git(Path("./new_project"))
```

---

## remove_child_git

Delete the `.git` folder inside `project_dir` so the directory becomes part of a parent repository.

```python
remove_child_git(project_dir: Path) -> bool
```

Returns `True` if `.git` was removed (or was already absent), `False` on `PermissionError`.

```python
ok = stx.git.remove_child_git(Path("./sub_project"))
```

**Note** — This is called automatically by `init_git_repo` when `git_strategy="parent"` and a parent is found. Manual use is only needed in custom workflows.
