<!-- ---
!-- Timestamp: 2026-03-27 05:32:20
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/_skills/general/version-management.md
!-- --- -->

# SciTeX Version Management

## Version Management Levels

| Level | Scope | Actions | When |
|-------|-------|---------|------|
| 1 | **Local** | Edit `pyproject.toml` → commit → `git tag vX.Y.Z` → push | Every release |
| 2 | **GitHub Release** | Level 1 + `gh release create vX.Y.Z --generate-notes` | Every release |
| 3 | **PyPI** | Level 2 + verify `publish-pypi.yml` triggered (or manual twine) | Public packages |
| 4 | **Hosts** | Level 3 + `scitex dev versions sync --confirm` (NAS, Spartan) | Multi-host packages |
| 5 | **Skills** | Level 4 + `scitex-dev skills export` (stamps MANIFEST.md version) | Packages with `_skills/` |

Pick the highest applicable level. Most packages need Level 4. Packages with `_skills/` directories need Level 5.

**PyPI first-publish caveat**: The first publish requires a manual workflow run with twine to register the project on PyPI. Only after that can you configure the trusted publisher (OIDC) on pypi.org. Subsequent releases are automatic via `publish-pypi.yml`.

### How to Present Choices

When invoked via `/scitex-versions`, investigate current state and present like:

```
Current: scitex-dev v0.4.0
  pyproject.toml: 0.4.0 | tag: v0.4.0 | release: v0.4.0 | PyPI: 0.4.0 | NAS: 0.4.0

Recommendation: Level 4 (Hosts)

  1. Local only
  2. + GitHub Release
  3. + PyPI
  4. + Host sync       <-- recommended
  5. + Skills export
```

Speak the recommendation and numbered choices. Wait for user to select a number, then execute that level.

### Pre-Push CI Check

**Before pushing any release, check GitHub Actions for failures:**

```bash
# Check latest workflow runs for a package
gh run list -R ywatanabe1989/PACKAGE --limit 5
# Check specific run
gh run view RUN_ID -R ywatanabe1989/PACKAGE
```

If CI is failing, fix the issue before bumping version. This prevents releasing broken code and gives an opportunity to fix CI before the release.

### Full Ecosystem Update

When user says "update all packages" or "full release", for each package:

1. **Check CI** — verify GitHub Actions pass (`gh run list`)
2. Check commits since last tag and classify (feat → minor, fix → patch)
3. Skip alpha/beta packages unless explicitly requested
4. For each needing update: bump pyproject.toml → commit → tag → push → gh release → wait for PyPI → pip install -e → fix mismatches → sync to NAS
5. Use parallel subagents for independent repos

**Key tools for the full update workflow:**

- `mcp__scitex__dev_ecosystem_list` — initial status check across all packages
- `mcp__scitex__dev_ecosystem_fix_mismatches` — auto-fix installed vs pyproject.toml mismatches after PyPI publish
- CLI equivalent: `scitex-dev ecosystem fix-mismatches --confirm`

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

## Should We Increment?

Before bumping, check what changed since last tag:

```bash
git -C ~/proj/PACKAGE log $(git -C ~/proj/PACKAGE describe --tags --abbrev=0)..HEAD --oneline
```

**Increment if**: new commits exist since last tag that change behavior, API, or dependencies.
**Skip if**: only docs, skills, or CI changes (unless you want a release for those).

### Minor vs Patch

| Bump | When |
|------|------|
| **Patch** (Z) | Bug fixes, small improvements, dependency updates |
| **Minor** (Y) | New features, new CLI commands, new API functions |
| **Major** (X) | Breaking changes — only when user explicitly requests |

Auto-determine from `git log`: if any commit starts with `feat:` → minor. Otherwise → patch.

## Version Increment

Format: `vX.Y.Z` (X=Major, Y=Minor, Z=Patch, may have -alpha/-beta suffix).

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

## Ecosystem-Wide Check

Check all packages at once (useful for `/update-scitex all packages`):

```bash
# Quick scan: toml vs tag vs PyPI for all repos
for repo in scitex-python scitex-cloud figrecipe openalex-local crossref-local scitex-writer scitex-dataset socialia scitex-dev; do
  dir=~/proj/$repo
  ver=$(grep '^version' "$dir/pyproject.toml" 2>/dev/null | head -1 | sed 's/.*"\(.*\)"/\1/')
  tag=$(git -C "$dir" tag --sort=-v:refname 2>/dev/null | head -1)
  printf "%-20s toml=%-10s tag=%s\n" "$repo" "$ver" "$tag"
done
```

Or via MCP: `mcp__scitex__dev_ecosystem_list`

Flag mismatches: toml != tag → needs tag. tag != PyPI → needs release/publish.

### Consistency Checker (scitex-dev built-in)

Detects both **version mismatches** (toml != tag != PyPI) and **code-version mismatches** (commits exist since last tag but version not bumped).

```bash
scitex-dev ecosystem fix-mismatches              # Preview mismatches
scitex-dev ecosystem fix-mismatches --confirm    # Fix them
```

Or via MCP: `mcp__scitex__dev_ecosystem_fix_mismatches`

Python API:
```python
from scitex_dev.versions import get_mismatches, get_commits_since_tag
from scitex_dev.fix import fix_mismatches

mismatches = get_mismatches()                          # {pkg: {status, issues, ...}}
# Issues include: "N commit(s) since vX.Y.Z but version not bumped"
fix_mismatches(confirm=True)                           # Fix all (local + remote)
```

The `commits_since_tag` field in `list_versions()` output tells you how many commits exist since the last tag — if > 0 and version matches tag, a version bump is needed.

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

<!-- EOF -->
