---
name: logging-logger
description: SciTeXLogger — enhanced Python logger with success/fail levels, indent, separator, color, and pprint support.
---

# Logger

`stx.logging` replaces the standard `logging.Logger` class with `SciTeXLogger` globally via `setup_logger_class()`. Calling `stx.logging.getLogger(__name__)` returns a `SciTeXLogger` instance.

## getLogger

```python
import scitex as stx

logger = stx.logging.getLogger(__name__)
```

Returns the standard Python logger for the given name, but with the `SciTeXLogger` class which adds extended keyword arguments to every log method.

## Log methods

All methods share the same extended signature:

```python
logger.debug(message, *args, indent=0, sep=None, n_sep=40, c=None, pprint=False, **kwargs)
logger.info(message, *args, indent=0, sep=None, n_sep=40, c=None, pprint=False, **kwargs)
logger.warning(message, *args, indent=0, sep=None, n_sep=40, c=None, pprint=False, **kwargs)
logger.error(message, *args, indent=0, sep=None, n_sep=40, c=None, pprint=False, **kwargs)
logger.critical(message, *args, indent=0, sep=None, n_sep=40, c=None, pprint=False, **kwargs)
logger.success(message, *args, indent=0, sep=None, n_sep=40, c=None, pprint=False, **kwargs)
logger.fail(message, *args, indent=0, sep=None, n_sep=40, c=None, pprint=False, **kwargs)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | any | required | Message to log |
| `indent` | int | `0` | Number of indent levels (each level = 2 spaces in default formatter) |
| `sep` | str or None | `None` | Separator character, e.g. `"="` or `"-"`. Wraps message with `sep * n_sep` lines above and below |
| `n_sep` | int | `40` | Number of separator characters per line |
| `c` | str or None | `None` | Color override name (e.g. `"green"`, `"red"`, `"cyan"`). See color table below |
| `pprint` | bool | `False` | Format `message` with `pprint.pformat` for dicts/objects before logging |

**Custom levels**

| Method | Level value | Level name | Console color |
|--------|-------------|------------|---------------|
| `success()` | 31 | `SUCC` | Green |
| `fail()` | 35 | `FAIL` | Light red |

These sit between `WARNING` (30) and `ERROR` (40).

**Available color names for `c=`**

`black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `grey`, `light_red`, `light_green`, `light_yellow`, `lightblue`, `light_magenta`, `light_cyan`

## Examples

```python
import scitex as stx

logger = stx.logging.getLogger(__name__)

# Basic usage
logger.info("Processing started")
logger.success("Model training complete")
logger.fail("Validation failed")

# Indent for nested steps
logger.info("Step 1", indent=0)
logger.info("Sub-step A", indent=1)
logger.info("Sub-step B", indent=1)

# Separator lines
logger.info("New experiment", sep="=")
# Output:
# INFO: ========================================
# INFO: New experiment
# INFO: ========================================

# Custom color
logger.info("Highlighted path", c="cyan")

# pprint for complex objects
config = {"lr": 0.001, "batch_size": 32, "epochs": 100}
logger.info(config, pprint=True)

# Context manager: log to a specific file
with logger.to("/tmp/session.log"):
    logger.info("This goes to console and /tmp/session.log")
```

## logger.to() — temporary file logging

```python
logger.to(file_path, level=None, mode="w")
```

Context manager. Adds a file handler for the duration of the `with` block, then removes it.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | str | required | Path to log file |
| `level` | int or None | `DEBUG` | Logging level for this handler |
| `mode` | str | `"w"` | File open mode: `"w"` (overwrite) or `"a"` (append) |
