---
skill: plt.color
description: Named color constants, converters, cycling, gradients, and colormap utilities from scitex.plt.color.
---

# stx.plt.color

`scitex.plt.color` delegates to `figrecipe.colors` for all core functionality. Two functions (`add_hue_col`, `vizualize_colors`) are scitex-specific additions not in figrecipe.

## Named color dictionaries

```python
from scitex.plt import color

# All available colors in different formats:
color.HEX       # {"red": "#FF0000", "blue": "#0000FF", ...}
color.RGB       # {"red": (255, 0, 0), ...}
color.RGB_NORM  # {"red": (1.0, 0.0, 0.0), ...}
color.RGBA      # {"red": (255, 0, 0, 255), ...}
color.RGBA_NORM # {"red": (1.0, 0.0, 0.0, 1.0), ...}

# Full parameter dict (includes RGBA_NORM_FOR_CYCLE etc.)
color.PARAMS

# Default alpha value
color.DEF_ALPHA   # 0.9
```

## Converters

```python
# Any input format → hex string "#RRGGBB"
color.to_hex("red")
color.to_hex((255, 0, 0))
color.to_hex((1.0, 0.0, 0.0))

# Any input → (R, G, B) 0-255
color.to_rgb("#FF0000")

# Any input → (R, G, B, A) 0-255
color.to_rgba("red", alpha=200)

# Modify alpha channel while keeping other channels
rgba = color.update_alpha((1.0, 0.0, 0.0, 0.5), new_alpha=1.0)
```

## Color cycling

```python
# Cycle through the SciTeX color palette by index
c = color.cycle_color(0)   # first colour
c = color.cycle_color(1)   # second colour
c = color.cycle_color(2)   # etc.
```

## Gradients and interpolation

```python
import numpy as np

# Gradiate from one color toward another
gradient = color.gradiate_color("blue", n=10, target="white")

# Interpolate between two colors
mid = color.interpolate("red", "blue", t=0.5)

# Return a callable that interpolates between two colors
fn = color.gen_interpolate("red", "blue")
c  = fn(0.3)   # 30% from red toward blue
```

## Colormap utilities

```python
# Get a single color from a matplotlib colormap
c = color.get_color_from_cmap("viridis", value=0.5)

# Get N evenly spaced colors from a colormap
palette = color.get_colors_from_cmap("plasma", n=5)

# Get N categorical colors from a colormap
cats = color.get_categorical_colors_from_cmap("tab10", n=4)
```

## scitex-specific extras

### add_hue_col

Utility for seaborn-style plotting. Adds a `hue` column to a DataFrame and
appends a NaN sentinel row so seaborn renders a second colour without extra data:

```python
import pandas as pd
from scitex.plt.color import add_hue_col

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
df_hued = add_hue_col(df)
# df_hued has a "hue" column (0 for real rows, 1 for sentinel)
```

### vizualize_colors

Display the full colour palette as a matplotlib figure:

```python
from scitex.plt.color import vizualize_colors

fig = vizualize_colors()
fig.savefig("palette.png")
```
