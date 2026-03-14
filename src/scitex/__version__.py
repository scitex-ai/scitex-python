#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-python/src/scitex/__version__.py

"""
Version is sourced from pyproject.toml via importlib.metadata.
Single source of truth: pyproject.toml [project] version field.
"""

try:
    from importlib.metadata import version

    __version__ = version("scitex")
except Exception:
    __version__ = "0.0.0"  # Fallback for editable installs without metadata

# EOF
