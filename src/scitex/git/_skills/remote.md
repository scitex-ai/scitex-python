---
name: git-remote
description: Remote inspection — get_remote_url, is_cloned_from (HTTPS/SSH-normalizing URL comparison), ls_remote (remote commit hash lookup), get_head_hash (local HEAD hash).
---

# Remote Operations

## get_remote_url

Read the URL of a named remote from the repository configuration.

```python
get_remote_url(
    repo_path: Path,
    remote_name: str = "origin",
    verbose: bool = False,
) -> Optional[str]
```

**Returns** — The URL string (stripped), or `None` if the remote does not exist or the path is not a git repo.

```python
from pathlib import Path
import scitex as stx

url = stx.git.get_remote_url(Path("./my_project"))
# "https://github.com/user/repo.git"
```

---

## is_cloned_from

Check whether a local repository was cloned from a specific URL. Normalizes both HTTPS and SSH forms before comparing, so `https://github.com/user/repo` and `git@github.com:user/repo.git` are treated as equal.

```python
is_cloned_from(
    repo_path: Path,
    expected_url: str,
    remote_name: str = "origin",
) -> bool
```

**Returns** — `True` if the normalized actual URL matches the normalized expected URL; `False` otherwise (including when `.git/` is absent or the remote does not exist).

**URL normalization rules applied to both sides:**
1. Strip trailing `/`
2. Convert SSH form `git@host:user/repo` → `https://host/user/repo`
3. Strip `.git` suffix

```python
from pathlib import Path
import scitex as stx

stx.git.is_cloned_from(
    Path("./my_project"),
    "https://github.com/user/repo",
)
# True even if actual remote is "git@github.com:user/repo.git"
```

---

## ls_remote

Query a remote repository for the commit hash of a ref without cloning it (`git ls-remote`).

```python
ls_remote(
    url: str,
    ref: Optional[str] = None,
    verbose: bool = False,
) -> Optional[str]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | required | Remote repository URL |
| `ref` | `str` | `None` | Branch name, tag, or other ref. When `None`, uses `--symref` to get HEAD. |
| `verbose` | `bool` | `False` | Log command output |

**Returns** — A 40-character SHA-1 hash string, or `None` on failure or if no matching ref is found.

```python
import scitex as stx

# HEAD hash of default branch
h = stx.git.ls_remote("https://github.com/user/repo.git")

# Hash of a specific branch
h = stx.git.ls_remote("https://github.com/user/repo.git", ref="main")

# Hash of a tag
h = stx.git.ls_remote("https://github.com/user/repo.git", ref="v1.0.0")
```

---

## get_head_hash

Get the commit hash of the local `HEAD`.

```python
get_head_hash(repo_path: Path, verbose: bool = False) -> Optional[str]
```

**Returns** — A 40-character SHA-1 hash string, or `None` if `repo_path` has no `.git/` directory.

```python
from pathlib import Path
import scitex as stx

h = stx.git.get_head_hash(Path("./my_project"))
# "a1b2c3d4e5f6..."
```

---

## Supported remote hosts

The URL validator (used internally by `clone_repo`) accepts only:
- `github.com`
- `gitlab.com`
- `bitbucket.org`

Both HTTPS (`https://host/…`) and SSH (`git@host:…`) formats are accepted.
