---
name: stx.canvas
description: DEPRECATED as of 2.16.0 — Multi-panel figure composition. Use figrecipe instead.
---

# stx.canvas

The `stx.canvas` module is **deprecated as of SciTeX 2.16.0**. Importing it raises `DeprecationWarning` immediately. All functionality has moved to the `figrecipe` package.

## Sub-skills

- [migration-to-figrecipe.md](migration-to-figrecipe.md) — Migration table, interactive editor, multi-panel composition with figrecipe

## Quick Migration

```python
# OLD (deprecated — raises DeprecationWarning on import)
from scitex.canvas import edit, compose

# NEW — use figrecipe directly
import figrecipe as fr

# Interactive GUI editor (browser at port 5050)
fr.edit(fig)

# Multi-panel composition
fig, axes = fr.compose(
    sources={
        "panel_a.png": {"xy_mm": (10, 10), "size_mm": (80, 60)},
        "panel_b.png": {"xy_mm": (100, 10), "size_mm": (80, 60)},
    },
    canvas_size_mm=(190, 80),
    panel_labels=True,
)
```

Install: `pip install figrecipe`
