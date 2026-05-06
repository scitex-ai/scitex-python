#!/usr/bin/env python3
# Timestamp: "2025-08-11 05:54:51 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import glob
from pathlib import Path
from typing import Any, Union

# Core loaders (from scitex-io, single source of truth)
from scitex_io._load_modules._bibtex import _load_bibtex
from scitex_io._load_modules._json import _load_json
from scitex_io._load_modules._markdown import _load_markdown
from scitex_io._load_modules._numpy import _load_npy
from scitex_io._load_modules._pandas import _load_csv, _load_excel, _load_tsv
from scitex_io._load_modules._pickle import _load_pickle
from scitex_io._load_modules._txt import _load_txt
from scitex_io._load_modules._xml import _load_xml
from scitex_io._load_modules._yaml import _load_yaml
from scitex_io._loading._load_cache import (
    cache_data,
    get_cached_data,
    load_npy_cached,
)

from scitex.decorators import preserve_doc


# Optional loaders - wrapped for missing dependencies
def _unavailable_loader(name):
    def _loader(*args, **kwargs):
        raise ImportError(
            f"Loader for {name} not available. Install required dependencies."
        )

    return _loader


try:
    from scitex_io._load_modules._con import _load_con
except ImportError:
    _load_con = _unavailable_loader("con")

try:
    from scitex_io._load_modules._docx import _load_docx
except ImportError:
    _load_docx = _unavailable_loader("docx")

try:
    from scitex_io._load_modules._eeg import _load_eeg_data
except ImportError:
    _load_eeg_data = _unavailable_loader("eeg")

try:
    from scitex_io._load_modules._hdf5 import _load_hdf5
except ImportError:
    _load_hdf5 = _unavailable_loader("hdf5")

try:
    from scitex_io._load_modules._image import _load_image
except ImportError:
    _load_image = _unavailable_loader("image")

try:
    from scitex_io._load_modules._joblib import _load_joblib
except ImportError:
    _load_joblib = _unavailable_loader("joblib")

try:
    from scitex_io._load_modules._matlab import _load_matlab
except ImportError:
    _load_matlab = _unavailable_loader("matlab")

try:
    from scitex_io._load_modules._pdf import _load_pdf
except ImportError:
    _load_pdf = _unavailable_loader("pdf")

try:
    from scitex_io._load_modules._sqlite3 import _load_db_sqlite3
except ImportError:
    _load_db_sqlite3 = _unavailable_loader("sqlite3")

try:
    from scitex_io._load_modules._torch import _load_torch
except ImportError:
    _load_torch = _unavailable_loader("torch")

try:
    from scitex_io._load_modules._zarr import _load_zarr
except ImportError:
    _load_zarr = _unavailable_loader("zarr")


def _load_bundle(lpath, verbose=False, **kwargs):
    """Load a .plot, .figure, or .stats bundle.

    Parameters
    ----------
    lpath : str or Path
        Path to the bundle (directory or ZIP).
    verbose : bool
        If True, print verbose output.
    **kwargs
        Additional arguments.

    Returns
    -------
    For .plot bundles:
        tuple: (fig, ax, data) where fig is reconstructed figure,
               ax is the axes, data is DataFrame or None.
    For .figure bundles:
        dict: Figure data with 'spec' and 'panels'.
    For .stats bundles:
        dict: Stats data with 'spec' and 'comparisons'.
    """
    from .bundle import BundleType
    from .bundle import load as load_bundle

    bundle = load_bundle(lpath)
    bundle_type = bundle.get("type")

    if bundle_type == BundleType.PLOT:
        # Return (fig, ax, data) tuple for .plot bundles
        # Note: We return the spec and data, not a reconstructed figure
        # as matplotlib figures cannot be perfectly serialized/deserialized
        from pathlib import Path

        import matplotlib.pyplot as plt

        p = Path(lpath)
        bundle_dir = p

        # Handle ZIP extraction
        if not p.is_dir():
            import tempfile
            import zipfile

            temp_dir = Path(tempfile.mkdtemp())
            with zipfile.ZipFile(p, "r") as zf:
                zf.extractall(temp_dir)
            bundle_dir = temp_dir

        # Find PNG file - layered format stores in exports/
        basename = bundle.get("basename", "plot")
        png_path = bundle_dir / "exports" / f"{basename}.png"
        if not png_path.exists():
            # Fallback to root level (legacy format)
            png_path = bundle_dir / f"{basename}.png"

        # Load the PNG as a figure
        if png_path.exists():
            img = plt.imread(str(png_path))
            fig, ax = plt.subplots()
            ax.imshow(img)
            ax.axis("off")

            # Attach metadata from spec
            spec = bundle.get("spec", {})
            if spec:
                # Handle both layered and legacy spec formats
                axes_list = spec.get("axes", [])
                if axes_list and isinstance(axes_list, list):
                    for key, val in axes_list[0].items():
                        setattr(ax, f"_scitex_{key}", val)
                # Theme from style (layered) or spec (legacy)
                style = bundle.get("style", {})
                theme = style.get("theme", {}) if style else spec.get("theme", {})
                if theme:
                    fig._scitex_theme = theme.get("mode")

            # Data from bundle (merged in load_layered_plot_bundle)
            data = bundle.get("data")
            return fig, ax, data
        else:
            # No PNG, return spec and data
            return bundle.get("spec"), None, bundle.get("data")

    elif bundle_type == BundleType.FIGURE:
        # Return figure dict for .figure bundles
        return bundle

    elif bundle_type == BundleType.STATS:
        # Return stats dict for .stats bundles
        return bundle

    return bundle


