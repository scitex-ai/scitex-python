---
name: stx.capture.monitor
description: Continuous screenshot monitoring at configurable intervals, with event callbacks and a context-manager Session wrapper.
---

# monitor — Continuous Monitoring

Two-layer API for ongoing capture: the low-level `ScreenshotWorker` thread class
(`capture/capture.py`) and the high-level convenience functions / `Session` context
manager (`capture/utils.py`, `capture/session.py`).

## start_monitor

```python
def start_monitor(
    output_dir: str = "~/.scitex/capture/",
    interval: float = 1.0,
    jpeg: bool = True,
    quality: int = 60,
    on_capture=None,     # callable(filepath: str)
    on_error=None,       # callable(exception)
    verbose: bool = True,
    monitor_id: int = 0,
    capture_all: bool = False,
) -> ScreenshotWorker
```

Returns the running `ScreenshotWorker` instance. The worker runs in a daemon
thread so it is automatically killed when the main process exits.

**Public aliases**: `capture.start(...)` delegates to `start_monitor(...)`.

## stop_monitor

```python
def stop_monitor() -> None
```

Stops the global `CaptureManager` worker. Waits up to 2 seconds for the thread to
join before returning. **Public alias**: `capture.stop()`.

## ScreenshotWorker — internal class

Defined in `capture/capture.py`. Used directly when you need fine-grained control.

```python
class ScreenshotWorker:
    def __init__(
        self,
        output_dir: str = "/tmp/scitex_capture_screenshots",
        interval_sec: float = 1.0,
        verbose: bool = False,
        use_jpeg: bool = True,
        jpeg_quality: int = 60,
        on_capture=None,    # called after each successful capture
        on_error=None,      # called on each capture exception
    )

    def start(self, session_id: str = None) -> None
    def stop(self) -> None
    def get_status(self) -> dict
```

`get_status()` returns:

```python
{
    "running": bool,
    "session_id": str,         # YYYYMMDD_HHMMSS if auto-generated
    "screenshot_count": int,
    "output_dir": str,
    "interval_sec": float,
    "use_jpeg": bool,
    "jpeg_quality": int,
}
```

Output filenames follow: `{session_id}_{count:04d}_{timestamp}.{ext}`

## Session context manager

```python
class Session:
    def __init__(
        self,
        output_dir: str = "~/.scitex/capture/",
        interval: float = 1.0,
        jpeg: bool = True,
        quality: int = 60,
        on_capture=None,
        on_error=None,
        verbose: bool = True,
        monitor_id: int = 0,
        capture_all: bool = False,
    )
```

`__enter__` calls `start_monitor(...)` and returns `self`.
`__exit__` calls `stop_monitor()`. Does **not** suppress exceptions.

**Factory function**: `capture.session(**kwargs)` returns a `Session` object.

## Examples

```python
from scitex import capture

# Simple start / stop
capture.start()
# ... your code ...
capture.stop()

# With configurable interval and callbacks
def on_each(path):
    print(f"New frame: {path}")

worker = capture.start(
    interval=2.0,
    quality=50,
    on_capture=on_each,
)
# worker.get_status() -> {"running": True, "screenshot_count": ..., ...}
capture.stop()

# Context manager (auto start/stop)
with capture.session(interval=0.5, output_dir="/tmp/my_session/") as sess:
    # monitoring runs here
    do_long_running_work()
# monitoring automatically stopped on exit

# All monitors, continuous
with capture.session(capture_all=True, interval=3.0):
    run_experiment()
```

## File Layout

Screenshots saved under `output_dir`:

```
~/.scitex/capture/
  20250823_104523_0000_20250823_104523_123.jpg
  20250823_104523_0001_20250823_104524_456.jpg
  ...
```

The session ID embedded in each filename is used by the GIF creator to
group frames (see `gif.md`).

## Cache Management

`start_monitor` does **not** enforce cache size during monitoring.
Cache trimming runs only inside `capture()` (single-shot) via
`_manage_cache_size(cache_dir, max_cache_gb)`.

To manage cache manually:

```python
from scitex.capture.utils import _manage_cache_size
from pathlib import Path

_manage_cache_size(Path("~/.scitex/capture").expanduser(), max_size_gb=0.5)
```

Files are removed oldest-first until total size is under the limit.
