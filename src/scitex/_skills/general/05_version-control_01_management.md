<!-- ---
!-- Timestamp: 2026-04-23 08:50:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/_skills/general/05_version-control_01_management.md
!-- --- -->

---
name: version-control-management
description: Core version management workflow — branches, tags, release waves, release gates across the SciTeX ecosystem.
---

# SciTeX Version Management (Core Workflow)

For automation commands and ecosystem-sync CLI details, see the companion skill [05_version-control_02_release-automation.md](05_version-control_02_release-automation.md).

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

## How to Present Choices

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

## Pre-Push CI Check

**Before pushing any release, check GitHub Actions for failures:**

```bash
gh run list -R ywatanabe1989/PACKAGE --limit 5
gh run view RUN_ID -R ywatanabe1989/PACKAGE
```

If CI is failing, fix the issue before bumping version.

## Ecosystem Roster

Run `scitex-dev ecosystem list` for the authoritative current roster (39+ packages). Do not maintain a hand-list here — it drifts immediately.

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

### Also: did consumers grow a new minimum?

If your bump exposes a new API that downstream/middle/upstream packages
already use, those packages' `pyproject.toml` lower bounds must be raised
in the same wave. See [08 § When YOU update a package, bump minima in
consumers](01_arch_02_dependency-and-version-pinning.md#when-you-update-a-package-bump-minima-in-consumers).

Quick check:

```bash
# Which scitex packages import the one you just bumped?
grep -r "^from scitex_io\|^import scitex_io" ~/proj/scitex-*/src \
    | cut -d/ -f5 | sort -u
```

Each hit is a potential minimum-bump candidate — inspect its
`pyproject.toml` to decide if the bound needs to move.

## Version Increment (Core Workflow)

Format: `vX.Y.Z` (X=Major, Y=Minor, Z=Patch, may have -alpha/-beta suffix).

```bash
# 1. Edit pyproject.toml: version = "X.Y.Z"
# 2. Commit and tag
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin develop --tags
# 3. Sync — see 05_version-control_02_release-automation.md for commands
```

## RULES: Never Sync Blind

1. **NEVER push without checking remote state first** (`diff`)
2. **NEVER pull without checking local state first** (`git status`)
3. **NEVER discard uncommitted changes without reading the diff**
4. **Always classify changes**: improvement (commit), artifact (discard), obsolete (archive)

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
scitex dev versions commit --host nas -p PACKAGE -m "preserve: work from NAS" --confirm
ssh nas "cd ~/proj/PACKAGE && git stash && git pull && git stash pop"
```

### Stale dist-info

```bash
ls ~/.env-3.11/lib/python3.11/site-packages/PACKAGE_NAME-*.dist-info
rm -rf ~/.env-3.11/lib/python3.11/site-packages/PACKAGE_NAME-OLD_VERSION.dist-info
```

<!-- EOF -->
