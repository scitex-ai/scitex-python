---
description: The five globals injected by @stx.session: CONFIG, plt, COLORS, rngg, logger — what they are, how they are created, and how to use them.
---

# Injected Globals

When `@stx.session` runs a function in CLI mode (no arguments), it injects five
objects into the function's module `__globals__` dict **and** passes matching
parameters as keyword arguments to the function if they are declared with
`=stx.INJECTED`.

## The Five Injected Objects

### CONFIG

`DotDict` assembled from YAML files + session metadata. See [config.md](config.md)
for the full key reference.

```python
CONFIG.ID           # session ID string
CONFIG.SDIR_RUN     # Path to the running output directory
CONFIG.PID          # process ID
CONFIG.FILE         # Path to the script
CONFIG.ARGS         # DotDict of parsed CLI arguments
CONFIG.PARAMS.lr    # from ./config/PARAMS.yaml (if it exists)
```

### plt

`scitex.plt` module, configured for the session. This replaces the standard
`matplotlib.pyplot` with scitex's wrapped version. It has the same API but records
plot data for CSV export.

```python
fig, ax = plt.subplots()
ax.plot([1, 2, 3], label="signal")
stx.io.save(fig, "plot.png")   # also writes plot.csv automatically
```

The backend is set to `Agg` automatically in headless/WSL environments (detected
at module load time in `_matplotlib.py`). The `agg=True` parameter on the decorator
is kept for backwards compatibility.

### COLORS

`DotDict` of named color hex strings, sourced from `scitex.plt.utils.configure_mpl`.
`COLORS.gray` is aliased to `COLORS.grey`.

```python
plt.plot(x, y, color=COLORS.blue)
plt.plot(x, y, color=COLORS['red'])
plt.scatter(x, y, c=COLORS.orange)
```

Available keys are listed in `--help` at runtime.

### rngg

`scitex.repro.RandomStateManager` instance, created with `seed=42` by default
(override via `start(seed=N)` or `@stx.session` does not expose seed as a
decorator parameter — use manual `start()` for non-default seeds).

```python
rng_numpy = rngg("numpy_rng")   # creates/retrieves a named numpy Generator
rng_torch = rngg("torch_rng")   # creates/retrieves a named torch Generator

sample = rng_numpy.integers(0, 100, size=10)
```

### logger

`scitex.logging.SciTeXLogger` bound to `func.__module__`. Output goes to both
the terminal (through the tee-wrapped stdout) and to the session log files.

```python
logger.info("Processing started")
logger.warning("Low memory")
logger.error("Failed to load file", exc_info=True)
logger.success("All done")   # SciTeX-specific level
```

## INJECTED Sentinel

`stx.INJECTED` (also `stx.session.INJECTED`) is an instance of `_InjectedSentinel`.
Its only purpose is to mark function parameters that should receive injected values
instead of CLI arguments.

```python
@stx.session
def main(
    data_path: str,          # CLI arg: --data-path (required)
    n: int = 10,             # CLI arg: --n (default 10)
    CONFIG=stx.INJECTED,     # injected — never appears in CLI
    plt=stx.INJECTED,        # injected
    COLORS=stx.INJECTED,     # injected
    rngg=stx.INJECTED,       # injected
    logger=stx.INJECTED,     # injected
):
    ...
```

You do **not** need to declare all five in every function. Declare only those you
actually use.

## Global vs Parameter Injection

The decorator injects into both places simultaneously:

1. `func.__globals__["CONFIG"] = CONFIG` — available as a bare global anywhere
   in the module
2. `filtered_kwargs["CONFIG"] = CONFIG` — passed as a keyword argument to the
   function if it has `CONFIG=stx.INJECTED` in its signature

This means you can access `CONFIG` either as a function parameter or as a module-
level global from helper functions defined in the same file.

```python
@stx.session
def main(CONFIG=stx.INJECTED):
    helper()    # CONFIG is also available here as a module global

def helper():
    print(CONFIG.ID)   # works because CONFIG was injected into __globals__
```
