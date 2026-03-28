---
name: stx.utils
description: Index of skill files for the scitex.utils module.
---

# stx.utils — Skills Index

The `stx.utils` module provides miscellaneous utilities for scientific workflows.

## Public API

```python
import scitex as stx

stx.utils.compress_hdf5(...)   # HDF5 compression
stx.utils.yield_grids(...)     # Parameter grid iteration
stx.utils.count_grids(...)     # Count grid combinations
stx.utils.notify(...)          # Email notifications
stx.utils.search(...)          # Regex string search
```

## Sub-skills

| File | Feature | Key functions |
|------|---------|---------------|
| [compress-hdf5.md](compress-hdf5.md) | Compress HDF5 files with gzip | `compress_hdf5` |
| [grid-search.md](grid-search.md) | Enumerate parameter combinations | `yield_grids`, `count_grids` |
| [notify.md](notify.md) | Send email notifications from scripts | `notify` |
| [search.md](search.md) | Regex search over string collections | `search` |
| [verify-scitex-format.md](verify-scitex-format.md) | Audit Python files for template compliance (CLI only) | `_verify_scitex_format` |
