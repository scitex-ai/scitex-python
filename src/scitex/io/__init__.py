#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: src/scitex/io/__init__.py
"""SciTeX IO module — thin re-export of scitex-io.

`save()` and `load()` are re-exported directly from `scitex_io` per
SOC.md R5/R6. Observer wiring (clew session tracking) is layered
**below** the umbrella: `scitex-clew` self-registers with
`scitex_io`'s neutral post-save / post-load hook registry on its own
import, so any `scitex.io.save(...)` / `scitex.io.load(...)` call
automatically triggers clew tracking when clew is installed. No
umbrella glue needed.

Bundle I/O is now also re-exported from scitex-io:

    from scitex.io.bundle import Bundle
"""

# =============================================================================
# Core utilities from scitex-io (single source of truth)
# =============================================================================

# Bulk re-export everything scitex_io publishes via its __all__ — keeps the
# umbrella contract that every scitex_io public name is reachable via
# scitex.io. Explicit imports below retain backward-compat aliases (e.g.
# H5Explorer also bound as _H5Explorer) and add umbrella-only integration.
from scitex_io import *  # noqa: F401,F403

# Registry API (from scitex-io)
from scitex_io import (
    cache,
    clear_load_cache,
    configure_cache,
    flush,  # noqa: F401
    get_cache_info,
    get_loader,
    get_saver,
    glob,
    list_formats,
    parse_glob,
    register_loader,
    register_saver,
    reload,  # noqa: F401
)

# Explorers (from scitex-io)
try:
    from scitex_io import H5Explorer as _H5Explorer  # noqa: F401
    from scitex_io import explore_h5, has_h5_key
except (ImportError, TypeError):
    _H5Explorer = None
    explore_h5 = None
    has_h5_key = None

try:
    from scitex_io import ZarrExplorer as _ZarrExplorer  # noqa: F401
    from scitex_io import explore_zarr, has_zarr_key
except (ImportError, TypeError):
    _ZarrExplorer = None
    explore_zarr = None
    has_zarr_key = None

# Save utilities (from scitex-io)
try:
    from scitex_io import (
        save_image,
        save_listed_dfs_as_csv,
        save_listed_scalars_as_csv,
        save_mp4,
        save_optuna_study_as_csv_and_pngs,
        save_text,
    )
except (ImportError, TypeError):
    save_image = None
    save_text = None
    save_mp4 = None
    save_listed_dfs_as_csv = None
    save_listed_scalars_as_csv = None
    save_optuna_study_as_csv_and_pngs = None

# Optional utilities (from scitex-io)
try:
    from scitex_io import json2md
except (ImportError, TypeError):
    json2md = None

try:
    from scitex_io import migrate_h5_to_zarr, migrate_h5_to_zarr_batch
except (ImportError, TypeError):
    migrate_h5_to_zarr = None
    migrate_h5_to_zarr_batch = None

# =============================================================================
# Core save/load — pure re-export of scitex_io. Observer wiring (clew
# session tracking) is handled by scitex-clew self-registering with
# scitex_io's post-save/post-load hook registry on its own import,
# per SOC.md R6. No umbrella glue needed.
# =============================================================================

from scitex_io import load, load_configs, save  # noqa: F401

from . import bundle  # noqa: F401

# Metadata embedding (from scitex-io)
try:
    from scitex_io import embed_metadata, has_metadata, read_metadata
except (ImportError, TypeError):
    read_metadata = None
    embed_metadata = None
    has_metadata = None

__all__ = [
    # Primary I/O (scitex wrappers with clew hooks)
    "save",
    "load",
    # Bundle submodule (scitex-specific)
    "bundle",
    # Config loading (scitex-specific: uses DotDict)
    "load_configs",
    # File utilities (from scitex-io)
    "glob",
    "reload",
    "flush",
    "cache",
]

# EOF
