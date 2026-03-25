---
description: Enumerate monitors, virtual desktops, and visible windows; capture a specific window by handle.
---

# display-info — Monitor and Window Enumeration

Defined in `capture/capture.py` as methods of `CaptureManager` and re-exported
via `capture/__init__.py`.

## get_info

```python
def get_info() -> dict
```

Runs `detect_monitors_and_desktops.ps1` via PowerShell and returns a JSON
structure. Returns `{"error": "..."}` on failure (no exceptions raised).

**Public aliases**: `capture.get_info()`, `capture.list_windows()`,
`capture.get_display_info()` — all identical.

### Return structure

```python
{
    "Monitors": {
        "Count": int,
        "PrimaryMonitor": str,          # device name
        "Details": [
            {
                "DeviceName": str,
                "Bounds": {"X": int, "Y": int, "Width": int, "Height": int},
                "IsPrimary": bool,
            },
            ...
        ],
    },
    "Windows": {
        "VisibleCount": int,
        "Details": [
            {
                "Handle": int,          # use with capture_window()
                "Title": str,
                "ProcessName": str,
                "ProcessId": int,
            },
            ...
        ],
    },
    "VirtualDesktops": {
        "Supported": bool,
        "Note": str,
    },
    "Timestamp": str,                   # ISO-8601
}
```

## capture_window

```python
def capture_window(
    window_handle: int,
    output_path: str = None,
) -> str | None
```

Captures a specific window using `capture_window_by_handle.ps1`. The handle
must be obtained from `get_info()["Windows"]["Details"][n]["Handle"]`.

Returns path to saved screenshot (JPEG by default) or `None` on failure.

Auto-generates path as `/tmp/window_{handle}_{timestamp}.jpg` when
`output_path` is `None`.

## Examples

```python
from scitex import capture

# List all monitors
info = capture.get_info()
for i, mon in enumerate(info["Monitors"]["Details"]):
    b = mon["Bounds"]
    print(f"Monitor {i}: {b['Width']}x{b['Height']} @ ({b['X']},{b['Y']})")

# List visible windows
windows = info["Windows"]["Details"]
for w in windows:
    print(f"[{w['ProcessName']}] {w['Title']}  handle={w['Handle']}")

# Capture the first visible window
if windows:
    handle = windows[0]["Handle"]
    path = capture.capture_window(handle)
    print(f"Saved: {path}")

# Find and capture a specific app
for w in windows:
    if "code" in w["ProcessName"].lower():
        path = capture.capture_window(w["Handle"], output_path="/tmp/vscode.jpg")
        break
```

## Dependency

Requires `powershell.exe` accessible from WSL. The PowerShell scripts live in
`capture/powershell/`:

| Script | Used by |
|--------|---------|
| `detect_monitors_and_desktops.ps1` | `get_info()` |
| `capture_window_by_handle.ps1` | `capture_window()` |
| `capture_single_monitor.ps1` | `snap()` (single monitor) |
| `capture_all_monitors.ps1` | `snap(all=True)` |
| `capture_url.ps1` | `snap(url=...)` WSL fallback |
| `capture_all_desktops.ps1` | Available but not used in public API |
| `enumerate_virtual_desktops.ps1` | Available but not used in public API |
