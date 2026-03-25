---
description: How session CONFIG is built from YAML files, session keys, and CLI args; DotDict access patterns; and config persistence.
---

# Session Configuration (CONFIG)

CONFIG is a `scitex.dict.DotDict` assembled by `_lifecycle/_config.py:setup_configs()`
during `start()`. It combines YAML files from `./config/`, session-specific metadata,
and parsed CLI arguments.

## YAML Loading

`setup_configs()` calls `scitex.io.load_configs(IS_DEBUG)` which reads all
`./config/*.yaml` files. Each YAML file is namespaced by its filename (uppercased):

```
./config/
    PARAMS.yaml      ->  CONFIG.PARAMS.*
    IS_DEBUG.yaml    ->  CONFIG.IS_DEBUG (or top-level bool)
    PATHS.yaml       ->  CONFIG.PATHS.*
```

Example `./config/PARAMS.yaml`:

```yaml
lr: 1e-3
n_epochs: 100
batch_size: 32
```

Accessed in code:

```python
@stx.session
def main(CONFIG=stx.INJECTED):
    lr = CONFIG.PARAMS.lr          # 0.001
    epochs = CONFIG['PARAMS']['n_epochs']  # 100 (dict-style also works)
```

## Session Keys Added by `start()`

These keys are always present after `start()`:

```python
CONFIG.ID             # "2025Y-11M-18D-07h53m37s_Z5MR"
CONFIG.PID            # 12345
CONFIG.START_DATETIME # datetime(2025, 11, 18, 7, 53, 37)
CONFIG.FILE           # Path("/path/to/script.py")
CONFIG.SDIR_OUT       # Path("/path/to/script_out")
CONFIG.SDIR_RUN       # Path("/path/to/script_out/RUNNING/2025Y-.../")
```

`CONFIG.DEBUG` is also set from `IS_DEBUG.yaml`; if `True` the session ID has a
`DEBUG_` prefix.

## CLI Args in CONFIG.ARGS

When `args` is passed to `start()` (done automatically by the decorator), parsed
CLI arguments are stored under `CONFIG.ARGS`:

```python
@stx.session
def main(threshold: float = 0.5, CONFIG=stx.INJECTED):
    print(CONFIG.ARGS)          # {'threshold': 0.5}
    print(CONFIG.ARGS.threshold) # 0.5 (DotDict access)
```

## DotDict Access Patterns

Both attribute access and dict access work identically:

```python
CONFIG['ID']        # string
CONFIG.ID           # same thing

CONFIG['PARAMS']['lr']   # nested dict-style
CONFIG.PARAMS.lr         # nested attribute-style
```

## Debug Mode

If `./config/IS_DEBUG.yaml` contains `IS_DEBUG: true`, the session ID is prefixed:

```
DEBUG_2025Y-11M-18D-07h53m37s_Z5MR
```

This propagates to the output directory name so debug runs are visually distinct.

## Config Persistence

At `close()` time, `save_configs()` writes CONFIG to two files in the session
output directory:

```
<SDIR_RUN>/CONFIGS/CONFIG.pkl    # Python pickle (full fidelity)
<SDIR_RUN>/CONFIGS/CONFIG.yaml   # Human-readable YAML snapshot
```

Both files use `track=False` so the verification system does not flag them as
"missing" after the `RUNNING/` → `FINISHED_SUCCESS/` directory move.

## Using CONFIG in the --help Epilog

The decorator's `_create_parser()` reads `./config/*.yaml` at help-time and shows
all variable names and values in the `--help` output under "Global Variables
Injected by @session Decorator". Values longer than 50 characters are truncated
with `...`.
