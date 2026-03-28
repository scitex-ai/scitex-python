---
description: MCP tools for screen capture — take screenshots, monitor, create GIFs, inspect windows. Exposed via the unified scitex MCP server.
---

# mcp — MCP Tools

Handlers live in `capture/_mcp/handlers.py`. Registered with the unified scitex
MCP server (`scitex serve`).

The deprecated standalone server in `capture/mcp_server.py` emits a
`DeprecationWarning` on import and should not be used directly.

## Tools

### capture_screenshot

```
capture_screenshot(
    message: str = None,
    monitor_id: int = 0,
    all: bool = False,
    app: str = None,
    url: str = None,
    quality: int = 85,
    return_base64: bool = False,
) -> dict
```

Delegates to `capture.snap(...)`. Returns:

```json
{
  "success": true,
  "path": "/home/user/.scitex/capture/20250823_...-stdout.jpg",
  "category": "stdout",
  "message": "Screenshot saved to ...",
  "timestamp": "2025-08-23T10:45:23.456789",
  "base64": "<base64-encoded-image>"   // only if return_base64=true
}
```

### start_monitoring

```
start_monitoring(
    interval: float = 1.0,
    monitor_id: int = 0,
    capture_all: bool = False,
    output_dir: str = None,
    quality: int = 60,
    verbose: bool = True,
) -> dict
```

Starts `ScreenshotWorker` in background. Returns `{"success": true, ...}`.
Only one monitoring session can run at a time per server instance.

### stop_monitoring

```
stop_monitoring() -> dict
```

Returns `{"success": true, "screenshots_taken": N, "session_id": "..."}`.

### get_monitoring_status

```
get_monitoring_status() -> dict
```

Returns:

```json
{
  "success": true,
  "active": false,
  "cache_dir": "/home/user/.scitex/capture",
  "cache_size_mb": 14.3,
  "screenshot_count": 87
}
```

When monitoring is active also includes `screenshots_taken`, `session_id`.

### analyze_screenshot

```
analyze_screenshot(path: str) -> dict
```

Runs `_detect_category(path)` — pixel-based color heuristic. Returns:

```json
{
  "success": true,
  "path": "...",
  "category": "stdout",
  "is_error": false,
  "size_kb": 45.2
}
```

### list_recent_screenshots

```
list_recent_screenshots(
    limit: int = 10,
    category: str = "all",   // "all" | "stdout" | "stderr"
) -> dict
```

Lists `*.jpg` files in `$SCITEX_DIR/capture`, sorted newest-first.

### clear_cache

```
clear_cache(
    max_size_gb: float = 1.0,
    clear_all: bool = False,
) -> dict
```

`clear_all=True` removes every `*.jpg` in the cache directory.
Otherwise trims oldest files until under `max_size_gb`.

### create_gif

```
create_gif(
    session_id: str = None,      // "latest" or specific ID like "20250823_104523"
    image_paths: list = None,    // explicit file list
    pattern: str = None,         // glob pattern
    output_path: str = None,
    duration: float = 0.5,
    optimize: bool = True,
    max_frames: int = None,
) -> dict
```

One of `session_id`, `image_paths`, or `pattern` must be provided.
Returns `{"success": true, "path": "...", "duration": 0.5}`.

### list_sessions

```
list_sessions(limit: int = 10) -> dict
```

Lists monitoring session IDs (YYYYMMDD_HHMMSS format) found in the capture
directory, newest-first. Returns `{"success": true, "sessions": [...], "count": N}`.

### get_info

```
get_info() -> dict
```

Delegates to `capture.get_info()`. Returns monitor and window data.

### list_windows

```
list_windows() -> dict
```

Returns simplified window list:

```json
{
  "success": true,
  "windows": [
    {"handle": 12345, "title": "Visual Studio Code", "process": "Code.exe"},
    ...
  ],
  "count": 12
}
```

### capture_window

```
capture_window(
    window_handle: int,
    output_path: str = None,
    quality: int = 85,
) -> dict
```

Captures specific window. `window_handle` from `list_windows`.

## MCP Resources

The deprecated standalone `mcp_server.py` exposes screenshots as resources:

```
screenshot://<filename>
```

Returns `image/jpeg` content as base64. The 20 most-recent screenshots are
listed by `list_resources()`.

## Configuration

Cache directory resolves as: `$SCITEX_DIR/capture` if `SCITEX_DIR` is set,
otherwise `~/.scitex/capture`. Migrates automatically from legacy location
`~/.cache/cammy` on first access.
