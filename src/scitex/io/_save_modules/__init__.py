#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: src/scitex/io/_save_modules/__init__.py
"""Save modules — delegates format handlers to scitex-io, keeps scitex-specific ones local."""

# =============================================================================
# Format handlers from scitex-io (single source of truth)
# =============================================================================

from scitex_io._save_modules._bibtex import save_bibtex
from scitex_io._save_modules._catboost import _save_catboost as save_catboost
from scitex_io._save_modules._csv import _save_csv as save_csv
from scitex_io._save_modules._excel import save_excel
from scitex_io._save_modules._json import _save_json as save_json
from scitex_io._save_modules._listed_dfs_as_csv import (
    _save_listed_dfs_as_csv as save_listed_dfs_as_csv,
)
from scitex_io._save_modules._listed_scalars_as_csv import (
    _save_listed_scalars_as_csv as save_listed_scalars_as_csv,
)
from scitex_io._save_modules._mp4 import _mk_mp4 as save_mp4
from scitex_io._save_modules._numpy import _save_npy as save_npy
from scitex_io._save_modules._numpy import _save_npz as save_npz
from scitex_io._save_modules._optuna_study_as_csv_and_pngs import (
    save_optuna_study_as_csv_and_pngs,
)
from scitex_io._save_modules._pickle import _save_pickle as save_pickle
from scitex_io._save_modules._pickle import _save_pickle_gz as save_pickle_compressed
from scitex_io._save_modules._text import _save_text as save_text
from scitex_io._save_modules._yaml import _save_yaml as save_yaml

# Optional: image (requires PIL/plotly)
try:
    from scitex_io._save_modules._image import save_image
except ImportError:
    save_image = None

# Optional: HTML (requires plotly)
try:
    from scitex_io._save_modules._html import save_html
except ImportError:
    save_html = None

# Optional: HDF5 (requires h5py)
try:
    from scitex_io._save_modules._hdf5 import _save_hdf5 as save_hdf5
except ImportError:
    save_hdf5 = None

# Optional: joblib
try:
    from scitex_io._save_modules._joblib import _save_joblib as save_joblib
except ImportError:
    save_joblib = None

# Optional: matlab (requires scipy)
try:
    from scitex_io._save_modules._matlab import _save_matlab as save_matlab
except ImportError:
    save_matlab = None

# Optional: torch
try:
    from scitex_io._save_modules._torch import _save_torch as save_torch
except ImportError:
    save_torch = None

# Optional: zarr
try:
    from scitex_io._save_modules._zarr import _save_zarr as save_zarr
except ImportError:
    save_zarr = None

# =============================================================================
# SciTeX-specific save modules (NOT in scitex-io)
# =============================================================================

from ._figure_utils import get_figure_with_data
from ._image_csv import handle_image_with_csv
from ._legends import save_separate_legends
from ._plot_bundle import save_plot_bundle
from ._plot_scitex import save_plot_as_scitex
from ._stx_bundle import save_stx_bundle
from ._symlink import symlink, symlink_to
from ._tex import _save_tex as save_tex  # scitex version has extra logic

__all__ = [
    # Format handlers (from scitex-io)
    "save_csv",
    "save_excel",
    "save_npy",
    "save_npz",
    "save_pickle",
    "save_pickle_compressed",
    "save_joblib",
    "save_torch",
    "save_json",
    "save_yaml",
    "save_hdf5",
    "save_matlab",
    "save_catboost",
    "save_text",
    "save_html",
    "save_image",
    "save_mp4",
    "save_zarr",
    "save_bibtex",
    "save_listed_dfs_as_csv",
    "save_listed_scalars_as_csv",
    "save_optuna_study_as_csv_and_pngs",
    # SciTeX-specific
    "save_tex",
    "save_stx_bundle",
    "save_plot_bundle",
    "save_plot_as_scitex",
    "save_separate_legends",
    "handle_image_with_csv",
    "get_figure_with_data",
    "symlink",
    "symlink_to",
]

# EOF
