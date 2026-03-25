---
description: Repository creation — clone_repo (clone from URL with optional branch/tag) and git_init (bare git init -b main). Both return bool.
---

# Repository Cloning and Initialization

## clone_repo

Clone a remote git repository to a local path.

```python
clone_repo(
    url: str,
    target_path: Path,
    branch: str = None,
    tag: str = None,
    verbose: bool = True,
) -> bool
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | required | Git repository URL |
| `target_path` | `Path` | required | Local destination path |
| `branch` | `str` | `None` | Branch to clone. Mutually exclusive with `tag`. |
| `tag` | `str` | `None` | Tag/release to clone. Mutually exclusive with `branch`. |
| `verbose` | `bool` | `True` | Log progress messages |

**Returns** — `True` on success, `False` on failure.

**Raises** — `ValueError` if both `branch` and `tag` are provided.

**URL validation** — Only URLs from `github.com`, `gitlab.com`, and `bitbucket.org` are accepted, in both HTTPS (`https://host/`) and SSH (`git@host:`) forms. Any other URL returns `False` with an error log.

**Examples**

```python
from pathlib import Path
import scitex as stx

# Clone default branch
stx.git.clone_repo(
    "https://github.com/user/repo",
    Path("./local_repo"),
)

# Clone a specific branch
stx.git.clone_repo(
    "https://github.com/user/repo",
    Path("./local_repo"),
    branch="develop",
)

# Clone a tagged release
stx.git.clone_repo(
    "git@github.com:user/repo.git",
    Path("./local_repo"),
    tag="v2.0.0",
)

# Error: mutually exclusive
stx.git.clone_repo(
    "https://github.com/user/repo",
    Path("./local_repo"),
    branch="main",
    tag="v1.0",
)  # raises ValueError
```

---

## git_init

Initialize a new empty git repository at `repo_path` with `main` as the initial branch name.

```python
git_init(repo_path: Path, verbose: bool = True) -> bool
```

**Returns** — `True` on success. Returns `False` (with a warning log) if `.git` already exists.

Runs `git init -b main` internally.

```python
from pathlib import Path
import scitex as stx

stx.git.git_init(Path("./new_empty_project"))
```
