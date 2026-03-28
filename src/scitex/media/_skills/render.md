---
description: Detect media file references in text with render.detect(), display files in terminal/markdown/chat targets with render.show(), and classify file types with render.classify().
---

# Media Render

`from scitex.media import render`

---

## render.detect

Scan a text string for media file references and return structured metadata.

```python
render.detect(text: str, root_path: str | None = None) -> list[dict]
```

```python
from scitex.media import render

text = "Saved /home/user/proj/results/figure.png and data.csv"
refs = render.detect(text, root_path="/home/user/proj")
# [{'type': 'image', 'path': '/home/user/proj/results/figure.png'}, ...]
```

---

## render.show

Display a media file in the specified target environment.

```python
render.show(path: str, target: str = "terminal") -> None
```

| `target` | Output |
|----------|--------|
| `"terminal"` | OSC escape sequence (inline image in terminal) |
| `"markdown"` | `![filename](path)` |
| `"chat"` | Formatted for AI chat pane |

```python
from scitex.media import render

# Display in terminal (requires iTerm2 / Kitty / etc.)
render.show("figure.png")

# Get markdown embed
render.show("figure.png", target="markdown")
```

---

## render.classify

Classify a file by its extension and return a media-type dict.

```python
render.classify(path: str) -> dict
```

```python
from scitex.media import render

info = render.classify("results.csv")
# {'type': 'csv', 'path': 'results.csv', 'ext': '.csv'}

info = render.classify("plot.png")
# {'type': 'image', 'path': 'plot.png', 'ext': '.png'}
```

---

## MEDIA_EXTENSIONS

Dict mapping extension → media type.

```python
from scitex.media.render import MEDIA_EXTENSIONS
print(MEDIA_EXTENSIONS)
# {'.png': 'image', '.jpg': 'image', '.mp4': 'video', '.csv': 'csv', ...}
```

---

## CLI

```bash
python -m scitex.media.render show figure.png --target terminal
python -m scitex.media.render classify data.csv
python -m scitex.media.render detect "Saved /proj/fig.png" --root /proj
```
