---
name: git-branch
description: Branch management — git_branch_rename (git branch -M) and git_checkout_new_branch (git checkout -b). Both validate branch names against git naming rules before running the command.
---

# Branch Management

## git_branch_rename

Rename the current branch in-place (`git branch -M <new_name>`).

```python
git_branch_rename(repo_path: Path, new_name: str, verbose: bool = True) -> bool
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | `Path` | required | Git repository root (must contain `.git/`) |
| `new_name` | `str` | required | New branch name |
| `verbose` | `bool` | `True` | Log progress messages |

**Returns** — `True` on success. Returns `False` with an error log if:
- `repo_path` does not exist or has no `.git/`
- `new_name` fails branch-name validation (see rules below)
- `git branch -M` exits non-zero

```python
from pathlib import Path
import scitex as stx

stx.git.git_branch_rename(Path("./my_project"), "main")
```

---

## git_checkout_new_branch

Create and switch to a new branch (`git checkout -b <branch_name>`).

```python
git_checkout_new_branch(repo_path: Path, branch_name: str, verbose: bool = True) -> bool
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | `Path` | required | Git repository root (must contain `.git/`) |
| `branch_name` | `str` | required | New branch name |
| `verbose` | `bool` | `True` | Log progress messages |

**Returns** — `True` on success. Returns `False` with an error log if:
- `repo_path` does not exist or has no `.git/`
- `branch_name` fails validation
- `git checkout -b` exits non-zero (e.g. branch already exists)

```python
from pathlib import Path
import scitex as stx

stx.git.git_checkout_new_branch(Path("./my_project"), "feature/new-analysis")
```

---

## Branch name validation rules

Both functions validate names before issuing git commands. A name is rejected if it:

- Is empty or whitespace-only
- Starts with `-` or `/`
- Ends with `/` or `.lock`
- Contains `..`, `//`
- Contains any of: `~`, `^`, `:`, `?`, `*`, `[`, `\`, space, or tab
