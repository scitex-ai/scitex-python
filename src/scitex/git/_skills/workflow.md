---
description: High-level branch workflow — setup_branches sequences git_add_all, git_commit, git_branch_rename("main"), and git_checkout_new_branch("develop") with rollback on partial failure.
---

# Workflow

## setup_branches

Run a complete "initial commit + standard branch structure" sequence in one call.

```python
setup_branches(
    repo_path: Path,
    template_name: str,
    verbose: bool = True,
) -> bool
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | `Path` | required | Git repository root |
| `template_name` | `str` | required | Used in the initial commit message: `"Initial commit from {template_name}"` |
| `verbose` | `bool` | `True` | Log progress |

**Returns** — `True` if all four steps succeed. `False` if any step fails (with partial rollback, see below).

### What it does

```
git add .
git commit -m "Initial commit from <template_name>"
git branch -M main
git checkout -b develop
```

Delegates to: `git_add_all`, `git_commit`, `git_branch_rename`, `git_checkout_new_branch`.

### Rollback behaviour

If `git_branch_rename` or `git_checkout_new_branch` fails, `setup_branches` calls `git reset --soft HEAD~1` to undo the commit and restore a clean working state. The `add` and `commit` steps do not need rollback because any failure there leaves the repo unchanged.

### Example

```python
from pathlib import Path
import scitex as stx

repo = stx.git.git_init(Path("./new_project"))
if repo:
    stx.git.setup_branches(Path("./new_project"), template_name="my-template")
# Result: repo has commits on 'develop', with 'main' as the base branch
```

### Sequence diagram

```
git_add_all  -->  git_commit  -->  git_branch_rename("main")  -->  git_checkout_new_branch("develop")
                                           |                                   |
                                     FAIL: rollback                      FAIL: rollback
```
