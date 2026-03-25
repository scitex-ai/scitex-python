---
name: git-commit
description: Staging and committing — git_add_all (git add .) and git_commit (git commit -m). Both validate the path, require an existing .git directory, and return bool.
---

# Staging and Committing

## git_add_all

Stage all files in a repository (`git add .`).

```python
git_add_all(repo_path: Path, verbose: bool = True) -> bool
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | `Path` | required | Git repository root (must contain `.git/`) |
| `verbose` | `bool` | `True` | Log progress messages |

**Returns** — `True` on success. Returns `False` with an error log if:
- `repo_path` does not exist
- `repo_path` contains no `.git/` directory
- `git add .` exits non-zero

```python
from pathlib import Path
import scitex as stx

ok = stx.git.git_add_all(Path("./my_project"))
```

---

## git_commit

Create a commit with a message.

```python
git_commit(repo_path: Path, message: str, verbose: bool = True) -> bool
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | `Path` | required | Git repository root (must contain `.git/`) |
| `message` | `str` | required | Non-empty commit message |
| `verbose` | `bool` | `True` | Log progress messages |

**Returns** — `True` on success. Returns `False` with an error log if:
- `repo_path` does not exist or has no `.git/`
- `message` is empty or whitespace-only
- `git commit -m` exits non-zero (including "nothing to commit")

```python
from pathlib import Path
import scitex as stx

stx.git.git_commit(Path("./my_project"), "Add experiment results")
```

---

## Typical two-step workflow

```python
from pathlib import Path
import scitex as stx

repo = Path("./my_project")
if stx.git.git_add_all(repo):
    stx.git.git_commit(repo, "Save analysis snapshot")
```
