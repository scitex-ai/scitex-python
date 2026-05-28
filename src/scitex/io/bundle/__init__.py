#!/usr/bin/env python3
# Timestamp: 2026-01-07
# File: src/scitex/io/bundle/__init__.py

"""
SciTeX Bundle I/O - Unified bundle handling for bundles.

This module provides a clean API for working with SciTeX bundles:
    - .figure.zip - Publication Figure Bundle (panels + layout)
    - .plot.zip - Reproducible Plot Bundle (data + spec + exports)
    - .stats.zip - Statistical Results Bundle (stats + metadata)

Each bundle can exist in two forms:
    - ZIP archive: Figure1.figure.zip, plot.plot.zip, results.stats.zip
    - Directory: Figure1.figure/, plot.plot/, results.stats/

Usage:
    import scitex.io.bundle as bundle

    # Load a bundle
    data = bundle.load("Figure1.figure.zip")

    # Save a bundle
    bundle.save(data, "output.plot.zip", as_zip=True)

    # Copy a bundle
    bundle.copy("template.plot.zip", "my_plot.plot")

    # Access ZIP bundles in-memory
    with bundle.ZipBundle("figure.figure.zip") as zb:
        spec = zb.read_json("spec.json")
        data = zb.read_csv("data.csv")

    # Access nested bundles (plot inside figure)
    preview = bundle.nested.get_preview("Figure1.figure/A.plot")
    spec = bundle.nested.get_json("Figure1.figure/A.plot/spec.json")
"""

# Nested bundle access as namespace
from . import _nested as nested

# Bundle class and factory functions
from ._Bundle import Bundle, create_bundle, from_matplotlib, load_bundle

# Core operations
from ._core import (
    copy,
    dir_to_zip_path,
    get_type,
    is_bundle,
    load,
    pack,
    save,
    unpack,
    validate,
    validate_spec,
    zip_to_dir_path,
)

# Dataclasses
from scitex_io.bundle._dataclasses import BBox, DataInfo, SizeMM, Spec, SpecRefs

# Manifest functions for bundle identification
from ._manifest import (
    MANIFEST_FILENAME,
    create_manifest,
    get_type_from_manifest,
    read_manifest,
    write_manifest,
)
from scitex_io.bundle._types import (
    DIR_EXTENSIONS,
    EXTENSIONS,
    FIGURE,
    PLOT,
    STATS,
    BundleError,
    BundleNotFoundError,
    BundleType,
    BundleValidationError,
    NestedBundleNotFoundError,
)

# ZipBundle class and functions
from ._zip import ZipBundle
from ._zip import create as create_zip
from ._zip import open as open_zip
from ._zip import zip_directory

__all__ = [
    # Types
    "BundleType",
    "BundleError",
    "BundleValidationError",
    "BundleNotFoundError",
    "NestedBundleNotFoundError",
    # Constants - Extensions
    "EXTENSIONS",
    "DIR_EXTENSIONS",
    # Constants - Type names
    "FIGURE",
    "PLOT",
    "STATS",
    # Core operations
    "load",
    "save",
    "copy",
    "pack",
    "unpack",
    "validate",
    "validate_spec",
    "is_bundle",
    "get_type",
    "dir_to_zip_path",
    "zip_to_dir_path",
    # ZipBundle
    "ZipBundle",
    "open_zip",
    "create_zip",
    "zip_directory",
    # Nested access namespace
    "nested",
    # Bundle class and factory functions
    "Bundle",
    "load_bundle",
    "create_bundle",
    "from_matplotlib",
    # Dataclasses
    "Spec",
    "SpecRefs",
    "BBox",
    "SizeMM",
    "DataInfo",
    # Manifest functions
    "MANIFEST_FILENAME",
    "create_manifest",
    "write_manifest",
    "read_manifest",
    "get_type_from_manifest",
]

# EOF
