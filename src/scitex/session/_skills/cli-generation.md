---
name: stx.session — CLI generation
description: How @stx.session auto-generates an ArgumentParser from function signatures, including type inference, short forms, boolean flags, and Literal choices.
---

# Automatic CLI Generation

`_decorator.py:_create_parser(func)` builds an `argparse.ArgumentParser` directly
from the function's signature and type hints. Every parameter that is **not**
`INJECTED`-defaulted becomes a CLI argument.

## How Parameters Map to Arguments

| Python parameter | CLI form |
|---|---|
| `data_path: str` | `--data-path` (underscores become hyphens) |
| `n_epochs: int = 100` | `--n-epochs` with default 100 |
| `verbose: bool = False` | `--verbose` flag (`store_true`) |
| `verbose: bool = True` | `--verbose` flag (`store_false`) |
| `mode: Literal["train","eval"] = "train"` | `--mode` with `choices=["train","eval"]` |
| `CONFIG=stx.INJECTED` | **skipped** — not in CLI |

Parameters without defaults are marked `required=True` in argparse.

## Short Forms

`_generate_short_form(param_name, used_short_forms)` attempts to assign a single-
character short flag (`-x`) to each parameter, avoiding conflicts:

1. First letter of param name (e.g., `data_path` → `-d`)
2. Acronym of snake_case words (e.g., `data_path` → `-dp` if `-d` taken, but only
   if result is a single character)
3. First two letters (`da`)
4. Each character in sequence until an unused one is found
5. No short form if all are taken

`-h` is always reserved for `--help`.

## Type Inference

Types come from `get_type_hints(func)` first, then `param.annotation`, then `str`
as fallback if `inspect.Parameter.empty`.

`typing.Literal` is handled specially: choices are extracted with `get_args()` and
the base type is inferred from the first choice value.

## Help Text in `--help`

The function's docstring becomes the parser `description`. An `epilog` is generated
at help-time that documents all five injected globals with their actual values:

- `CONFIG.ID` — example session ID format
- `CONFIG.FILE` — absolute path to the calling script
- `CONFIG.SDIR_OUT` — computed output base directory
- `CONFIG.SDIR_RUN` — running session subdirectory
- `CONFIG.PID` — current process ID
- YAML config variables from `./config/*.yaml` (loaded and listed with values)
- `COLORS` available keys (loaded from `configure_mpl`)

## Example

Given:

```python
@stx.session
def analyze(
    data_path: str,
    threshold: float = 0.5,
    n_samples: int = 1000,
    mode: Literal["fast", "accurate"] = "fast",
    debug: bool = False,
    CONFIG=stx.INJECTED,
):
    """Analyze dataset."""
    ...
```

Generated CLI:

```
usage: script.py [-h] [-d DATA_PATH] [-t THRESHOLD] [-n N_SAMPLES]
                 [-m {fast,accurate}] [--debug]

Analyze dataset.

options:
  -h, --help            show this help message and exit
  -d DATA_PATH, --data-path DATA_PATH
                        (required)
  -t THRESHOLD, --threshold THRESHOLD
                        (default: 0.5)
  -n N_SAMPLES, --n-samples N_SAMPLES
                        (default: 1000)
  -m {fast,accurate}, --mode {fast,accurate}
                        (default: fast, choices: ['fast', 'accurate'])
  --debug               (default: False)
```

## Accessing Parsed Args in Function

CLI args land in `CONFIG['ARGS']` as a dict:

```python
@stx.session
def main(threshold: float = 0.5, CONFIG=stx.INJECTED):
    print(CONFIG['ARGS'])
    # {'threshold': 0.5}
    print(CONFIG.ARGS.threshold)  # DotDict access also works
```
