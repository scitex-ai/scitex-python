---
description: Control how git is initialized in newly cloned project templates — isolated child repo, parent repo integration, preserved template history, or no git.
---

# Git Strategies

Every project clone function accepts a `git_strategy` parameter that controls how the new project's git history is set up.

## Strategy Reference

| ID | Recommended | Description |
|----|-------------|-------------|
| `"child"` | Yes (default) | Isolated git repo created in project dir; template history stripped |
| `"parent"` | No | Project files added to the nearest ancestor git repo |
| `"origin"` | No | Template's original `.git` directory preserved as-is |
| `None` or `"none"` | No | No git initialization |

## child (default)

Creates a fresh, self-contained git repository inside the project directory.

- Removes the cloned template's `.git`
- Runs `git init` in the project directory
- Creates `main` and `develop` branches
- Makes an initial commit

```python
stx.template.clone_research("./my_project", git_strategy="child")
# Result: ./my_project/.git/ contains fresh history
```

## parent

Adds the project files to the nearest ancestor git repository.

- Removes the template's `.git`
- Finds parent git via `scitex.git.find_parent_git`
- If no parent git found, falls back to `"child"` with a warning

```python
stx.template.clone_research("./my_project", git_strategy="parent")
# Result: project files tracked by surrounding repo (no nested .git)
```

## origin

Preserves the template repository's complete git history.

- Does NOT remove the template's `.git`
- The project retains a `remote origin` pointing to the template GitHub URL
- Useful for tracking template updates via `git fetch origin`

```python
stx.template.clone_research("./my_project", git_strategy="origin")
# Result: .git with full template commit history intact
```

## None / "none"

Clones files only; no git initialization at all.

```python
stx.template.clone_research("./my_project", git_strategy=None)
stx.template.clone_template("research", "./my_project", git_strategy="none")
# MCP also accepts "none" as a string
```

## Listing Strategies Programmatically

```python
# MCP
strategies = await list_git_strategies_handler()
# Returns list of dicts: id, name, description, recommended, preserves_template_history

# Python (construct from template module internals)
from scitex.template._utils._git_strategy import apply_git_strategy, remove_template_git
```

## Implementation Detail

`apply_git_strategy(project_path, git_strategy, template_name)` is called as the last step of `clone_project`. For `"child"` it calls `scitex.git.git_init` then `scitex.git.setup_branches` (creates `main` + `develop` and makes the initial commit).
