---
skill: plt.gallery_and_termplot
description: Plot gallery generation for all supported chart types, and termplot for terminal ASCII plots.
---

# stx.plt — gallery and termplot

## gallery submodule

`stx.plt.gallery` provides a registry of all supported plot types with sample
data, organised by visualisation purpose.

### List available categories and plots

```python
import scitex.plt as plt

# All categories with metadata
cats = plt.gallery.list_plots()
# Returns:
# {
#   "line":         {"name": "Line Plots",       "plots": ["plot", "step", ...]},
#   "statistical":  {"name": "Statistical ...",  "plots": ["stx_mean_std", ...]},
#   "distribution": {"name": "Distributions",    "plots": ["hist", "stx_ecdf", ...]},
#   "categorical":  {"name": "Categorical",      "plots": ["bar", "boxplot", ...]},
#   "scatter":      {"name": "Scatter & Points", "plots": ["scatter", "hexbin", ...]},
#   "area":         {"name": "Area & Fill",      "plots": ["fill_between", ...]},
#   "grid":         {"name": "Grid & Matrix",    "plots": ["imshow", "stx_heatmap", ...]},
#   "contour":      {"name": "Contours",         "plots": ["contour", "contourf", ...]},
#   "vector":       {"name": "Vector Fields",    "plots": ["quiver", "streamplot"]},
#   "special":      {"name": "Special",          "plots": ["pie", "stx_raster", ...]},
# }

# List plots in one category
plots = plt.gallery.list_plots("categorical")
# ["bar", "barh", "stx_bar", "stx_barh", "boxplot", "violinplot", ...]
```

### Generate the full gallery

```python
# Write all example figures (PNG + CSV) to a directory
plt.gallery.generate("./gallery/")

# Generate a single category
plt.gallery.generate("./gallery/", category="line")
```

Each generated figure comes with its own `*_data/*.csv` sidecar file.

### Get spec and data for a specific plot

```python
# Spec dict (can be passed to figrecipe or build_spec)
spec = plt.gallery.get_plot_spec("scatter", "scatter")

# Sample DataFrame for that plot type
df = plt.gallery.get_plot_data("categorical", "boxplot")
```

### Available plot function registry

```python
from scitex.plt.gallery import PLOT_FUNCTIONS

# Dict: plot_name -> function(fig, ax, stx) -> (fig, ax)
print(list(PLOT_FUNCTIONS.keys()))
```

## Gallery categories reference

| Category | Key plots |
|---|---|
| line | `plot`, `step`, `stx_line`, `stx_shaded_line` |
| statistical | `stx_mean_std`, `stx_mean_ci`, `stx_median_iqr`, `errorbar` |
| distribution | `hist`, `hist2d`, `stx_ecdf`, `stx_kde`, `stx_joyplot` |
| categorical | `bar`, `barh`, `boxplot`, `violinplot`, `stx_violin`, `stx_box` |
| scatter | `scatter`, `stem`, `hexbin`, `stx_scatter` |
| area | `fill_between`, `fill_betweenx`, `stx_fillv` |
| grid | `imshow`, `matshow`, `stx_heatmap`, `stx_conf_mat`, `stx_image` |
| contour | `contour`, `contourf` |
| vector | `quiver`, `streamplot` |
| special | `pie`, `stx_raster`, `stx_rectangle` |

## termplot — ASCII terminal plotting

`termplot` renders a quick line plot directly in the terminal using
`termplotlib`. Useful for inspecting arrays without a display.

```python
import numpy as np
import scitex.plt as plt

# Plot y values (x is auto-generated as indices)
plt.termplot(np.sin(np.linspace(0, 2 * np.pi, 50)))

# Plot x, y
t = np.linspace(0, 10, 100)
plt.termplot(t, np.exp(-t) * np.sin(t))
```

`termplot` is `None` if `termplotlib` is not installed.
