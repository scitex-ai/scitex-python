---
skill: plt.composition_and_layout
description: Multi-panel figure composition, panel alignment, cropping, and spec-based plotting.
---

# stx.plt — composition and layout

## compose — multi-panel publication figures

`compose()` assembles multiple source images or panels into a single canvas with
mm-based positioning.

```python
import scitex.plt as plt

fig, axes = plt.compose(
    sources={
        "panel_a.png": {"xy_mm": (10, 10), "size_mm": (80, 60)},
        "panel_b.png": {"xy_mm": (100, 10), "size_mm": (80, 60)},
    },
    canvas_size_mm=(200, 90),
    panel_labels=True,          # Add A, B, C ... labels
    label_offset_mm=(2, 2),     # Label position relative to panel corner
)
stx.io.save(fig, "Figure1.png")
```

## align_panels / align_smart

```python
# Align a list of axes to the same left edge
plt.align_panels(axes_list, axis="left")

# Smart alignment — infer alignment from panel positions
plt.align_smart(axes_list)

# Alias
plt.smart_align(axes_list)  # same as align_smart
```

## distribute_panels

```python
# Evenly distribute panels along horizontal or vertical axis
plt.distribute_panels(axes_list, axis="x", spacing_mm=5)
```

## crop — trim whitespace from saved images

```python
# Crop whitespace from all sides with a uniform margin
plt.crop("figure.png", margin_mm=2)

# Different margins per side
plt.crop("figure.png", top_mm=5, bottom_mm=5, left_mm=10, right_mm=10)
```

`crop` is re-exported from figrecipe.

## build_spec — construct figrecipe spec dicts programmatically

`build_spec` converts a flat parameter dict into a figrecipe-compatible spec.
It is the spec-building layer used by MCP tools and REST APIs.

```python
from scitex.plt import build_spec, build_spec_from_csv

# From inline data (comma-separated strings)
spec = build_spec({
    "kind": "line",
    "x": "0,1,2,3,4",
    "y": "0,1,4,9,16",
    "title": "Quadratic",
    "xlabel": "x",
    "ylabel": "y²",
    "color": "blue",
})

# Distribution plot with multiple groups
spec = build_spec({
    "kind": "box",
    "data":  "1.2,3.4,2.1,4.5",
    "data2": "2.3,1.1,3.8,2.9",
    "labels": "Control,Treatment",
})

# Supported kinds
from scitex.plt import XY_KINDS, DATA_KINDS, LABEL_KINDS, MATRIX_KINDS, ALL_KINDS
# XY_KINDS:   line, scatter, step, errorbar, stem, bar, barh
# DATA_KINDS: hist, box, boxplot, violin, violinplot
# LABEL_KINDS: pie
# MATRIX_KINDS: heatmap, imshow
```

### build_spec_from_csv

Builds a spec that references columns in an external CSV file — preferred for
MCP tools where data is written first.

```python
spec = build_spec_from_csv(
    "/tmp/data.csv",
    {"kind": "scatter", "x_col": "time", "y_col": "amplitude"},
)
spec = build_spec_from_csv(
    "/tmp/data.csv",
    {"kind": "box", "data_col": "score", "labels": "Group A,Group B"},
)
```

## render_spec_to_bytes

Render a spec dict to PNG bytes (for in-memory use, e.g. MCP image responses):

```python
from scitex.plt import render_spec_to_bytes

spec = build_spec({"kind": "line", "y": "1,2,4,8"})
png_bytes = render_spec_to_bytes(spec)
```

## graph visualization

```python
import networkx as nx
import scitex.plt as plt

G = nx.karate_club_graph()
fig, ax = plt.subplots(width_mm=120, height_mm=100)
result = plt.draw_graph(
    ax, G,
    layout="spring",
    node_color="#3498db",
    edge_color="gray",
    labels=True,
    font_size=6,
)
# result: {"pos": ..., "node_collection": ..., "edge_collection": ...}

# Preset management for graph styles
presets = plt.list_graph_presets()
preset  = plt.get_graph_preset("citation_network")
plt.register_graph_preset("my_preset", {...})
```

## Interactive GUI editor

```python
# Launch browser-based editor for a saved figure recipe
plt.gui("outputs/signal.yaml", port=5050)
plt.edit("outputs/signal.yaml")   # alias for gui
```

## Diagram — flow charts and pipelines

```python
d = plt.Diagram(type="pipeline")
d.add_node("Load data")
d.add_node("Preprocess")
d.add_edge("Load data", "Preprocess")
fig = d.render()
```
