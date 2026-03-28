---
name: stx.bridge
description: Cross-module adapters connecting stx.stats, stx.plt, and visualization models with protocol versioning.
---

# stx.bridge

The `stx.bridge` module provides official adapters for converting data between SciTeX modules. It connects statistical results to plot annotations and visualization models using only public APIs with schema validation and protocol versioning.

## Sub-skills

- [stats-plt-bridge.md](stats-plt-bridge.md) — `add_stat_to_axes`, `extract_stats_from_axes`, `format_stat_for_plot`
- [figrecipe-bridge.md](figrecipe-bridge.md) — `save_with_recipe`, `load_recipe`, `has_figrecipe`, bundle structure
- [protocol-versioning.md](protocol-versioning.md) — `BRIDGE_PROTOCOL_VERSION`, `check_protocol_compatibility`, `ProtocolInfo`, `COORDINATE_SYSTEMS`

## Quick Reference

```python
import scitex as stx
from scitex.bridge import (
    add_stat_to_axes,
    save_with_recipe,
    load_recipe,
    FIGRECIPE_AVAILABLE,
    BRIDGE_PROTOCOL_VERSION,
    check_protocol_compatibility,
    COORDINATE_SYSTEMS,
)

# Stats -> Plt
result = stx.stats.test_ttest_ind(group1, group2)
add_stat_to_axes(ax, result)

# Save with figrecipe recipe
saved = save_with_recipe(fig, "./my_figure/")

# Protocol version check
is_compat, msg = check_protocol_compatibility("1.0.0")
```

## Module Connections

| Bridge | Source | Target | Key functions |
|--------|--------|--------|---------------|
| Stats-Plt | `stx.stats` | `stx.plt` | `add_stat_to_axes`, `extract_stats_from_axes` |
| Stats-Vis | `stx.stats` | vis models | `stat_result_to_annotation`, `add_stats_to_figure_model` |
| Plt-Vis | `stx.plt` | vis models | `figure_to_vis_model`, `axes_to_vis_axes` |
| FigRecipe | any | figrecipe | `save_with_recipe`, `load_recipe` |
