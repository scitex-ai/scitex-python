---
name: stx.plt
description: Publication-quality matplotlib plotting via figrecipe with automatic CSV data export.
---

# stx.plt — index

`scitex.plt` is a thin wrapper over `figrecipe`. All core plotting functionality (`subplots`, `save`, `compose`, `crop`, style management) comes from figrecipe. `stx.plt` sets the brand environment variables, applies scitex auto-configuration on import, adds a color submodule, and provides scitex-specific wrappers for `close()`, `colorbar()`, and `tight_layout()`.

Any attribute not found on `stx.plt` falls through to `matplotlib.pyplot`, making `import scitex.plt as plt` a drop-in replacement.

## Sub-skills

| File | Topic |
|---|---|
| [01_subplots_and_save.md](01_subplots_and_save.md) | `subplots()`, `save()`, `close()`, `reproduce()`, `validate()`, `extract_data()` |
| [02_style_and_auto_config.md](02_style_and_auto_config.md) | Auto-configuration on import, figrecipe style presets, rcParams cascade, DPI utilities |
| [03_color.md](03_color.md) | Named color constants (HEX/RGB/RGBA), converters, cycling, gradients, colormaps |
| [04_composition_and_layout.md](04_composition_and_layout.md) | `compose()`, panel alignment, `crop()`, spec builders, graph visualisation, GUI editor |
| [05_gallery_and_termplot.md](05_gallery_and_termplot.md) | Gallery of all plot types, `termplot` for terminal ASCII output |

## Quick reference

```python
import scitex.plt as plt
import scitex as stx

# Create figure
fig, ax = plt.subplots(width_mm=80, height_mm=60)
ax.plot(x, y, label="signal")
ax.set_xyt("Time (s)", "Amplitude", "EEG")   # figrecipe shorthand

# Save (also writes _data/*.csv sidecar)
stx.io.save(fig, "signal.png")

# Style management
plt.load_style("SCITEX")
plt.list_presets()

# Multi-panel composition
fig, axes = plt.compose(
    sources={"panel_a.png": {"xy_mm": (0, 0), "size_mm": (80, 60)}},
    canvas_size_mm=(90, 70),
    panel_labels=True,
)

# Crop whitespace
plt.crop("figure.png", margin_mm=2)

# Reproduce from recipe
fig = plt.reproduce("outputs/signal.yaml")

# Gallery
plt.gallery.generate("./gallery/")
plt.gallery.list_plots()

# Terminal quick-look
plt.termplot(data_array)

# Color utilities
from scitex.plt import color
color.cycle_color(0)
color.to_hex("blue")
```

## Architecture note

`stx.plt.__init__` re-exports the full figrecipe public API plus local additions:
- `color/` — re-exports `figrecipe.colors` plus `add_hue_col`, `vizualize_colors`
- `styles/` — YAML-based style config with `PriorityConfig` cascade
- `gallery/` — plot type registry and sample generation
- `_auto_config.py` — single-call configuration at import time
- `_figrecipe_integration.py` — `draw_graph()` wrapper (unwraps AxisWrapper)
- `_spec_builders.py` — `build_spec()`, `build_spec_from_csv()` for API/MCP use
- `_render.py` — `render_spec_to_bytes()` for in-memory PNG rendering
- `_tpl.py` — `termplot()` via termplotlib
