---
name: stx.media
description: Media handling — detect file paths in text, classify by type, and render to terminal/chat/markdown.
---

# stx.media — Skills Index

The `stx.media` module provides utilities for detecting, classifying, and displaying media files. It is organized into the `render` submodule.

## Sub-skills

| File | Description |
|------|-------------|
| [render-detect-classify-show.md](render-detect-classify-show.md) | Detect paths in text, classify by type, show in terminal/markdown/chat |

## Quick Reference

```python
from scitex.media import render

# Classify a single file
render.classify("fig.png")          # {"type": "image", "path": "fig.png", "ext": ".png"}

# Detect media refs in tool output
refs = render.detect(tool_output, root_path="/home/user/proj")

# Display to terminal (OSC escape)
render.show("fig.png", target="terminal")

# Markdown embed
md = render.show("fig.png", target="markdown")  # "![fig.png](fig.png)"
```

## Exports (via stx.media.render)

- `classify(path)` → `dict | None`
- `detect(text, root_path)` → `list[dict]`
- `show(path, target, root_path, alt)` → `str`
- `MEDIA_EXTENSIONS` — immutable mapping of type → frozenset of extensions
