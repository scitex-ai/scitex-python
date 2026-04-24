---
name: arch-local-state-directories
description: Canonical filesystem layout for every scitex-* package's local state — config, logs, caches, PID files, workspace dirs. Two roots (`<project>/.scitex/<pkg-short>/` and `~/.scitex/<pkg-short>/`), project overrides user, always via PathManager.
user-invocable: false
canonical-location: scitex-python/src/scitex/_skills/general/01_arch_06_local-state-directories.md
---

# Local State Directories — Canonical Layout

Every `scitex-*` package that writes anything to disk — config, logs, caches, PID files, databases, workspace dirs — must put it under exactly one of two roots. Same dirname at both scopes, project overrides user, mirrors Claude Code's `~/.claude/` vs `<project>/.claude/`.

## 1. The two roots

Every scope carries two parallel trees — one **tracked** (rules / config the team commits) and one **runtime-only** (outputs / logs / caches that must not enter git):

| Precedence | Scope | Root | Example (`scitex-scholar`) | Tracked by git? |
|---|---|---|---|---|
| higher | **Project (tracked)** | `<project-root>/.scitex/<pkg-short>/` | `./.scitex/scholar/` | Yes — config.yaml, custom dicts, skill bundles |
| higher | **Project (runtime)** | `<project-root>/.scitex/<pkg-short>/runtime/` | `./.scitex/scholar/runtime/` | No — only `.gitkeep` + `README.md` committed |
| lower | **User (tracked)** | `~/.scitex/<pkg-short>/` | `~/.scitex/scholar/` | Yes (inside dotfiles repo, if the user versions their home) |
| lower | **User (runtime)** | `~/.scitex/<pkg-short>/runtime/` | `~/.scitex/scholar/runtime/` | No |

**Project scope always wins.** A package reads project-local state if present and only falls back to the user root when the project file does not exist. CLI flags and env vars override both — see §3.

### The `runtime/` subdirectory

Every `<pkg-short>/` root **MUST** contain a `runtime/` subdirectory. This is where the package writes everything that is re-creatable from config + source: logs, PID files, cached downloads, temporary workspaces, SQLite databases, dashboard state, etc.

`runtime/` is intentionally ignored by git. Each package ships two seed files and nothing else:

```
<pkg-short>/runtime/
├── .gitkeep        # Committed so the directory exists in fresh clones
└── README.md       # Committed, one paragraph explaining what lives here
                    #   and pointing at the local-state-directories skill
```

The package's `.gitignore` contains a single line that excludes everything *except* those two files:

```gitignore
# <project-root>/.gitignore (or a nested one inside the package root)
.scitex/*/runtime/*
!.scitex/*/runtime/.gitkeep
!.scitex/*/runtime/README.md
```

