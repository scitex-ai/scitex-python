---
name: version-control-release-automation
description: Automation commands and ecosystem-sync CLI for SciTeX version management — scitex-dev ecosystem, dashboard, Python API, MCP tools.
---

# Version Control — Release Automation

Companion to [11_version-control-management.md](11_version-control-management.md). This skill documents the **automation commands** (CLI, MCP, Python API) that support the release workflow.

## Full Ecosystem Update

When user says "update all packages" or "full release", for each package:

1. **Check CI** — verify GitHub Actions pass (`gh run list`).
2. Check commits since last tag and classify (`feat:` → minor, `fix:` → patch).
3. Skip alpha/beta packages unless explicitly requested.
4. For each needing update: bump pyproject.toml → commit → tag → push → gh release → wait for PyPI → pip install -e → fix mismatches → sync to NAS.
5. Use parallel subagents for independent repos.

**Key tools for the full update workflow:**

- `mcp__scitex__dev_ecosystem_list` — initial status check across all packages
- `mcp__scitex__dev_ecosystem_fix_mismatches` — auto-fix installed vs pyproject.toml mismatches after PyPI publish
- CLI equivalent: `scitex-dev ecosystem fix-mismatches --confirm`

## Dashboard

```bash
scitex dev versions list --json
scitex dev versions dashboard       # Web GUI at http://127.0.0.1:5000
```

## CLI Commands

### Read-only

```bash
scitex dev versions list                         # Local + PyPI
scitex dev versions list --json                  # JSON output
scitex dev versions list -p scitex               # Specific package
scitex dev versions list --local-only            # Skip PyPI
scitex dev versions list-hosts                   # SSH host versions
scitex dev versions list-hosts --host nas        # Specific host
scitex dev versions list-remotes                 # GitHub remote versions
scitex dev versions list-rtd                     # Read the Docs status
scitex dev versions check                        # Consistency check
scitex dev versions dashboard                    # Web GUI at http://127.0.0.1:5000
scitex dev versions dashboard --background       # Run as background daemon
scitex dev versions dashboard --stop             # Stop background daemon
```

### Push (local -> remote)

```bash
scitex dev versions sync                         # Preview (dry run)
scitex dev versions sync --confirm               # Execute (parallel)
scitex dev versions sync --confirm --host nas    # Specific host
scitex dev versions sync --confirm -p scitex     # Specific package
scitex dev versions sync --confirm --no-install  # Git pull only
scitex dev versions sync --local --confirm       # Local reinstall
scitex dev versions sync --tags --confirm        # Push tags
```

### Pull (remote -> local)

```bash
scitex dev versions diff                         # Show remote diffs
scitex dev versions commit --host nas --confirm  # Commit remote changes
scitex dev versions pull --confirm               # Git pull all
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `dev_versions_list` | Read-only: list versions |
| `dev_versions_sync` | Push local -> remote (confirm=False for preview) |
| `dev_versions_sync_local` | Reinstall local (confirm=False for preview) |
| `dev_versions_diff` | Read-only: show remote diffs |
| `dev_versions_commit` | Commit remote changes (confirm=False for preview) |
| `dev_versions_pull` | Pull remote -> local (confirm=False for preview) |
| `dev_ecosystem_list` | Read-only: list all ecosystem packages with version status |
| `dev_ecosystem_fix_mismatches` | Auto-fix installed vs pyproject mismatches (confirm=False for preview) |

## Python API

```python
from scitex._dev import sync_all, sync_local, sync_tags
from scitex._dev import remote_diff, remote_commit, pull_local

# Push (preview by default)
sync_all(confirm=True)                    # Parallel across hosts
sync_all(hosts=["nas"], confirm=True)     # Specific host
sync_local(confirm=True)                  # Local reinstall
sync_tags(confirm=True)                   # Push tags

# Pull (preview by default)
diffs = remote_diff()                     # Read-only
remote_commit(host="nas", confirm=True)   # Commit + push
pull_local(confirm=True)                  # Git pull all
```

## Standard Workflow

```bash
# 1. Check both sides
scitex dev versions diff                     # Remote state
scitex dev versions list                     # Version alignment
git status                                   # Local state

# 2. Triage remote changes — read diffs, classify each
scitex dev versions diff --host nas --json
scitex dev versions commit --host nas -p scitex -m "feat: work from NAS" --confirm

# 3. Pull, work, push
scitex dev versions pull --confirm
# ... do local work ...
scitex dev versions sync --confirm

# 4. Verify
scitex dev versions list
scitex dev versions diff                     # Should be clean
```

## Ecosystem-Wide Check

Run `scitex-dev ecosystem list` for the authoritative roster and current version states. Flag mismatches: toml != tag → needs tag. tag != PyPI → needs release/publish.

### Consistency Checker (scitex-dev built-in)

Detects both **version mismatches** (toml != tag != PyPI) and **code-version mismatches** (commits exist since last tag but version not bumped).

```bash
scitex-dev ecosystem fix-mismatches              # Preview mismatches
scitex-dev ecosystem fix-mismatches --confirm    # Fix them
```

Or via MCP: `mcp__scitex__dev_ecosystem_fix_mismatches`.

Python API:

```python
from scitex_dev.versions import get_mismatches, get_commits_since_tag
from scitex_dev.fix import fix_mismatches

mismatches = get_mismatches()                          # {pkg: {status, issues, ...}}
# Issues include: "N commit(s) since vX.Y.Z but version not bumped"
fix_mismatches(confirm=True)                           # Fix all (local + remote)
```

The `commits_since_tag` field in `list_versions()` output tells you how many commits exist since the last tag — if > 0 and version matches tag, a version bump is needed.
