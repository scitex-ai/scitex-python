#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: src/scitex/io/_load_modules/__init__.py
"""Load modules — delegates format handlers to scitex-io, keeps scitex-specific ones local."""

import importlib as _importlib
import inspect as _inspect

# =============================================================================
# Import all public functions/classes from scitex_io._load_modules
# =============================================================================

try:
    _io_mod = _importlib.import_module("scitex_io._load_modules")
    for _name, _obj in _inspect.getmembers(_io_mod):
        if (
            _inspect.isfunction(_obj) or _inspect.isclass(_obj)
        ) and not _name.startswith("_"):
            globals()[_name] = _obj
    del _io_mod
except ImportError:
    pass

# =============================================================================
# SciTeX-specific load modules (NOT in scitex-io)
# =============================================================================

# Canvas loading (scitex-specific)
try:
    from ._canvas import load_canvas  # noqa: F401
except ImportError:
    pass

# Clean up
del _importlib, _inspect

# EOF
