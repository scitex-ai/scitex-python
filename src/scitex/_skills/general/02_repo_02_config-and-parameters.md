---
name: repo-config-and-parameters
description: How SciTeX projects store and inject configuration/parameters into scripts — `./config/*.yaml` as the project-scope config tree, the auto-merged `CONFIG` object that `@stx.session` injects into main(), canonical keys (`PATH`, `PARAMS`, `DEBUG`, plus arbitrary user namespaces), deep-merge semantics (file merge + CLI override + env override), injected `SDIR_OUT`/`SDIR_RUN` path variables for deterministic save/load round trips, and how this integrates with the config-precedence chain in `01_arch_06_local-state-directories.md`. Use when adding parameters to a script, debugging config resolution, or auditing an experiment for reproducibility.
canonical-location: scitex-python/src/scitex/_skills/general/02_repo_02_config-and-parameters.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# `@stx.session` and the `CONFIG` Object

`@stx.session` is the entry-point decorator for any reproducible SciTeX
script. It gives you auto-CLI, structured output dirs, reproducibility
metadata, and — via the injected `CONFIG` object — a single source of
truth for every path, parameter, and identifier in your run.

## Decorator basics

```python
import scitex as stx

@stx.session
def main(
    data_path: str = "./data.csv",
    n_samples: int = 100,
    CONFIG=stx.session.INJECTED,   # YAML-merged + session-resolved
    plt=stx.session.INJECTED,      # Pre-configured matplotlib
    logger=stx.session.INJECTED,   # Session logger
):
    ...
    return 0

if __name__ == "__main__":
    main()
```

## CONFIG anatomy

`CONFIG` is a `DotDict` (attribute + key access both work) containing:

### 1. Session-resolved keys (injected at decorator setup)

| Key | Type | Meaning |
|-----|------|---------|
| `CONFIG.ID` | `str` | Session identifier, e.g. `2026-04-23T21-30-00_Z5MR` |
| `CONFIG.PID` | `int` | Python process id of this run |
| `CONFIG.START_DATETIME` | `datetime` | When the session started |
| `CONFIG.FILE` | `Path` | Absolute path to the caller script |
| `CONFIG.SDIR_OUT` | `Path` | Base output dir, e.g. `analysis_out/` |
| `CONFIG.SDIR_RUN` | `Path` | This run's dir, e.g. `analysis_out/RUNNING/<ID>/` → renamed to `FINISHED_SUCCESS/<ID>/` (or `FINISHED_ERROR/`) on exit |
| `CONFIG.ARGS` | `DotDict` | Parsed CLI args as a DotDict (same keys as the function's parameters) |

### 2. YAML-merged user configs

Every `./config/*.yaml` file is loaded and namespaced by filename
(uppercased, `.yaml` stripped):

```
config/
├── PATH.yaml       → CONFIG.PATH.*
├── MODEL.yaml      → CONFIG.MODEL.*
└── PARAMS.yaml     → CONFIG.PARAMS.*
```

Inside YAML files, keys prefixed with `DEBUG_` are auto-promoted when
`IS_DEBUG=true` (via env or `config/IS_DEBUG.yaml`), so you can ship
lightweight defaults and prod-scale values in the same file.

```yaml
# config/MODEL.yaml
hidden_size: 1024
DEBUG_hidden_size: 32    # used when IS_DEBUG
```

### 3. Frozen snapshot

Once the session starts, `CONFIG` is persisted at:

```
{SDIR_RUN}/CONFIGS/CONFIG.yaml     # Human-readable frozen copy
{SDIR_RUN}/CONFIGS/CONFIG.pkl      # Full Python copy (incl. Path objects)
```

You can audit or re-use the exact parameters any future time.

## Using `CONFIG.SDIR_RUN` for save-load round-trips

```python
@stx.session
def main(CONFIG=stx.session.INJECTED):
    # save() auto-routes relative paths to CONFIG.SDIR_RUN
    stx.io.save(df, "results.csv")

    # To load back by relative name, either:
    df2 = stx.io.load(CONFIG.SDIR_RUN / "results.csv")   # explicit
    # or pass symlink_from_cwd=True at save time (see scitex-io skill)
```

## Why this matters for new users and agents

The most common confusion when starting with SciTeX:

```python
stx.io.save(df, "results.csv")
df = stx.io.load("results.csv")     # ❌ FileNotFoundError
```

`save()` routes by caller context to `CONFIG.SDIR_RUN`, but `load()`
resolves the path as given (cwd-relative). Three idiomatic fixes:

1. Pass `symlink_from_cwd=True` to `save()` — one-liner round trip.
2. Use `CONFIG.SDIR_RUN / "results.csv"` for explicit loading.
3. Capture the `Path` returned by `save()` and pass it to `load()`.

Once you internalize the layout, every session's output is a clean,
timestamped, hash-verifiable directory with frozen parameters — a
strong default for reproducible science.

## CLI + ArgumentParser auto-generation

The same function signature doubles as a CLI:

```bash
$ python analysis.py --help
usage: analysis.py [--data-path DATA_PATH] [--n-samples N_SAMPLES]
$ python analysis.py --data-path experiment.csv --n-samples 200
```

Type hints drive argument parsing; docstring becomes `--help` text.
Parsed args end up in `CONFIG.ARGS`.

## See also

- [scitex-io save/load path resolution](../scitex-io/07_path-resolution.md)
- [scitex-io round-trip gotcha](../scitex-io/01_save-and-load.md)
- [scitex-clew verification DAG](../scitex-clew/SKILL.md)
