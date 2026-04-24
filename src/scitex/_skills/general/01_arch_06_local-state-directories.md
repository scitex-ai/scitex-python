---
name: arch-local-state-directories
description: Canonical filesystem layout for every scitex-* package's local state — config, logs, caches, PID files, workspace dirs. Two roots (`<project>/.scitex/<pkg-short>/` and `~/.scitex/<pkg-short>/`), project overrides user, always via PathManager.
user-invocable: false
canonical-location: scitex-python/src/scitex/_skills/general/01_arch_06_local-state-directories.md
---

# Local State Directories — Canonical Layout

Every `scitex-*` package that writes anything to disk — config, logs, caches, PID files, databases, workspace dirs — must put it under exactly one of two roots. Same dirname at both scopes, project overrides user, mirrors Claude Code's `~/.claude/` vs `<project>/.claude/`.

## 1. The two roots

| Precedence | Scope | Root | Example (`scitex-scholar`) |
|---|---|---|---|
| higher | **Project** | `<project-root>/.scitex/<pkg-short>/` | `./.scitex/scholar/` |
| lower | **User** | `~/.scitex/<pkg-short>/` | `~/.scitex/scholar/` |

**Project scope always wins.** A package reads project-local state if present and only falls back to the user root when the project file does not exist. CLI flags and env vars override both — see §3.

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

## 4. What goes in the package root

Everything the package writes at runtime lives here:

| File / subdir | Purpose |
|---|---|
| `config.yaml` | Primary config (canonical name — always `config.yaml`, never `<pkg>_config.yaml`) |
| `dashboard.log`, `*.log` | Logs |
| `dashboard.pid`, `*.pid` | PID files for background services |
| `cache/` | Derived / regenerable data |
| `workspace/` | Long-lived package-specific state (browser profiles, scratch dirs) |
| `*.db`, `*.sqlite` | Small embedded DBs (larger ones may relocate with `SCITEX_DIR`) |
| `cli-audit-dict.yaml` | Per-scope linter custom dict (see `03_interface_02_cli.md` §1d) |
| `shared/skills/<pkg>-private/` | Private skill bundle (see `06_skills_03_public-vs-private.md`) |

Subdirectory layout is up to each package, but **no per-package state may live outside its own root**.

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
