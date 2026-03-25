---
description: Compress existing HDF5 files with gzip, preserving all datasets, groups, and attributes.
---

# stx.utils.compress_hdf5

Rewrite an HDF5 file with gzip compression applied to every dataset, preserving the full group hierarchy, dataset chunking, and all metadata attributes.

## Signature

```python
compress_hdf5(
    input_file: str,
    output_file: str | None = None,
    compression_level: int = 4,
) -> str
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_file` | str | required | Path to the source HDF5 file |
| `output_file` | str or None | None | Destination path. If None, appends `.compressed` before the extension |
| `compression_level` | int | 4 | gzip level 1–9 (higher = smaller file, slower) |

### Returns

`str` — path to the output compressed file.

### Behaviour notes

- When `output_file` is None the output is named `<stem>.compressed<ext>` (e.g. `data.h5` → `data.compressed.h5`).
- Datasets with more than 10 000 000 rows are copied in 5 000 000-row chunks to keep memory usage bounded.
- Original chunking is preserved when the source dataset was already chunked; otherwise h5py chooses chunk sizes automatically.
- All file-level and dataset-level attributes are copied verbatim.
- Prints progress and final size comparison to stdout.

## Dependencies

`h5py` is required and must be installed separately. `tqdm` is optional — if installed, chunk progress bars are shown for very large (> 1 000 000 row) datasets.

## Example

```python
import scitex as stx

# Compress with default level 4
out = stx.utils.compress_hdf5("recordings.h5")
# -> writes recordings.compressed.h5, prints size comparison

# Explicit output path and higher compression
out = stx.utils.compress_hdf5(
    "recordings.h5",
    output_file="recordings_v2.h5",
    compression_level=7,
)
```

## CLI

The module is also runnable as a script:

```bash
python -m scitex.utils._compress_hdf5 recordings.h5
python -m scitex.utils._compress_hdf5 recordings.h5 --output_file out.h5 --compression 7
```
