---
description: Quick reference of schema dataclasses in scitex.schema — PlotSpec, PlotStyle, PlotTheme, StatResult, Encoding, and validation functions.
---

# Schema Reference

All classes below are temporarily accessible from `scitex.schema`. Prefer importing from `scitex.io.bundle`.

## Plot Schemas

| Class | Purpose |
|-------|---------|
| `PlotSpec` | Full plot specification (traces, axes, theme) |
| `PlotStyle` | Per-trace visual style (color, linewidth, marker) |
| `PlotTheme` | Figure-level theme (colors, fonts, margins) |
| `PlotGeometry` | Figure size, DPI, and bounding boxes |
| `TraceSpec` | Single data trace specification |
| `AxesLabels` | X/Y/title labels for an axes |
| `AxesLimits` | X/Y axis limits |

## Stats Schemas

| Class | Purpose |
|-------|---------|
| `StatResult` | Single statistical test result |
| `StatPositioning` | Position of stat annotation on plot |
| `StatStyling` | Visual style for stat annotations |

## Encoding / Theme

| Class | Purpose |
|-------|---------|
| `PlotEncoding` | Channel-to-visual mapping (color=group, size=value) |
| `PlotTheme` | Color scheme + typography + line/marker defaults |

## Validation

```python
from scitex.schema import validate_figure, validate_plot, validate_stat_result, ValidationError

try:
    validate_figure(fig_spec)
except ValidationError as e:
    print(e)
```
