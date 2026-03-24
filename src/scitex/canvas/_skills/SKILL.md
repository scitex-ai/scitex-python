---
name: stx.canvas
description: DEPRECATED - Multi-panel figure composition. Use figrecipe instead.
---

# stx.canvas

The `stx.canvas` module is deprecated as of SciTeX 2.16.0. All functionality has moved to the `figrecipe` package which provides superior multi-panel composition via `figrecipe.compose()` and an interactive GUI editor via `figrecipe.edit()`.

## Python API

```python
# OLD (deprecated - triggers DeprecationWarning on import)
from scitex.canvas import edit
edit(fig)

# NEW - use figrecipe instead
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

## Key Features

- Module is a deprecation shim only — importing raises `DeprecationWarning`
- Migration path: `figrecipe.edit()` for interactive GUI, `figrecipe.compose()` for multi-panel layouts
- Install figrecipe: `pip install figrecipe`
