# Migrating from stx.canvas to figrecipe

`stx.canvas` is deprecated as of SciTeX 2.16.0. Importing it raises `DeprecationWarning` immediately. All functionality has moved to the `figrecipe` package.

## Installation

```bash
pip install figrecipe
```

## Migration Table

| Old (stx.canvas) | New (figrecipe) |
|------------------|-----------------|
| `stx.canvas.edit(fig)` | `fr.edit(fig)` |
| `stx.canvas.compose(...)` | `fr.compose(...)` |
| `stx.canvas.create_canvas(...)` | `fr.compose(sources=..., canvas_size_mm=...)` |
| `stx.canvas.add_panel(...)` | use `sources` dict in `fr.compose()` |
| `stx.canvas.export_canvas(...)` | `fr.save(fig, path)` |
| `stx.canvas.Canvas` | figrecipe canvas types |

## Interactive GUI Editor

```python
import figrecipe as fr

fig, axes = fr.subplots()
axes[0].plot([1, 2, 3], [4, 5, 6])

# Launch browser-based editor at port 5050
fr.edit(fig)
```

## Multi-panel Composition

```python
import figrecipe as fr

fig, axes = fr.compose(
    sources={
        "panel_a.png": {"xy_mm": (10, 10), "size_mm": (80, 60)},
        "panel_b.png": {"xy_mm": (100, 10), "size_mm": (80, 60)},
    },
    canvas_size_mm=(190, 80),
    panel_labels=True,
)
```

## What Still Works (with Deprecation Warning)

The shim delegates `edit()` and `compose()` to figrecipe when it is installed. Legacy submodules (`backend`, `editor`, `io`) can still be accessed but also emit `DeprecationWarning`.

```python
# This works but warns:
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from scitex.canvas import edit
    edit(fig)  # delegates to fr.edit(fig)
```
