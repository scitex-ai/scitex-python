---
name: canvas-migration
description: Migrate from deprecated scitex.canvas to figrecipe. Maps edit(), compose(), Canvas, and panel operations to figrecipe equivalents.
---

# Canvas Migration

## Install figrecipe

```bash
pip install figrecipe
```

## API mapping

| Old (scitex.canvas) | New (figrecipe) |
|---------------------|----------------|
| `stx.canvas.edit(fig)` | `fr.edit(fig)` — browser GUI at port 5050 |
| `stx.canvas.compose(...)` | `fr.compose(sources, canvas_size_mm, ...)` |
| `Canvas(...)` | `fr.compose(...)` |
| `add_panel(...)` | `sources={...}` dict in `fr.compose()` |

## Interactive editor

```python
# Old
from scitex.canvas import edit
edit(fig)

# New
import figrecipe as fr
fr.edit(fig)  # launches browser at http://localhost:5050
```

## Multi-panel composition

```python
# Old
stx.canvas.create_canvas("output.png", width=190, height=80)
stx.canvas.add_panel("output.png", "panel_a.png", x=10, y=10, w=80, h=60)
stx.canvas.add_panel("output.png", "panel_b.png", x=100, y=10, w=80, h=60)

# New
import figrecipe as fr

fig, axes = fr.compose(
    sources={
        "panel_a.png": {"xy_mm": (10, 10), "size_mm": (80, 60)},
        "panel_b.png": {"xy_mm": (100, 10), "size_mm": (80, 60)},
    },
    canvas_size_mm=(190, 80),
    panel_labels=True,
)
fr.save(fig, "output.png")
```
