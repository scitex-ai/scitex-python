# FigRecipe Bridge (stx.bridge)

The `_figrecipe` bridge enables saving figures with both SigmaPlot-compatible CSV sidecars and figrecipe YAML recipes for reproducibility.

## Availability Check

```python
from scitex.bridge import FIGRECIPE_AVAILABLE, has_figrecipe

if has_figrecipe():
    print("figrecipe is installed")
# FIGRECIPE_AVAILABLE is a bool constant set at import time
```

## save_with_recipe

Save a figure to a bundle directory (or single file) with optional CSV and recipe sidecar:

```python
from scitex.bridge import save_with_recipe

fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Save to a directory bundle (creates plot.png, plot.csv, recipe.yaml)
saved = save_with_recipe(fig, "./my_figure/", include_csv=True, include_recipe=True)
print(saved)
# {"image": Path("my_figure/plot.png"),
#  "csv": Path("my_figure/plot.csv"),
#  "recipe": Path("my_figure/recipe.yaml")}

# Save as a single image file with sidecars
saved = save_with_recipe(fig, "plot.png", dpi=300)
# Creates: plot.png, plot.csv, plot.yaml
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `path` | required | Directory, `.zip`, or image file path |
| `include_csv` | `True` | Export SigmaPlot-compatible CSV |
| `include_recipe` | `True` | Save figrecipe YAML recipe |
| `data_format` | `"csv"` | Recipe data format: `"csv"`, `"npz"`, or `"inline"` |
| `dpi` | `300` | Image resolution |

## load_recipe

Reproduce a figure from a saved recipe:

```python
from scitex.bridge import load_recipe

# From bundle directory
fig, axes = load_recipe("./my_figure/")

# From recipe.yaml directly
fig, axes = load_recipe("my_figure/recipe.yaml")

# From zip bundle
fig, axes = load_recipe("my_figure.zip")
```

## Bundle Structure

When saving to a directory or zip, the FTS bundle layout is:

```
figure/
├── recipe.yaml      # Source of truth (figrecipe format)
├── plot.csv         # SigmaPlot combined CSV (derived from recorded data)
├── plot.png         # Primary image (derived)
└── meta.yaml        # FTS metadata (optional)
```
