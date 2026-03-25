---
skill: io.special_savers
description: Convenience save helpers for images, video, Optuna studies, and metadata embedding.
---

# stx.io — special save helpers

Beyond the core `save()` dispatcher, `scitex.io` re-exports several typed helpers from `scitex-io` for common scientific output patterns.

## Image saving

```python
import scitex as stx

# Save a PIL image or numpy array as PNG/TIFF/JPEG
stx.io.save_image(img_array, "output.png", dpi=300)

# Shortcut — same as calling save() with an image path
stx.io.save(fig, "plot.png", auto_crop=True, crop_margin_mm=1.0)
```

## Video

```python
import numpy as np

frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
          for _ in range(30)]

stx.io.save_mp4(frames, "animation.mp4", fps=10)
# or via the unified dispatcher:
stx.io.save(frames, "animation.mp4")
```

## Tabular helpers

```python
# Save a list of DataFrames as separate CSV sheets
stx.io.save_listed_dfs_as_csv(
    [df1, df2, df3],
    "combined.csv",
    names=["train", "val", "test"],
)

# Save a list of scalars as a single-column CSV
stx.io.save_listed_scalars_as_csv(
    [0.91, 0.93, 0.95],
    "accuracy_runs.csv",
)
```

## Optuna study export

```python
import optuna

study = optuna.load_study(study_name="hp_search", storage="sqlite:///optuna.db")
stx.io.save_optuna_study_as_csv_and_pngs(study, "optuna_results/")
# Writes: optuna_results/history.csv, optuna_results/importance.png, etc.
```

## Text

```python
stx.io.save_text("Hello, world!\n", "notes.txt")
# Equivalent to stx.io.save("Hello, world!\n", "notes.txt")
```

## Metadata embedding (PNG/TIFF)

Figures saved via `stx.io.save(fig, "plot.png")` automatically embed scitex
metadata into the image file. The metadata can be read back later:

```python
# Read embedded metadata without loading the full image
meta = stx.io.read_metadata("plot.png")
print(meta["scitex"]["version"])

# Check whether metadata is present
has = stx.io.has_metadata("plot.png")

# Embed custom metadata manually
stx.io.embed_metadata("plot.png", {"experiment_id": "exp_001"})
```

All three functions (`read_metadata`, `has_metadata`, `embed_metadata`) are
wrapped with `try/except ImportError` at import time and become `None` if the
`scitex-io` version does not support them.

## HDF5 migration

```python
# Migrate a single HDF5 file to Zarr
stx.io.migrate_h5_to_zarr("data.h5", "data.zarr")

# Batch migration of a directory
stx.io.migrate_h5_to_zarr_batch("data/", "zarr_store/")
```

These are `None` if `zarr` is not installed.

## JSON to Markdown

```python
md_text = stx.io.json2md({"title": "Results", "value": 42})
print(md_text)
# None if scitex-io version does not provide this helper.
```
