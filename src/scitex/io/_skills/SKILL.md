---
name: stx.io
description: Universal file I/O for 30+ formats — save and load DataFrames, arrays, figures, and any Python object.
---

# stx.io — index

`scitex.io` is a thin wrapper over the standalone `scitex-io` package. Core format handlers come from `scitex-io`; `save()` and `load()` live here to integrate with `stx.session`, `stx.clew`, `stx.path`, and figure CSV export.

## Sub-skills

| File | Topic |
|---|---|
| [01_save_load.md](01_save_load.md) | `save()` and `load()` — universal I/O, format dispatch, path resolution, image metadata |
| [02_format_registry.md](02_format_registry.md) | Register custom formats, list formats, explore HDF5/Zarr, `load_configs` |
| [03_bundle.md](03_bundle.md) | SciTeX bundle format (`.plot`, `.figure`, `.stats`) — ZIP containers for reproducible outputs |
| [04_special_savers.md](04_special_savers.md) | Typed helpers: `save_image`, `save_mp4`, `save_listed_dfs_as_csv`, metadata embedding |

## Quick reference

```python
import scitex as stx

# Save — format inferred from extension
stx.io.save(df,  "results.csv")
stx.io.save(arr, "data.npy")
stx.io.save(fig, "plot.png")      # also writes plot_data/*.csv
stx.io.save(obj, "model.pkl")

# Load — auto-detects format
df  = stx.io.load("results.csv")
arr = stx.io.load("data.npy")
img, meta = stx.io.load("plot.png")   # image + embedded metadata

# Config loading
CONFIG = stx.io.load_configs("./config/")

# Bundles
stx.io.save(fig, "outputs/signal.plot")   # write bundle directory
stx.io.load("outputs/signal.plot/")       # returns (fig, ax, data)

# HDF5 exploration
stx.io.explore_h5("experiment.h5")
stx.io.has_h5_key("experiment.h5", "results/array")

# File globbing
paths = stx.io.glob("runs/*/metrics.csv")

# Register a custom format
stx.io.register_loader(".myext", my_loader)
stx.io.register_saver(".myext", my_saver)
```

## Architecture note

`save()` and `load()` are defined in `scitex/io/_save.py` and `scitex/io/_load.py`. All individual format handlers (`save_csv`, `save_npy`, `_load_csv`, `_load_npy`, …) come from `scitex_io` and are imported into these files. The registry API (`register_loader`, `register_saver`, `list_formats`, `get_loader`, `get_saver`) is re-exported directly from `scitex_io` in `scitex/io/__init__.py`.
