---
name: stx.session — decorator
description: The @stx.session decorator: automatic CLI generation, session lifecycle, global injection, and error handling for experiment entry points.
---

# @stx.session Decorator

The `@stx.session` decorator (defined in `_decorator.py`) wraps a function into a
self-contained experiment entry point. When the wrapped function is called with no
arguments (i.e., from `if __name__ == "__main__":`), the decorator takes over: it
parses CLI arguments, starts a session, injects globals, runs the function, then
closes the session cleanly.

## Signature

```python
def session(
    func: Callable = None,
    *,
    verbose: bool = False,
    agg: bool = True,
    notify: bool = False,
    sdir_suffix: str = None,
    **session_kwargs,
) -> Callable:
```

## Two Invocation Styles

```python
# Style 1: bare decorator (no options)
@stx.session
def main(threshold: float = 0.5):
    ...

# Style 2: decorator with options
@stx.session(verbose=True, notify=True)
def main(threshold: float = 0.5):
    ...
```

Both are supported. When called with options, `session()` returns a decorator;
when called bare, `session(func)` wraps directly.

## Behavior When Called Without Arguments (CLI Mode)

1. Reads `__file__` from the calling frame to determine the script path.
2. Builds an `argparse.ArgumentParser` from the function signature (see
   [cli-generation.md](cli-generation.md)).
3. Calls `session.start(...)` — sets up output directories, logging, matplotlib,
   `RandomStateManager`, and YAML configs.
4. Injects five globals into the function's module namespace:
   - `CONFIG` — `DotDict` with session ID, paths, YAML data, and parsed args
   - `plt` — `scitex.plt` module, configured for the session
   - `COLORS` — `DotDict` of named colors from `configure_mpl`
   - `rngg` — `RandomStateManager` instance (seed=42 by default)
   - `logger` — `SciTeXLogger` bound to `func.__module__`
5. Executes the function, passing only the parameters it declares (CLI args
   plus any `INJECTED`-defaulted params).
6. On success, return value is used as exit code (int expected; 0 assumed if None).
7. On error, logs exception and re-raises.
8. In the `finally` block, calls `session.close(CONFIG, ...)` regardless of
   outcome, then calls `plt.close("all")`.

## Behavior When Called With Arguments (Direct Mode)

```python
# Bypasses all session management and calls the function directly.
main("/path/to/data.csv", threshold=0.7)
```

The wrapper checks `if args or kwargs:` and short-circuits to `func(*args, **kwargs)`.

## Injected Globals vs Declared Parameters

Parameters whose default is `stx.INJECTED` (the `_InjectedSentinel` instance) are
recognized during injection. They are **skipped** during CLI argument registration
and filled from the injection map at call time.

```python
@stx.session
def main(
    data_path: str,             # Required CLI arg: --data-path
    threshold: float = 0.5,     # Optional CLI arg: --threshold (default 0.5)
    CONFIG=stx.INJECTED,        # Never a CLI arg; injected as CONFIG DotDict
    logger=stx.INJECTED,        # Never a CLI arg; injected as SciTeXLogger
):
    ...
```

Supported injection names and their objects:

| Parameter name | Injected object |
|---|---|
| `CONFIG` | `DotDict` from `start()` |
| `plt` | `scitex.plt` module |
| `COLORS` | `DotDict` of color palette |
| `rngg` | `RandomStateManager` |
| `logger` | `SciTeXLogger` for `func.__module__` |

## Output Directory Suffix

By default the output directory suffix is the function name:

```
script_out/RUNNING/<SESSION_ID>-<func_name>/
```

Override with `sdir_suffix`:

```python
@stx.session(sdir_suffix="experiment_v2")
def main(...):
    ...
# -> script_out/RUNNING/<SESSION_ID>-experiment_v2/
```

## `run()` — Explicit Alternative

`stx.session.run(func, parse_args=None, **session_kwargs)` provides the same
lifecycle without the decorator syntax:

```python
def main(args):
    return 0

if __name__ == "__main__":
    stx.session.run(main)
```

Accepts an optional `parse_args` callable for custom argument parsing.

## Decorator Metadata

The wrapper sets two attributes on the returned callable:

```python
wrapper._func           # Reference to the original unwrapped function
wrapper._is_session_wrapped  # True — lets callers detect session-wrapped functions
```

## Full Script Template

```python
import scitex as stx

@stx.session
def main(
    data_path: str,
    n_iterations: int = 1000,
    threshold: float = 0.5,
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Run analysis on data file.

    This docstring becomes the --help description.
    """
    logger.info(f"Session ID: {CONFIG['ID']}")
    logger.info(f"Output dir: {CONFIG['SDIR_RUN']}")

    data = stx.io.load(data_path)
    result = process(data, threshold=threshold)
    stx.io.save(result, "result.csv")
    return 0  # exit code

if __name__ == "__main__":
    main()
```

CLI usage:
```
python script.py --data-path data.csv --n-iterations 500 --threshold 0.3
python script.py --help
```
