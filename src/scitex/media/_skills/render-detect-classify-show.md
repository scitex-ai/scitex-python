---
description: Detect media file paths in text output, classify by type, and display to terminal, chat, or markdown.
---

# stx.media.render — Detect, Classify, and Show Media

`stx.media.render` provides three focused functions for working with media file references in tool output and scripts.

## classify

Classify a file path by media type based on its extension.

```python
from scitex.media import render

ref = render.classify("figures/plot.png")
# {"type": "image", "path": "figures/plot.png", "ext": ".png"}

ref = render.classify("data.csv")
# {"type": "csv", "path": "data.csv", "ext": ".csv"}

ref = render.classify("unknown.xyz")
# None  — unrecognized extension
```

Supported media types and their extensions:

| Type | Extensions |
|------|-----------|
| `image` | `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.bmp` |
| `audio` | `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`, `.webm` |
| `video` | `.mp4`, `.webm`, `.avi`, `.mov`, `.mkv` |
| `pdf` | `.pdf` |
| `csv` | `.csv`, `.tsv` |
| `plotly` | `.html` |
| `mermaid` | `.mmd`, `.mermaid` |
| `graphviz` | `.dot`, `.gv` |

## detect

Extract media file references from arbitrary text by scanning for absolute paths that start with a given root.

```python
from scitex.media import render

text = "Saved to /home/user/proj/figures/plot.png and /home/user/proj/data.csv"
refs = render.detect(text, root_path="/home/user/proj")
# [
#   {"type": "image", "path": "figures/plot.png", "ext": ".png"},
#   {"type": "csv",   "path": "data.csv",          "ext": ".csv"},
# ]
```

- Deduplicates paths (same path seen twice → one entry)
- Strips trailing punctuation (`.`, `,`, `)`, etc.) from matched paths
- Returns empty list if `root_path` is `None` or `text` is empty

## show

Display a media file to a specific rendering target.

```python
from scitex.media import render

# Terminal: prints OSC escape \033]9998;media:<base64>\007 to stdout
osc = render.show("figure.png", target="terminal")

# Markdown: returns embed string
md = render.show("figure.png", target="markdown")
# "![figure.png](figure.png)"

md = render.show("data.csv", target="markdown")
# "[data.csv](data.csv)"  — non-image types use link syntax

# Chat: returns JSON-encoded MediaRef dict for AI chat SSE stream
import json
ref = json.loads(render.show("figure.png", target="chat", root_path="/home/user/proj"))
# {"type": "image", "path": "figure.png", "ext": ".png"}
```

## CLI

```bash
python -m scitex.media.render show figure.png --target terminal
python -m scitex.media.render classify data.csv
python -m scitex.media.render detect "Saved /proj/fig.png" --root /proj
```

## MEDIA_EXTENSIONS constant

```python
from scitex.media.render import MEDIA_EXTENSIONS

# Immutable mapping: media_type -> frozenset of extensions
print(MEDIA_EXTENSIONS["image"])
# frozenset({'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'})
```
