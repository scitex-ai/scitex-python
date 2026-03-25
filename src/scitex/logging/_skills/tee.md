---
name: logging-tee
description: Tee class and tee() function — redirect stdout/stderr to both console and log files simultaneously.
---

# Tee — Stream Multiplexer

Redirects `sys.stdout` and `sys.stderr` to both the original streams and log files. Useful for capturing all terminal output from a script session.

## tee()

```python
sys.stdout, sys.stderr = stx.logging.tee(sys, sdir=None, verbose=True)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sys` | module | required | The `sys` module (pass directly) |
| `sdir` | str or None | `None` | Directory for log files. Defaults to `<calling_script>_out/logs/` |
| `verbose` | bool | `True` | Log the paths where stdout/stderr are being saved |

**Returns** `(sys_stdout, sys_stderr)` — two `Tee` instances wrapping the original streams.

**Log files created**

- `<sdir>/logs/stdout.log` — all stdout
- `<sdir>/logs/stderr.log` — all stderr (progress bar lines filtered out)

**sdir resolution**

When `sdir=None`, `tee()` uses the calling script's filename:
- Script at `/home/user/train.py` → `sdir = /home/user/train_out/`
- IPython → `sdir = /tmp/<USER>_out/`

## Tee class

```python
stx.logging.Tee(stream, log_path, verbose=True)
```

Low-level class that wraps any `TextIO` stream.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `stream` | TextIO | Original stream (`sys.stdout` or `sys.stderr`) |
| `log_path` | str | Path to log file (opened with line buffering) |
| `verbose` | bool | Log the file path via `stx.logging` on open/close |

**Methods**

| Method | Description |
|--------|-------------|
| `write(data)` | Writes to both the original stream and log file. For stderr, filters lines matching progress bar patterns (`\d+%.*\[A*`) |
| `flush()` | Flushes both streams |
| `isatty()` | Delegates to original stream |
| `fileno()` | Delegates to original stream |
| `close()` | Flushes and closes the log file |
| `.buffer` | Property, delegates to original stream's buffer |

## Examples

```python
import sys
import scitex as stx

# Capture both streams for an entire script
sys.stdout, sys.stderr = stx.logging.tee(sys)

print("This goes to console and stdout.log")
# tqdm progress bars are filtered from stderr.log

# Custom output directory
sys.stdout, sys.stderr = stx.logging.tee(sys, sdir="./my_experiment_out")
# Writes to ./my_experiment_out/logs/stdout.log and stderr.log

# Manual Tee for just stdout
import sys
tee_out = stx.logging.Tee(sys.stdout, "/tmp/out.log")
sys.stdout = tee_out
print("Captured")
sys.stdout = tee_out._stream  # restore
tee_out.close()
```

## Notes

- `Tee` uses line buffering (`buffering=1`) so log files are written immediately.
- `tee()` is typically called once at script startup, before any output.
- The `@stx.session` decorator calls `tee()` internally; manual use is only needed outside the session pattern.
