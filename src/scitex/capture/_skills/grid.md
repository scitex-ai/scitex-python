---
name: stx.capture.grid
description: Draw coordinate grids, monitor boundaries, and cursor-position markers on screenshots to help with UI automation and coordinate debugging.
---

# grid — Visual Overlays for Coordinate Debugging

Defined in `capture/grid.py`. NOT re-exported by `capture/__init__.py`; import
directly from the submodule.

## draw_grid_overlay

```python
from scitex.capture.grid import draw_grid_overlay

def draw_grid_overlay(
    filepath: str,
    grid_spacing: int = 100,
    output_path: str = None,        # default: {stem}_grid{ext}
    grid_color: tuple = (255, 0, 0),   # red lines
    text_color: tuple = (255, 255, 0), # yellow labels
    line_width: int = 1,
    show_coordinates: bool = True,
) -> str
```

Draws a pixel-coordinate grid directly on the image. X labels appear at the
top of each vertical line; Y labels appear at the left of each horizontal line.
Modifies a copy — the original file is overwritten only if `output_path` is the
same as `filepath`.

Requires `Pillow`. Raises `ImportError` if not installed.

## add_monitor_info_overlay

```python
from scitex.capture.grid import add_monitor_info_overlay

def add_monitor_info_overlay(
    filepath: str,
    monitor_info: dict,             # from capture.get_info()
    output_path: str = None,        # default: {stem}_monitors{ext}
) -> str
```

Draws colored rectangles around each monitor's region in a multi-monitor
combined screenshot. Labels include `Monitor N: WxH @ (X,Y) [PRIMARY]`.

Colors cycle through red, green, blue, yellow, magenta, cyan.

Pass the raw dict returned by `capture.get_info()` as `monitor_info`.

## draw_cursor_overlay

```python
from scitex.capture.grid import draw_cursor_overlay

def draw_cursor_overlay(
    filepath: str,
    cursor_pos: tuple = None,       # (x, y) system coords; auto-detected if None
    output_path: str = None,        # default: {stem}_cursor{ext}
    marker_color: tuple = (0, 255, 0),  # green crosshair
    marker_size: int = 20,
    show_coords: bool = True,
    capture_mode: str = "all",      # "all" or "0", "1", ...
) -> str
```

Draws a crosshair + center dot at the cursor's position translated into image
coordinates. Handles multi-monitor coordinate offsets automatically:

- `capture_mode="all"` — offsets by `(min_x, min_y)` across all monitors.
- `capture_mode="N"` — offsets by the Nth monitor's `(X, Y)` position.

Also shows: `Mon:<n> Sys:(sx,sy) Img:(ix,iy)` text label next to the marker.
If the cursor is outside the image bounds, a red note is drawn at the bottom.

Cursor position is fetched via PowerShell (`GetCursorPos` from `user32.dll`).

## get_display_info (grid module)

```python
from scitex.capture.grid import get_display_info

def get_display_info() -> dict
```

A lightweight alternative to `capture.get_info()`. Uses
`System.Windows.Forms.Screen.AllScreens` and returns:

```python
{
    "monitors": [
        {"Name": str, "Primary": bool, "X": int, "Y": int, "Width": int, "Height": int},
        ...
    ],
    "dpi_scale": float,   # e.g. 1.25 for 125 %
    "dpi_percent": int,   # e.g. 125
}
```

## Examples

```python
from scitex import capture
from scitex.capture.grid import (
    draw_grid_overlay,
    add_monitor_info_overlay,
    draw_cursor_overlay,
)

# 1. Take a screenshot and overlay a 200-px grid
path = capture.snap()
grid_path = draw_grid_overlay(path, grid_spacing=200)
print(f"Grid overlay: {grid_path}")

# 2. Annotate monitor boundaries on an all-monitor capture
all_path = capture.snap(all=True)
info = capture.get_info()
annotated = add_monitor_info_overlay(all_path, info)

# 3. Mark where the cursor is right now
cursor_path = draw_cursor_overlay(path, capture_mode="0")

# 4. Supply cursor coords explicitly (useful for testing)
cursor_path = draw_cursor_overlay(path, cursor_pos=(960, 540))
```

## Dependencies

All functions require `Pillow`. Font detection tries common system paths
(DejaVu, Liberation, FreeMono on Linux; Consolas/Courier on Windows; Monaco/Menlo
on macOS) then falls back to `ImageFont.load_default()`.
