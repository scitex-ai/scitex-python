# SciTeX Version Management

## Dashboard

```bash
scitex dev versions list --json
scitex dev versions dashboard       # Web GUI at http://127.0.0.1:5000
```

## Ecosystem Packages

01. scitex (scitex-python), 02. scitex-cloud, 03. figrecipe,
04. openalex-local, 05. crossref-local, 06. scitex-writer,
07. scitex-dataset, 08. socialia, 09. automated-research-demo,
10. scitex-research-template, 11. pip-project-template, 12. singularity-template
... and growing.

## CLI Commands

### Read-only

```bash
scitex dev versions list                         # Local + PyPI
scitex dev versions list --json                  # JSON output
scitex dev versions list -p scitex               # Specific package
scitex dev versions list-hosts                   # SSH host versions
scitex dev versions list-remotes                 # GitHub remote versions
scitex dev versions list-rtd                     # Read the Docs status
scitex dev versions check                        # Consistency check
```

### Push (local -> remote)

```bash
scitex dev versions sync                         # Preview (dry run)
scitex dev versions sync --confirm               # Execute (parallel)
scitex dev versions sync --confirm --host nas    # Specific host
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

## RULES: Never Sync Blind

1. **NEVER push without checking remote state first** (`diff`)
2. **NEVER pull without checking local state first** (`git status`)
3. **NEVER discard uncommitted changes without reading the diff**
4. **Always classify changes**: improvement (commit), artifact (discard), obsolete (archive)

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

## Version Increment

Format: `vX.Y.Z` (X=Major, Y=Minor, Z=Patch, may have -alpha/-beta suffix).
Auto-determine minor vs patch from diff. No major bumps unless explicitly requested.

```bash
# 1. Edit pyproject.toml: version = "X.Y.Z"
# 2. Commit and tag
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin develop --tags
# 3. Sync
scitex dev versions sync --tags --confirm
scitex dev versions sync --confirm
```

## PyPI Trusted Publisher

```
Repository: ywatanabe1989/<package>
Workflow: publish-pypi.yml
Environment name: pypi
```

## Troubleshooting

### Tag not reachable from current branch

```bash
git tag -d vX.Y.Z                               # Delete local
git tag -a vX.Y.Z -m "Release vX.Y.Z" HEAD      # Retag on HEAD
git push origin vX.Y.Z --force                   # Force-push tag
```

### Merge conflicts on remote hosts

**Always read diff contents before discarding:**

```bash
scitex dev versions diff --host nas -p PACKAGE   # READ FIRST
# If improvement: commit it
scitex dev versions commit --host nas -p PACKAGE -m "preserve: work from NAS" --confirm
# If artifact: safe to discard AFTER confirming
ssh nas "cd ~/proj/PACKAGE && git stash && git pull && git stash pop"
```

### Stale dist-info

```bash
ls ~/.env-3.11/lib/python3.11/site-packages/PACKAGE_NAME-*.dist-info
rm -rf ~/.env-3.11/lib/python3.11/site-packages/PACKAGE_NAME-OLD_VERSION.dist-info
```
