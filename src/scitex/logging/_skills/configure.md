---
name: logging-configure
description: Configure stx.logging — set log level, enable/disable file output, manage rotating log files, and control print capture.
---

# Configuration

## configure()

Primary entry point for logging setup. Called automatically on `import scitex` with defaults.

```python
stx.logging.configure(
    level="info",
    log_file=None,
    enable_file=True,
    enable_console=True,
    capture_prints=False,
    max_file_size=10 * 1024 * 1024,
    backup_count=5,
)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | str or int | `"info"` | Log level: `"debug"`, `"info"`, `"warning"`, `"error"`, `"critical"`, `"success"`, `"fail"` |
| `log_file` | str or None | `None` | Path to log file. Defaults to `~/.scitex/logs/scitex-YYYY-MM-DD.log` |
| `enable_file` | bool | `True` | Write logs to a rotating file |
| `enable_console` | bool | `True` | Write logs to stdout |
| `capture_prints` | bool | `False` | Redirect `print()` calls into the logging system |
| `max_file_size` | int | `10485760` | Rotate log file when it reaches this size in bytes (default: 10 MB) |
| `backup_count` | int | `5` | Number of rotated backup files to keep |

**Behavior**

- Clears all existing handlers before adding new ones (`force=True` on `basicConfig`).
- Uses `RotatingFileHandler` for the file handler.
- Log file directory is created automatically if it does not exist.

## set_level() / get_level()

```python
stx.logging.set_level(level)   # str or int
current = stx.logging.get_level()  # returns int
```

`set_level()` updates the root logger and all its existing handlers to the new level. Accepts both string names (case-insensitive) and integer constants.

## enable_file_logging() / is_file_logging_enabled()

```python
stx.logging.enable_file_logging(enabled=True)
stx.logging.is_file_logging_enabled()  # -> bool
```

Global flag that gates whether `configure()` will attach a file handler. Disabling this before calling `configure()` prevents any file handler from being created even if `enable_file=True`.

## get_log_path()

```python
path = stx.logging.get_log_path()  # -> str or None
```

Returns the `baseFilename` of the first `RotatingFileHandler` on the root logger, or `None` if no file handler is attached.

## Environment variable control

| Variable | Effect |
|----------|--------|
| `SCITEX_LOGGING_LEVEL` | Initial log level (default: `INFO`). Parsed on import. |
| `SCITEX_LOGGING_FORMAT` | Format template: `minimal`, `default`, `detailed`, `debug`, `full` |
| `SCITEX_LOG_FORMAT` | Alias for `SCITEX_LOGGING_FORMAT` |
| `SCITEX_LOGGING_FORCE_COLOR` | `1`/`true`/`yes` forces ANSI colors even when stdout is not a TTY |
| `SCITEX_FORCE_COLOR` | Alias for `SCITEX_LOGGING_FORCE_COLOR` |

## Format templates

| Template | Pattern |
|----------|---------|
| `minimal` | `%(levelname)s: %(message)s` |
| `default` | `%(levelname)s: %(message)s` |
| `detailed` | `%(levelname)s: [%(name)s] %(message)s` |
| `debug` | `%(levelname)s: [%(filename)s:%(lineno)d - %(funcName)s()] %(message)s` |
| `full` | `%(asctime)s - %(levelname)s: [%(filename)s:%(lineno)d - %(name)s.%(funcName)s()] %(message)s` |

File handler always uses the `full` format with timestamp.

## Default log file location

```python
# Resolves to: ~/.scitex/logs/scitex-YYYY-MM-DD.log
# or $SCITEX_DIR/logs/scitex-YYYY-MM-DD.log if SCITEX_DIR is set
stx.logging.get_log_path()
```

## Examples

```python
import scitex as stx

# Change to debug level
stx.logging.set_level("debug")

# Reconfigure with a custom file path
stx.logging.configure(
    level="info",
    log_file="./logs/experiment.log",
    enable_file=True,
    enable_console=True,
)

# Force color output when piping through tee
import os
os.environ["SCITEX_LOGGING_FORCE_COLOR"] = "1"

# Use detailed format for development
os.environ["SCITEX_LOGGING_FORMAT"] = "debug"
```
