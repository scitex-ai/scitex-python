---
skill: io.save_load
description: Universal save/load with format auto-detection, session integration, and clew provenance tracking.
---

# stx.io — save and load

`save()` and `load()` are the two primary entry points in `scitex.io`. Both live in `scitex.io` directly (not delegated to `scitex-io`) because they integrate with `scitex.session`, `scitex.clew`, and `scitex.path`.

## save()

```python
import scitex as stx

# Format inferred from extension — works for any supported type
stx.io.save(df, "results.csv")          # pandas DataFrame
stx.io.save(arr, "weights.npy")         # NumPy array
stx.io.save(model, "model.pkl")         # Any picklable object
stx.io.save(data, "experiment.h5")      # HDF5
stx.io.save(fig, "figure.png")          # Matplotlib figure (+ auto CSV)
stx.io.save({"k": 1}, "cfg.yaml")       # dict to YAML
stx.io.save(text, "notes.md")           # string to text file
```

### Path resolution

When `specified_path` is relative, the save destination depends on context:

| Context | Destination |
|---|---|
| Inside `@stx.session` script | `<script>_out/<session_id>/` |
| Jupyter notebook | `<notebook_name>_out/` |
| IPython / `<stdin>` | `/tmp/<USER>/` |
| Plain script | `<script>_out/` |

Absolute paths are used as-is.

### Key parameters

```python
stx.io.save(
    obj,
    "results/data.csv",
    makedirs=True,          # Create parent dirs (default True)
    verbose=True,           # Log save path and file size (default True)
    dry_run=False,          # Simulate without writing (default False)
    no_csv=False,           # Skip CSV sidecar for figure saves (default False)
    auto_crop=True,         # Auto-crop saved images (default True)
    crop_margin_mm=1.0,     # Crop margin in millimetres (default 1.0)
    symlink_from_cwd=False, # Create symlink from current working dir
    track=True,             # Track file in stx.clew verification system
    register=False,         # Register file hash with remote Clew Registry
)
```

### Supported save formats

| Extension | Type saved |
|---|---|
| `.csv` | DataFrame, list of scalars |
| `.xlsx`, `.xls` | DataFrame |
| `.npy`, `.npz` | NumPy array |
| `.pkl`, `.pickle` | Any picklable object |
| `.pkl.gz` | Pickle compressed |
| `.joblib` | Joblib-serialised object |
| `.pth`, `.pt` | PyTorch tensors / models |
| `.mat` | MATLAB `.mat` file |
| `.cbm` | CatBoost model |
| `.json` | dict / list |
| `.yaml`, `.yml` | dict |
| `.txt`, `.md`, `.py`, `.css`, `.js` | String / text |
| `.tex` | LaTeX source |
| `.bib` | BibTeX bibliography |
| `.html` | HTML string |
| `.hdf5`, `.h5` | HDF5 groups / datasets |
| `.zarr` | Zarr arrays |
| `.mp4` | Video frames |
| `.png`, `.jpg`, `.jpeg`, `.gif`, `.tiff`, `.svg`, `.pdf` | Matplotlib figure |
| `.zip` / no-extension dir | SciTeX bundle |

### Figure saves and automatic CSV export

Saving a Matplotlib figure to an image format triggers CSV export of all tracked plot data:

```python
fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
stx.io.save(fig, "analysis/signal.png")
# Creates: analysis/signal.png
#          analysis/signal_data/*.csv   (plot data columns)
```

The CSV sidecar is generated via `_RecordingFigureDataProxy`, which reads
recorded arrays from the figrecipe `RecordingFigure`. Pass `no_csv=True` to
suppress it.

## load()

```python
data = stx.io.load("results.csv")          # DataFrame
arr  = stx.io.load("weights.npy")          # NumPy array
cfg  = stx.io.load("config.yaml")          # dict
img, meta = stx.io.load("figure.png")      # image array + metadata dict
img  = stx.io.load("figure.png", metadata=False)  # image only
pdf  = stx.io.load("paper.pdf")            # dict with full_text, sections, etc.
text = stx.io.load("notes.md")             # string

# Glob pattern — returns list of loaded objects
frames = stx.io.load("data/*.csv")

# Explicit extension override (for files without extension)
doc = stx.io.load("a4b2c3d1", ext="pdf")
```

### Supported load formats

In addition to all save formats, load supports:

| Extension | Returns |
|---|---|
| `.tsv` | DataFrame |
| `.xlsm`, `.xlsb` | DataFrame |
| `.db` | SQLite data |
| `.docx` | string |
| `.pdf` | dict (full_text, sections, metadata, pages) |
| `.jpg`, `.png`, `.tiff`, `.tif` | `(image_array, metadata_dict)` by default |
| `.vhdr`, `.vmrk`, `.edf`, `.bdf`, `.gdf`, `.cnt`, `.egi`, `.eeg`, `.set` | MNE Raw object |
| `.figure`, `.plot`, `.stats` (ZIP or dir) | SciTeX bundle dict |
| `.xml` | parsed XML |
| `.bib` | BibTeX dict |
| `.con` | Connectivity data |

### Caching

`load()` caches results in memory by default. NumPy files get disk-level caching:

```python
data = stx.io.load("big_file.npy")   # cached after first load
stx.io.clear_load_cache()            # invalidate cache
info = stx.io.get_cache_info()       # inspect cache state
```

Pass `cache=False` to always reload from disk.

### Image metadata

Images saved via `stx.io.save(fig, ...)` have scitex metadata embedded in the
PNG/TIFF metadata fields. `load()` returns a tuple `(image, metadata_dict)` by
default for image files:

```python
img, meta = stx.io.load("figure.png")
print(meta["scitex"]["version"])
```
