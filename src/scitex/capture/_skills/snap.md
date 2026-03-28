---
description: Take a single screenshot — monitor, app window, URL, or all monitors. Auto-categorizes as stdout/stderr based on content.
---

# snap — Single Screenshot

Primary function for one-shot captures. Defined in `capture/utils.py`.

## Signature

```python
def capture(
    message: str = None,
    path: str = None,
    quality: int = 85,
    auto_categorize: bool = True,
    verbose: bool = True,
    monitor_id: int = 0,
    capture_all: bool = False,
    all: bool = False,          # shorthand for capture_all
    app: str = None,
    url: str = None,
    url_wait: int = 3,
    url_width: int = 1920,
    url_height: int = 1080,
    max_cache_gb: float = 1.0,
) -> str
```

**Public aliases** (all call `capture()` identically):

| Alias | Style |
|-------|-------|
| `capture.snap(...)` | Primary — natural camera action |
| `capture.take(...)` | Alternative phrasing |
| `capture.cpt(...)` | Legacy backwards-compat |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `message` | `None` | Label embedded in output filename |
| `path` | `None` | Explicit save path; auto-generated under `~/.scitex/capture/` if omitted |
| `quality` | `85` | JPEG quality 1-100 |
| `auto_categorize` | `True` | Detect stdout/stderr from content and embed in filename |
| `monitor_id` | `0` | 0-based monitor index (primary = 0) |
| `capture_all` | `False` | Capture all monitors stitched into one image |
| `all` | `False` | Shorthand for `capture_all=True` |
| `app` | `None` | App name to find and capture (e.g. `"chrome"`, `"code"`) |
| `url` | `None` | URL to capture via Playwright headless browser |
| `url_wait` | `3` | Seconds to wait after page load before screenshot |
| `url_width` | `1920` | Viewport width for URL capture |
| `url_height` | `1080` | Viewport height for URL capture |
| `max_cache_gb` | `1.0` | Auto-evict oldest files when cache exceeds this size |

## Returns

`str` — absolute path to the saved screenshot, or `None` on failure.

## Output File Naming

When `path` is not given, the filename is assembled from placeholders:

```
~/.scitex/capture/<timestamp><scope><message><category_suffix>.jpg
```

- `<timestamp>` — `YYYYMMDD_HHMMSS_mmm`
- `<scope>` — empty for primary monitor; `-all-monitors` or `-monitor1` otherwise
- `<message>` — sanitised, first 50 chars of `message` param
- `<category_suffix>` — `-stdout` or `-stderr`

## Capture Priority Order

1. **URL capture** (`url=` set) — uses Playwright (`chromium`, headless). Falls back to Windows-side `capture_url.ps1` in WSL.
2. **App capture** (`app=` set) — calls `get_info()` to find matching window by process name or title, then `capture_window(handle)`.
3. **Monitor capture** (default) — PowerShell scripts for WSL; `mss` or `scrot` fallback for native Linux.

## Auto-categorization

When `auto_categorize=True` the function:

1. Checks `sys.exc_info()` — if inside an exception handler the category is immediately `stderr` and the traceback is appended to `message`.
2. Otherwise reads pixel colors of the captured image (via PIL): >5 % red pixels → `"error"`, >5 % yellow pixels → `"warning"`, else `"stdout"`.

The category is embedded as `[STDOUT]` / `[STDERR]` in the EXIF `UserComment` tag (falls back to a `.txt` sidecar file if PIL is unavailable).

## Examples

```python
from scitex import capture

# Minimal — primary monitor, auto path
capture.snap()

# With label
capture.snap("after_training_epoch_5")

# Specific output path
capture.snap(path="/tmp/debug.jpg")

# All monitors
capture.snap(all=True)

# Secondary monitor
capture.snap(monitor_id=1)

# Capture Chrome window
capture.snap(app="chrome")

# Capture a local web app (Playwright required)
capture.snap(url="http://127.0.0.1:8000", url_wait=5)

# Capture URL without http:// prefix (auto-expanded)
capture.snap(url="localhost:3000")

# Lower quality for smaller files
capture.snap(quality=50)
```

## Installation Notes

- **WSL screen capture**: requires `powershell.exe` accessible from WSL (`/mnt/c/Windows/System32/...` or in `$PATH`).
- **URL capture**: `pip install 'scitex[capture-browser]'` or `pip install playwright && playwright install chromium`.
- **JPEG save / PIL**: `pip install Pillow`.
- **Native Linux fallback**: `pip install mss` or `apt install scrot`.
