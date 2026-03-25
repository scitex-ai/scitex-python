---
name: stx.capture.gif
description: Create animated GIFs from monitoring session frames, explicit file lists, or glob patterns.
---

# gif — Animated GIF Creation

Defined in `capture/gif.py` as the `GifCreator` class with four convenience
wrapper functions exported at the module level.

## Public Functions

### create_gif_from_latest_session

```python
def create_gif_from_latest_session(
    screenshot_dir: str = "~/.scitex/capture",
    duration: float = 0.5,
    optimize: bool = True,
    max_frames: int = None,
) -> str | None
```

Finds the most recent session ID in `screenshot_dir` and calls
`create_gif_from_session` on it. Returns GIF path or `None`.

**Public alias**: `capture.gif(...)` and `capture.make_gif(...)`.

### create_gif_from_session

```python
def create_gif_from_session(
    session_id: str,
    output_path: str = None,        # auto: {session_id}_summary.gif
    screenshot_dir: str = "~/.scitex/capture",
    duration: float = 0.5,
    optimize: bool = True,
    max_frames: int = None,
) -> str | None
```

Globs `{session_id}_*.jpg` (then `*.png`) in `screenshot_dir`, sorts
alphabetically, optionally thins to `max_frames` via even stride, and
creates the GIF.

### create_gif_from_files

```python
def create_gif_from_files(
    image_paths: list[str],
    output_path: str,
    duration: float = 0.5,
    optimize: bool = True,
    loop: int = 0,          # 0 = infinite loop
) -> str | None
```

Lowest-level function. Accepts arbitrary image list. Resizes all frames to
match the first frame's dimensions (`Image.Resampling.LANCZOS`). Requires
`Pillow`.

### create_gif_from_pattern

```python
def create_gif_from_pattern(
    pattern: str,           # glob pattern, e.g. "/tmp/frames/*.png"
    output_path: str = None,
    duration: float = 0.5,
    optimize: bool = True,
    max_frames: int = None,
) -> str | None
```

Expands the glob with `glob.glob`, sorts alphabetically, and calls
`create_gif_from_files`. Auto-generates path as
`{pattern_dir}/gif_summary_{timestamp}.gif` if `output_path` is `None`.

## Session ID Discovery

`GifCreator.get_recent_sessions(screenshot_dir)` returns a list of session
IDs (format `YYYYMMDD_HHMMSS`) found in the directory, sorted newest-first.
A session is detected when a file name matches:

```
^(\d{8}_\d{6})_\d{4}_.*\.(jpg|png)$
```

## Frame Thinning

When `max_frames` is set and the file count exceeds it, frames are selected
by even stride: `step = total // max_frames`, then `files[::step][:max_frames]`.

## Dependencies

Requires `Pillow`. Install with:

```
pip install Pillow
```

## Examples

```python
from scitex import capture

# GIF from the most recent monitoring session
path = capture.gif()
# same as:
path = capture.create_gif_from_latest_session()

# Slower playback, cap at 30 frames
path = capture.create_gif_from_latest_session(duration=1.0, max_frames=30)

# GIF from a specific session
path = capture.create_gif_from_session(
    "20250823_104523",
    output_path="/tmp/session_review.gif",
)

# GIF from explicit file list
path = capture.create_gif_from_files(
    image_paths=["/tmp/a.png", "/tmp/b.png", "/tmp/c.png"],
    output_path="/tmp/out.gif",
    duration=0.3,
)

# GIF from glob
path = capture.create_gif_from_pattern(
    "/tmp/experiment/*.jpg",
    output_path="/tmp/experiment.gif",
    max_frames=50,
)
```
