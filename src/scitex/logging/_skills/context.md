---
name: logging-context
description: Context managers for scoped file logging — log_to_file() and logger.to().
---

# Context Managers

## log_to_file()

Temporarily routes all log output to a specific file for the duration of a `with` block. The file handler is attached to the root logger and removed on exit.

```python
stx.logging.log_to_file(
    file_path,
    level=logging.DEBUG,
    mode="w",
    formatter=None,
)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | str or Path | required | Path to log file. Parent directory is created if it does not exist |
| `level` | int | `DEBUG` (10) | Minimum level for this handler. Use `stx.logging.INFO` etc. |
| `mode` | str | `"w"` | `"w"` overwrites the file; `"a"` appends |
| `formatter` | `logging.Formatter` or None | `None` | Custom formatter. Defaults to `SciTeXFileFormatter` (timestamped, no color) |

**Yields** the `FileHandler` instance (can be ignored in most cases).

**Behavior**

- Adds a `FileHandler` to the root logger on entry.
- Removes and closes the handler on exit, even if an exception is raised.
- Console logging continues unaffected alongside file logging.
- Uses `SciTeXFileFormatter` by default: `YYYY-MM-DD HH:MM:SS - name - LEVEL - message`.

## Examples

```python
import scitex as stx

logger = stx.logging.getLogger(__name__)

# Route logs to a file for a section of code
with stx.logging.log_to_file("./logs/preprocessing.log"):
    logger.info("Loading dataset")
    logger.success("Dataset loaded: 10000 samples")
    logger.warning("Missing values in column 'age'")

# Append mode — add to existing log
with stx.logging.log_to_file("./logs/experiment.log", mode="a"):
    logger.info("Epoch 5 complete, loss=0.042")

# Capture only warnings and above to a separate file
with stx.logging.log_to_file(
    "./logs/errors_only.log",
    level=stx.logging.WARNING,
):
    logger.info("This goes to console only")
    logger.warning("This goes to console AND errors_only.log")

# Via logger.to() — identical behavior
with logger.to("./logs/session.log"):
    logger.info("This also goes to session.log")
```

## logger.to()

Convenience method on `SciTeXLogger` that delegates to `log_to_file()`.

```python
logger.to(file_path, level=None, mode="w")
```

`level` defaults to `DEBUG` when `None` is passed.

## Nesting

Context managers can be nested. Each adds an independent handler; logs are written to all active handlers:

```python
with stx.logging.log_to_file("./logs/outer.log"):
    logger.info("Goes to console + outer.log")
    with stx.logging.log_to_file("./logs/inner.log"):
        logger.info("Goes to console + outer.log + inner.log")
    logger.info("Back to console + outer.log only")
```
