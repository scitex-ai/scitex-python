#!/usr/bin/env python3
# Timestamp: 2025-12-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/fts/_kinds/_figure/__init__.py

"""Figure kind - Composite container for multiple elements.

A figure is a container that holds other bundles (plots, tables, text, etc.)
arranged in a layout. It has no payload data of its own.

Structure:
- children/: Contains embedded child bundles
- layout: Defines arrangement (rows, cols, panels)
"""

from ._bundle import (
    FIGURE_SCHEMA_SPEC,
    load_figure_bundle,
    save_figure_bundle,
    validate_figure_spec,
)
from ._composite import render_composite

__all__ = [
    "FIGURE_SCHEMA_SPEC",
    "load_figure_bundle",
    "render_composite",
    "save_figure_bundle",
    "validate_figure_spec",
]

# EOF