Rationale: the dir must exist on first clone (so `PathManager` doesn't have to `mkdir` and accidentally expose permission bugs), but its *contents* must never leak — they are per-host, per-run, often large, and sometimes sensitive. Seeing `runtime/` appear in a `git status` is an immediate signal that something wrote where it shouldn't, or that `.gitignore` was not set up.

## 2. `<pkg-short>` — prefix-stripping rule

`<pkg-short>` is the package name with the `scitex-` prefix removed. Packages that don't carry the prefix use their name as-is.

| Package (pip name) | `<pkg-short>` | Local root |
|---|---|---|
| `scitex-dev` | `dev` | `~/.scitex/dev/` |
| `scitex-scholar` | `scholar` | `~/.scitex/scholar/` |
| `scitex-orochi` | `orochi` | `~/.scitex/orochi/` |
| `scitex-clew` | `clew` | `~/.scitex/clew/` |
| `scitex-cloud` | `cloud` | `~/.scitex/cloud/` |
| `scitex-writer` | `writer` | `~/.scitex/writer/` |
| `scitex-linter` | `linter` | `~/.scitex/linter/` |
| `figrecipe` | `figrecipe` | `~/.scitex/figrecipe/` |
| `crossref-local` | `crossref-local` | `~/.scitex/crossref-local/` |
| `openalex-local` | `openalex-local` | `~/.scitex/openalex-local/` |

## 3. Precedence chain (highest first)

Applies uniformly to config file resolution; packages may extend it to state files when user overrides are sensible.

| # | Source | Example |
|---|---|---|
| 1 | CLI flag | `--config <path>` |
| 2 | Env var | `$SCITEX_<PKG>_CONFIG` |
| 3 | Project scope | `<project>/.scitex/<pkg-short>/config.yaml` |
| 4 | User scope | `~/.scitex/<pkg-short>/config.yaml` |

## 4. What goes where

The package root splits into **tracked** (top-level) and **runtime** (under `runtime/`). The split is the same at both project and user scope.

### 4a. Tracked at the root (`<pkg-short>/`)

Intent: declarative inputs — things the team commits and reviews.

| File / subdir | Purpose |
|---|---|
| `config.yaml` | Primary config (canonical name — always `config.yaml`, never `<pkg>_config.yaml`) |
| `cli-audit-dict.yaml` | Per-scope linter custom dict (see `03_interface_02_cli.md` §1d) |
| `shared/skills/<pkg>-private/` | Private skill bundle (see `06_skills_03_public-vs-private.md`) |
| `runtime/.gitkeep` | Marker so the runtime dir exists in fresh clones |
| `runtime/README.md` | One-paragraph notice explaining why `runtime/` is empty |

### 4b. Runtime-only (`<pkg-short>/runtime/`)

Intent: regenerable outputs — things each host / each run writes for itself, never to be committed.

| File / subdir | Purpose |
|---|---|
| `dashboard.log`, `*.log` | Logs |
| `dashboard.pid`, `*.pid` | PID files for background services |
| `cache/` | Derived / regenerable data |
| `workspace/` | Long-lived package-specific scratch (browser profiles, build outputs) |
| `*.db`, `*.sqlite` | Small embedded DBs (larger ones may relocate with `SCITEX_DIR`) |
| `export/` | Outputs of `scitex-dev skills export` and similar one-shot generators |

Subdirectory layout within `runtime/` is up to each package, but **no per-package state may live outside its own root**.

## 5. Forbidden locations

Do **not** write to any of these — they fragment the layout and break `SCITEX_DIR` relocation:

- `~/.cache/scitex/…` — use `~/.scitex/<pkg-short>/cache/` instead
- `~/.config/scitex/…` — use `~/.scitex/<pkg-short>/config.yaml` instead
- `~/.<pkg>/` (tool's own dotdir at home) — always under `~/.scitex/`
- `./.scitex/<pkg>.yaml` — bare file in project root; use `<project>/.scitex/<pkg-short>/config.yaml` (the project scope is always a directory, never a single file)
- `/tmp/scitex-<pkg>-*` — use `~/.scitex/<pkg-short>/cache/` for transient state that must survive a reboot; `tempfile.TemporaryDirectory()` for ephemeral

## 6. `SCITEX_DIR` — ecosystem-wide relocation

`$SCITEX_DIR` (default `~/.scitex`) is the **single lever** that relocates the user scope atomically. Honouring this is the entire reason we use one shared root instead of per-package dotdirs.

```bash
export SCITEX_DIR=/mnt/fast-ssd/scitex
# Everything under ~/.scitex/* now lives at /mnt/fast-ssd/scitex/*
```

Project scope (`<project>/.scitex/`) is intentionally *not* affected by `SCITEX_DIR` — project state lives with the project.

## 7. Always via `PathManager`, never hardcode

```python
# NO
screenshot_dir = Path.home() / ".scitex/scholar/workspace/screenshots"

# YES
screenshot_dir = (
    ScholarConfig().path_manager.get_cache_engine_dir() / "workspace" / "screenshots"
)
```

Hardcoded paths break when users set `SCITEX_DIR` or the package moves to project scope. `PathManager` consults both scopes in precedence order and returns the resolved path. Child packages should **not** import an upstream package's config to find their own dirs — inject the path as a constructor argument instead (see `01_arch_03_modules-and-standalone-packages.md` §5).

## 8. Migration from legacy layouts

If a package already ships a different layout (`~/.scitex/<pkg>_config.yaml`, `~/.cache/scitex/<pkg>/…`, etc.), migrate once:

1. Add the new location to `PathManager` as primary.
2. On first startup, `mv` old → new and emit a one-time deprecation warning to stderr.
3. Keep the fallback read-path for one minor version, then remove.

Do not keep permanent back-compat shims — legacy locations silently defeat `SCITEX_DIR`.

## 9. Related

- `03_interface_02_cli.md` §6b — config-file resolution uses this layout.
- `01_arch_03_modules-and-standalone-packages.md` §5–§6 — `PathManager` dependency-injection pattern.
- `01_arch_04_environment-variables.md` — `SCITEX_DIR` and per-package `SCITEX_<PKG>_CONFIG`.
- `06_skills_03_public-vs-private.md` — private skills live under `<pkg-short>/shared/skills/`.
