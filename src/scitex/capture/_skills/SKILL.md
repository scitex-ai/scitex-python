---
name: stx.capture
description: AI-optimized screen capture with WSL support, multi-monitor, and GIF creation.
---

# stx.capture

The `stx.capture` module provides lightweight screen capture functionality optimized for WSL and Windows environments. It supports single screenshots, multi-monitor capture, continuous monitoring, and GIF creation from capture sessions.

## Python API

```python
import scitex as stx

# Single screenshot with debug label
stx.capture.capture("debug message")

# Capture all monitors
stx.capture.capture(capture_all=True)

# Continuous monitoring
stx.capture.start_monitor()
# ... do work ...
stx.capture.stop_monitor()

# Session-based capture
with stx.capture.session("my_session") as sess:
    stx.capture.capture("step 1")

# Create GIF from captured frames
stx.capture.create_gif_from_latest_session("output.gif")
stx.capture.create_gif_from_pattern("screenshots/*.png", "output.gif")

# Get display info
info = stx.capture.get_info()
```

## Key Features

- `capture(msg, capture_all=False)` — single screenshot with optional label
- `start_monitor()` / `stop_monitor()` — continuous capture at configurable intervals
- `session(name)` — context manager for organized capture sessions
- GIF creation: `create_gif_from_files`, `create_gif_from_pattern`, `create_gif_from_session`
- `get_info()` — enumerate monitors, windows, virtual desktops
- WSL-aware: captures Windows host screen from WSL
