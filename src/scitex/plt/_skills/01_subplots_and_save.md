---
skill: plt.subplots_and_save
description: Create publication-quality figures with subplots(), save figures, reproduce from recipe files.
---

# stx.plt — subplots and save

`stx.plt.subplots()` and `stx.plt.save()` are the two core entry points. Both delegate to `figrecipe`; `stx.plt` sets `FIGRECIPE_BRAND=scitex.plt` before importing figrecipe so error messages and YAML recipes show the scitex branding.

## Creating figures

```python
import scitex.plt as plt

# Standard matplotlib-compatible call
fig, ax = plt.subplots()

# With figrecipe-style mm-based sizing
fig, ax = plt.subplots(
    width_mm=80,
    height_mm=60,
    dpi=300,
)

# Multiple axes
fig, axes = plt.subplots(2, 3, width_mm=180, height_mm=120)

# From a style preset
from scitex.plt.styles import load_style
style = load_style()
fig, ax = plt.subplots(**style)
```

The returned `fig` is a figrecipe `RecordingFigure` that records all plot calls
for CSV export. The returned `ax` / `axes` are figrecipe `AxisWrapper` objects
that are fully matplotlib-compatible.

## Saving figures

```python
# Via stx.plt.save — saves to current working directory
plt.save(fig, "analysis/signal.png")

# Via stx.io.save — uses session-aware path resolution
import scitex as stx
stx.io.save(fig, "signal.png")
# Path resolved relative to script_out/<session_id>/ inside @stx.session

# Save as SVG for vector output
stx.io.save(fig, "signal.svg")

# Save as PDF
stx.io.save(fig, "signal.pdf")
```

Any image save automatically writes `<stem>_data/*.csv` unless `no_csv=True`.

## Closing figures

```python
plt.close(fig)        # RecordingFigure — unwrapped automatically
plt.close()           # close all
plt.close("all")      # matplotlib-style
```

The `close()` function in `scitex.plt` handles both raw `matplotlib.figure.Figure`
and figrecipe `RecordingFigure` wrappers.

## Reproducing from recipe

```python
# Load a saved recipe.yaml and re-render
fig = plt.reproduce("outputs/signal.yaml")

# Alias: load == reproduce
fig = plt.load("outputs/signal.yaml")
```

## Figure validation and data extraction

```python
# Validate a saved figure file or recipe
result = plt.validate("signal.png")

# Extract underlying plot data arrays from a rendered figure
data = plt.extract_data(fig)

# Print summary of figure contents
plt.info(fig)
```

## tight_layout and colorbar

`stx.plt` provides scitex-specific wrappers for two common matplotlib calls:

```python
# tight_layout — silently handles colorbar layout conflicts
plt.tight_layout()

# colorbar — unwraps figrecipe AxisWrapper axes before calling plt.colorbar
cb = plt.colorbar(mappable=im, ax=ax)
```

## matplotlib.pyplot fallback

Any attribute not defined on `stx.plt` falls through to `matplotlib.pyplot`:

```python
import scitex.plt as plt

plt.figure()       # matplotlib.pyplot.figure()
plt.xlabel("X")   # matplotlib.pyplot.xlabel("X")
plt.show()         # matplotlib.pyplot.show()
```

This makes `import scitex.plt as plt` a drop-in replacement for
`import matplotlib.pyplot as plt` in most scripts.
