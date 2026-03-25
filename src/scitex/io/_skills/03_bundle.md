---
skill: io.bundle
description: SciTeX bundle format — structured ZIP/directory containers for plots, figures, and statistical results.
---

# stx.io.bundle

The `bundle` submodule is scitex-specific (not from `scitex-io`). It provides structured containers for reproducible scientific outputs.

## Bundle types

| Extension | Contents |
|---|---|
| `.figure` / `.figure.zip` | Multi-panel publication figure (panels + layout) |
| `.plot` / `.plot.zip` | Single reproducible plot (data + spec + rendered exports) |
| `.stats` / `.stats.zip` | Statistical results (analyses, p-values, effect sizes) |

Bundles exist as either a directory tree or a ZIP archive.

## Basic operations

```python
from scitex.io import bundle

# Load any bundle — returns dict with type-specific keys
data = bundle.load("Figure1.figure.zip")
data = bundle.load("experiment.plot/")
data = bundle.load("analysis.stats.zip")

# Save a dict as a bundle (type inferred from path extension)
bundle.save(data, "output.plot.zip", as_zip=True)

# Copy a bundle
bundle.copy("template.plot.zip", "my_plot.plot")

# Pack a directory into ZIP
bundle.pack("Figure1.figure/", "Figure1.figure.zip")

# Unpack ZIP to directory
bundle.unpack("Figure1.figure.zip", "Figure1.figure/")

# Validate structure
bundle.validate("Figure1.figure.zip")

# Inspect type
btype = bundle.get_type("results.stats.zip")  # BundleType.STATS
```

## Bundle class

```python
from scitex.io.bundle import Bundle

# Open or create
b = Bundle("experiment.plot/", create=True, bundle_type="plot")
b.save()

# Factory from matplotlib figure
from scitex.io.bundle import from_matplotlib
from_matplotlib(fig, "output.plot/", name="signal", dpi=300)
```

## ZipBundle — in-memory ZIP access

```python
from scitex.io.bundle import ZipBundle

with ZipBundle("Figure1.figure.zip") as zb:
    spec = zb.read_json("spec.json")
    data = zb.read_csv("data/signal.csv")
    img_bytes = zb.read_bytes("exports/figure.png")
```

## Nested bundle access

Figures contain child plot bundles. Access them through `bundle.nested`:

```python
preview = bundle.nested.get_preview("Figure1.figure/A.plot")
spec    = bundle.nested.get_json("Figure1.figure/A.plot/spec.json")
```

## Saving figures as bundles

Pass a bundle path (no image extension) to `stx.io.save`:

```python
import scitex as stx

fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Save as bundle directory
stx.io.save(fig, "outputs/signal.plot")

# Save as ZIP bundle
stx.io.save(fig, "outputs/signal.plot.zip")
```

The bundle contains the rendered PNG, plot data CSV, and figrecipe `recipe.yaml`
(if figrecipe is installed).

## Loading plot bundles via stx.io.load

```python
fig, ax, data = stx.io.load("outputs/signal.plot/")
# fig  — matplotlib figure showing the rendered PNG
# ax   — axes (image display axes, not the original)
# data — DataFrame of plot data, or None
```

## Stats bundles

```python
import scitex as stx

result = stx.stats.test_ttest_ind(g1, g2)
stx.stats.save_stats([result], "analysis.stats.zip", as_zip=True)

# Later: load and inspect
data = stx.io.load("analysis.stats.zip")
# data["comparisons"] — list of flat dicts with p_value, effect_size, etc.
```

## Manifest

Every bundle contains a `_manifest.json` that identifies the bundle type:

```python
from scitex.io.bundle import read_manifest, get_type_from_manifest

manifest = read_manifest("Figure1.figure/")
btype    = get_type_from_manifest("Figure1.figure/")
```

## Type constants

```python
from scitex.io.bundle import BundleType, PLOT, FIGURE, STATS

# BundleType enum
BundleType.PLOT     # "plot"
BundleType.FIGURE   # "figure"
BundleType.STATS    # "stats"

# String aliases
PLOT    # "plot"
FIGURE  # "figure"
STATS   # "stats"
```
