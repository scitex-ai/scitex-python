---
name: stx.git
description: Git repository management utilities for initializing, cloning, branching, committing, inspecting remotes, and retrying flaky operations. Use when programmatically managing git repositories from Python.
---

# stx.git

Python-level git operations. All public functions are importable as `stx.git.<function>` after `import scitex as stx`.

## Sub-skills

### Repository Initialization
- [init.md](init.md) — `init_git_repo`, `find_parent_git`, `create_child_git`, `remove_child_git`: choose between isolated child repo, parent-merge, or origin-preserve strategies

### Cloning and Creation
- [clone.md](clone.md) — `clone_repo` (with optional branch/tag), `git_init`: create or clone repositories

### Staging and Committing
- [commit.md](commit.md) — `git_add_all`, `git_commit`: stage all files and create commits

### Branch Management
- [branch.md](branch.md) — `git_branch_rename`, `git_checkout_new_branch`: rename the current branch or create a new one, with git naming-rule validation

### Remote Inspection
- [remote.md](remote.md) — `get_remote_url`, `is_cloned_from`, `ls_remote`, `get_head_hash`: read remote URLs, compare origins (HTTPS/SSH normalized), query remote refs without cloning

### Retry Logic
- [retry.md](retry.md) — `git_retry`: exponential-backoff retry for `index.lock` conflicts in concurrent workflows

### High-level Workflow
- [workflow.md](workflow.md) — `setup_branches`: one-call sequence for initial commit + `main` + `develop` branch setup with rollback on failure

## Quick reference

```python
import scitex as stx
from pathlib import Path

repo = Path("./my_project")

# Initialize
stx.git.init_git_repo(repo, git_strategy="child")   # isolated repo
stx.git.init_git_repo(repo, git_strategy="parent")  # merge into parent
stx.git.git_init(repo)                              # bare init -b main

# Clone
stx.git.clone_repo("https://github.com/user/repo", repo)
stx.git.clone_repo("https://github.com/user/repo", repo, branch="develop")
stx.git.clone_repo("https://github.com/user/repo", repo, tag="v1.0.0")

# Stage and commit
stx.git.git_add_all(repo)
stx.git.git_commit(repo, "Add experiment results")

# Branch
stx.git.git_branch_rename(repo, "main")
stx.git.git_checkout_new_branch(repo, "feature/new-analysis")

# Remote inspection
url  = stx.git.get_remote_url(repo)
same = stx.git.is_cloned_from(repo, "https://github.com/user/repo")
h    = stx.git.ls_remote("https://github.com/user/repo", ref="main")
h    = stx.git.get_head_hash(repo)

# Retry on lock contention
stx.git.git_retry(lambda: stx.git.git_add_all(repo), max_retries=3)

# Full branch workflow
stx.git.setup_branches(repo, template_name="my-template")
```
