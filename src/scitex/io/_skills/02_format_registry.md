---
skill: io.format_registry
description: Register custom loaders and savers, list all supported formats, and explore HDF5/Zarr file trees.
---

# stx.io — format registry and exploration

All format handlers come from `scitex-io` (the standalone package). `scitex.io` re-exports the registry API so you can inspect and extend it without importing `scitex_io` directly.

## List registered formats

```python
import scitex as stx

formats = stx.io.list_formats()
# Returns dict of {extension: {"loader": fn, "saver": fn}}
```

## Register a custom format

```python
import json

def my_loader(path, **kwargs):
    with open(path) as f:
        return json.load(f)

def my_saver(obj, path, **kwargs):
    with open(path, "w") as f:
        json.dump(obj, f)

stx.io.register_loader(".myext", my_loader)
stx.io.register_saver(".myext", my_saver)

# Now save/load works transparently
stx.io.save({"key": "value"}, "data.myext")
data = stx.io.load("data.myext")
```

`get_loader` and `get_saver` return the registered handler for an extension:

```python
loader_fn = stx.io.get_loader(".csv")
saver_fn  = stx.io.get_saver(".npy")
```

## HDF5 exploration

```python
# Print the full HDF5 tree
stx.io.explore_h5("experiment.h5")

# Check whether a dataset path exists
exists = stx.io.has_h5_key("experiment.h5", "results/signal")

# Interactive explorer object
exp = stx.io._H5Explorer("experiment.h5")
```

`explore_h5` and `has_h5_key` are wrapped in a try/except at import time; they
are `None` if `h5py` is not installed.

## Zarr exploration

```python
stx.io.explore_zarr("dataset.zarr")
exists = stx.io.has_zarr_key("dataset.zarr", "group/array")
```

Same pattern — `None` if `zarr` is not installed.

## File globbing

```python
# Returns sorted list of matching paths
paths = stx.io.glob("runs/*/results.csv")

# glob also accepts any pattern parse_glob understands
from scitex.io import parse_glob
pattern = parse_glob("runs/**/metrics.json")
```

## Reload / flush

```python
# Re-import a module from disk (useful in notebooks)
stx.io.reload(my_module)

# Flush write buffers (e.g. for open HDF5 stores)
stx.io.flush(store)
```

## Config loading

`load_configs` is a scitex-specific convenience that loads all YAML/JSON files from a config directory and returns a `DotDict` (attribute-style access):

```python
CONFIG = stx.io.load_configs("./config/")
print(CONFIG.model.learning_rate)
```

The result should be assigned to an `UPPER_CASE` variable per the scitex-linter
rule `S007`.
