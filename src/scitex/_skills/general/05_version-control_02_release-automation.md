---
name: version-control-release-automation
description: Ecosystem-wide release automation via `scitex-dev` — the `ecosystem` subcommand tree (`list`, `sync`, `sync-remote`, `fix-mismatches`, `start-dashboard`), the dashboard web UI at `http://localhost:8050` for at-a-glance version reconciliation across all scitex-* packages, the matching Python API in `scitex_dev.ecosystem`, and the MCP tools so agents can drive the same release flow. Complements `05_version-control_01_management.md` (manual workflow) with the automated path used during multi-package release waves. Use when bumping versions across the ecosystem, resolving cross-package version drift, or scripting a release.
---

# Version Control — Release Automation

Companion to [05_version-control_01_management.md](05_version-control_01_management.md). This skill documents the **automation commands** (CLI, MCP, Python API) that support the release workflow.

## Full Ecosystem Update

When user says "update all packages" or "full release", for each package:

1. **Check CI** — verify GitHub Actions pass (`gh run list`).
2. Check commits since last tag and classify (`feat:` → minor, `fix:` → patch).
3. Skip alpha/beta packages unless explicitly requested.
4. For each needing update: bump pyproject.toml → commit → tag → push → gh release → wait for PyPI → pip install -e → fix mismatches → sync to other hosts.
5. Use parallel subagents for independent repos.

**Key tools for the full update workflow:**

- `mcp__scitex__dev_ecosystem_list` — initial status check across all packages
- `mcp__scitex__dev_ecosystem_fix_mismatches` — auto-fix installed vs pyproject.toml mismatches after PyPI publish
- CLI equivalent: `scitex-dev ecosystem fix-mismatches --confirm`

## Dashboard

```bash
scitex-dev ecosystem list --json
scitex-dev ecosystem start-dashboard                      # Web GUI (0.0.0.0:8050)
scitex-dev ecosystem start-dashboard --background         # background process
scitex-dev ecosystem start-dashboard --host 0.0.0.0 --port 8050 --force
```

The dashboard reads `~/.scitex/dev/config.yaml` (or `<project>/.scitex/dev/config.yaml` if present — project overrides user; see `01_arch_06_local-state-directories.md`). Project-scope config.yaml wins when both exist.

## CLI Commands

### Read-only

```bash
scitex-dev ecosystem list                         # Packages with version status
scitex-dev ecosystem list --json                  # JSON output
scitex-dev ecosystem list -p scitex               # Specific package
scitex-dev show-stats                             # Ecosystem-wide stats (count/LOC/tests)
scitex-dev show-config                            # Show resolved dev config
scitex-dev search-docs <query>                    # Search package docs
```

### Sync

```bash
scitex-dev ecosystem sync                         # Local editable reinstall (dry-run default)
scitex-dev ecosystem sync --confirm               # Execute
scitex-dev ecosystem sync-remote --host nas       # Push to remote host over SSH
scitex-dev ecosystem sync-remote --confirm --host all
```

### Fix version mismatches

```bash
scitex-dev ecosystem fix-mismatches               # Preview
scitex-dev ecosystem fix-mismatches --confirm     # Execute
```

Aligns installed version, pyproject toml version, and git tag for every package.

### Utilities

```bash
scitex-dev doctor                                 # Check scitex-dev + dependencies
scitex-dev mcp start                              # Start MCP server for agents
scitex-dev mcp show-installation                  # Print MCP client config
scitex-dev install-tab-completion --shell bash    # Install shell tab-completion
scitex-dev print-tab-completion --shell bash      # Print completion script to stdout
scitex-dev quality audit-cli <package>            # Audit a package's CLI (warn-only)
scitex-dev quality audit-docs                     # Audit docs drift
scitex-dev quality audit-scope                    # Audit test-coverage scope
scitex-dev quality audit-lines                    # Audit per-file line limits
```

## MCP Tools

Mirror the CLI verbs; names follow `dev_<noun>_<verb>` (see `03_interface_03_mcp.md`):

| Tool | Purpose |
|------|---------|
| `dev_ecosystem_list` | List every package with local/toml/git/PyPI version |
| `dev_ecosystem_sync` | Local editable reinstall (confirm=False for preview) |
| `dev_ecosystem_sync_remote` | Push to remote hosts over SSH |
| `dev_ecosystem_fix_mismatches` | Align installed ↔ toml ↔ git tag (confirm=False for preview) |
| `dev_quality_audit_cli` | Per-package noun-verb audit (warn-only) |
| `dev_quality_audit_docs` | Docs-drift audit |
| `dev_show_stats` | Ecosystem stats |
| `dev_show_config` | Resolved dev config |

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

## PyPI Trusted Publisher Setup (one-time per package)

First PyPI release must be a manual `twine upload` (trusted publishing cannot create a *new* project — it can only publish to an *existing* one). After that, configure the trusted publisher so tag-triggered GitHub Actions can publish without tokens.

Per-package settings URL:

```
https://pypi.org/manage/project/<pkg-name>/settings/publishing/
```

Fill in:

| Field | Value |
|---|---|
| PyPI project name | `<pkg-name>` (auto) |
| Owner | `ywatanabe1989` |
| Repository name | `<pkg-name>` |
| Workflow filename | `publish-pypi.yml` |
| Environment name | `pypi` |

**Verify it saved.** After submit, the publisher must appear under **Manage current publishers**. If that list still says "No publishers are currently configured", the save silently failed — re-enter the form. This is the most common cause of `invalid-publisher: Publisher with matching claims was not found` errors on tag push, even when PyPI shows the package existing.

If a tag already failed to publish because trusted-publishing was missing, just `gh run rerun <id>` after configuring — no retag needed.