def load(
    lpath: Union[str, Path],
    ext: str = None,
    show: bool = False,
    verbose: bool = False,
    cache: bool = True,
    metadata: bool = None,  # None = auto-detect (True for images)
    **kwargs,
) -> Any:
    """
    Load data from various file formats.

    This function supports loading data from multiple file formats with optional caching.

    Parameters
    ----------
    lpath : Union[str, Path]
        The path to the file to be loaded. Can be a string or pathlib.Path object.
    ext : str, optional
        File extension to use for loading. If None, automatically detects from filename.
        Useful for files without extensions (e.g., UUID-named files).
        Examples: 'pdf', 'json', 'csv'
    show : bool, optional
        If True, display additional information during loading. Default is False.
    verbose : bool, optional
        If True, print verbose output during loading. Default is False.
    cache : bool, optional
        If True, enable caching for faster repeated loads. Default is True.
    metadata : bool or None, optional
        If True, return tuple (data, metadata_dict) for images and PDFs.
        If False, return data only.
        If None (default), automatically True for images, False for PDFs and other formats.
        Works for image files (.png, .jpg, .jpeg, .tiff, .tif) and PDF files.
        For PDFs, metadata_dict contains embedded scitex metadata from PDF Subject field.
    **kwargs : dict
        Additional keyword arguments to be passed to the specific loading function.
        For PDFs, can include: mode='full'|'text'|'scientific', etc.

    Returns
    -------
    object
        The loaded data object, which can be of various types depending on the input file format.

        For images with metadata=True (default):
            Returns tuple (image, metadata_dict). metadata_dict is None if no metadata found.

        For PDFs with metadata=False (default):
            Returns dict with keys: 'full_text', 'sections', 'metadata', 'pages', etc.

        For PDFs with metadata=True:
            Returns tuple (pdf_data_dict, metadata_dict). Enables consistent API with images.

    Raises
    ------
    ValueError
        If the file extension is not supported.
    FileNotFoundError
        If the specified file does not exist.

    Supported Extensions
    -------------------
    - Data formats: .csv, .tsv, .xls, .xlsx, .xlsm, .xlsb, .json, .yaml, .yml
    - Scientific: .npy, .npz, .mat, .hdf5, .con
    - ML/DL: .pth, .pt, .cbm, .joblib, .pkl
    - Documents: .txt, .log, .event, .md, .docx, .pdf, .xml
    - Images: .jpg, .png, .tiff, .tif
    - EEG data: .vhdr, .vmrk, .edf, .bdf, .gdf, .cnt, .egi, .eeg, .set
    - Database: .db

    Examples
    --------
    >>> # Load CSV data
    >>> data = load('data.csv')

    >>> # Load image with metadata (default behavior)
    >>> img, meta = load('figure.png')
    >>> print(meta['scitex']['version'])

    >>> # Load image without metadata
    >>> img = load('figure.png', metadata=False)

    >>> # Load PDF with default extraction (no metadata tuple)
    >>> pdf = load('paper.pdf')
    >>> print(pdf['full_text'])

    >>> # Load PDF with metadata tuple (consistent API with images)
    >>> pdf, meta = load('paper.pdf', metadata=True)
    >>> print(meta['scitex']['version'])

    >>> # Load PDF with specific mode
    >>> text = load('paper.pdf', mode='text')

    >>> # Load file without extension (e.g., UUID PDF)
    >>> pdf = load('f2694ccb-1b6f-4994-add8-5111fd4d52f1', ext='pdf')
    """
    # Don't use clean_path as it breaks relative paths like ./file.txt
    # lpath = clean_path(lpath)

    # Convert Path objects to strings for consistency
    if isinstance(lpath, Path):
        lpath = str(lpath)
        if verbose:
            print(f"[DEBUG] After Path conversion: {lpath}")

    # Handle bundle formats (.plot, .figure, .stats and their ZIP variants)
    bundle_extensions = (".figure", ".plot", ".stats")
    for bext in bundle_extensions:
        if lpath.endswith(bext) or lpath.endswith(f"{bext}.zip"):
            return _load_bundle(lpath, verbose=verbose, **kwargs)

    # Check if it's a glob pattern
    if "*" in lpath or "?" in lpath or "[" in lpath:
        # Handle glob pattern
        matched_files = sorted(glob.glob(lpath))
        if not matched_files:
            raise FileNotFoundError(f"No files found matching pattern: {lpath}")
        # Load all matched files
        results = []
        for file_path in matched_files:
            results.append(load(file_path, show=show, verbose=verbose, **kwargs))
        return results

    # Handle broken symlinks - os.path.exists() returns False for broken symlinks
    if not os.path.exists(lpath):
        if os.path.islink(lpath):
            # For symlinks, resolve the target path relative to symlink's directory
            symlink_dir = os.path.dirname(os.path.abspath(lpath))
            target = os.readlink(lpath)
            resolved_target = os.path.join(symlink_dir, target)
            resolved_target = os.path.abspath(resolved_target)

            if os.path.exists(resolved_target):
                lpath = resolved_target
            else:
                raise FileNotFoundError(f"Symlink target not found: {resolved_target}")
        else:
            # Try general path resolution
            try:
                resolved_path = os.path.realpath(lpath)
                if os.path.exists(resolved_path):
                    lpath = resolved_path
                else:
                    raise FileNotFoundError(f"File not found: {lpath}")
            except Exception:
                raise FileNotFoundError(f"File not found: {lpath}")

    # Try to get from cache first (skip cache if metadata is requested for images)
    if cache and not metadata:
        cached_data = get_cached_data(lpath)
        if cached_data is not None:
            if verbose:
                print(f"[Cache HIT] Loaded from cache: {lpath}")
            return cached_data

    loaders_dict = {
        # Default
        "": _load_txt,
        # Config/Settings
        "yaml": _load_yaml,
        "yml": _load_yaml,
        "json": _load_json,
        "xml": _load_xml,
        # Bibliography
        "bib": _load_bibtex,
        # ML/DL Models
        "pth": _load_torch,
        "pt": _load_torch,
        # "cbm": _load_catboost,
        "joblib": _load_joblib,
        "pkl": _load_pickle,
        "pickle": _load_pickle,
        "gz": _load_pickle,  # For .pkl.gz files
        # Tabular Data
        "csv": _load_csv,
        "tsv": _load_tsv,
        "xls": _load_excel,
        "xlsx": _load_excel,
        "xlsm": _load_excel,
        "xlsb": _load_excel,
        "db": _load_db_sqlite3,
        # Scientific Data
        "npy": _load_npy,
        "npz": _load_npy,
        "mat": _load_matlab,
        "hdf5": _load_hdf5,
        "h5": _load_hdf5,
        "zarr": _load_zarr,
        "con": _load_con,
        # Documents
        "txt": _load_txt,
        "tex": _load_txt,
        "log": _load_txt,
        "event": _load_txt,
        "py": _load_txt,
        "sh": _load_txt,
        "md": _load_markdown,
        "docx": _load_docx,
        "pdf": _load_pdf,
        # Images
        "jpg": _load_image,
        "png": _load_image,
        "tiff": _load_image,
        "tif": _load_image,
        # EEG Data
        "vhdr": _load_eeg_data,
        "vmrk": _load_eeg_data,
        "edf": _load_eeg_data,
        "bdf": _load_eeg_data,
        "gdf": _load_eeg_data,
        "cnt": _load_eeg_data,
        "egi": _load_eeg_data,
        "eeg": _load_eeg_data,
        "set": _load_eeg_data,
    }

    # Determine extension: use explicit ext parameter or detect from filename
    if ext is not None:
        # Use explicitly provided extension (strip leading dot if present)
        detected_ext = ext.lstrip(".")
    else:
        # Auto-detect from filename
        detected_ext = lpath.split(".")[-1] if "." in lpath else ""

    # Auto-detect metadata for images and PDFs
    is_image = detected_ext in ["jpg", "jpeg", "png", "tiff", "tif"]
    is_pdf = detected_ext == "pdf"

    if metadata is None:
        # Default: True for images, False for other formats (PDFs default to False for backward compatibility)
        metadata = is_image

    # Special handling for numpy files with caching
    if cache and detected_ext in ["npy", "npz"]:
        return load_npy_cached(lpath, **kwargs)

    loader = preserve_doc(loaders_dict.get(detected_ext, _load_txt))

    try:
        # Pass metadata parameter for images and PDFs
        if is_image:
            result = loader(lpath, metadata=metadata, verbose=verbose, **kwargs)
        elif is_pdf:
            # Pass metadata parameter to PDF loader for API consistency
            result = loader(lpath, metadata=metadata, **kwargs)
        else:
            result = loader(lpath, **kwargs)

        # Cache the result if caching is enabled (skip if metadata was used)
        if cache and not metadata:
            cache_data(lpath, result)
            if verbose:
                print(f"[Cache STORED] Cached data for: {lpath}")

        # Track input for verification (if session is active)
        try:
            from scitex.clew import on_io_load

            on_io_load(lpath)
        except Exception:
            pass  # Silent fail - don't interrupt load operations

        return result
    except (ValueError, FileNotFoundError) as e:
        raise ValueError(f"Error loading file {lpath}: {str(e)}")


# EOF
