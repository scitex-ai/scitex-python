---
name: stx.bridge
description: Cross-module adapters connecting stx.stats, stx.plt, and visualization models.
---

# stx.bridge

The `stx.bridge` module provides official adapters for converting data between SciTeX modules. It connects statistical results to plot annotations and visualization models using only public APIs with schema validation.

## Python API

```python
import scitex as stx

# Add stat result annotation to a matplotlib axes
stx.bridge.add_stat_to_axes(ax, stat_result)

# Extract stats from axes annotations
stats = stx.bridge.extract_stats_from_axes(ax)

# Convert stat result to annotation dict for vis
annotation = stx.bridge.stat_result_to_annotation(stat_result)

# Check protocol compatibility
stx.bridge.check_protocol_compatibility(version="1.0.0")

# Check FigRecipe integration availability
available = stx.bridge.FIGRECIPE_AVAILABLE
```

## Key Features

- Stats-to-Plt bridges: `add_stat_to_axes`, `extract_stats_from_axes`
- Stats-to-Vis bridges: `stat_result_to_annotation`, `add_stats_to_figure_model`
- Protocol versioning via `BRIDGE_PROTOCOL_VERSION` and `check_protocol_compatibility`
- All bridges use only public APIs of each module
- Optional FigRecipe integration with `FIGRECIPE_AVAILABLE` flag
