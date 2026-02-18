#!/usr/bin/env python3
# File: ./src/scitex/plt/styles/__init__.py

"""SciTeX plot styling module.

Style configuration with priority resolution: direct -> yaml -> env -> default.

Usage:
    from scitex.plt.styles import SCITEX_STYLE, load_style, resolve_style_value

    # Load style as subplots kwargs
    style = load_style()
    fig, ax = stx.plt.subplots(**style)

    # Resolve individual values
    dpi = resolve_style_value("output.dpi", None, 300)
"""

from .presets import (  # DPI utilities
    DPI_DISPLAY,
    DPI_PREVIEW,
    DPI_SAVE,
    SCITEX_STYLE,
    STYLE,
    get_default_dpi,
    get_display_dpi,
    get_preview_dpi,
    get_style,
    load_style,
    resolve_style_value,
    save_style,
    set_style,
)

__all__ = [
    # Style configuration
    "SCITEX_STYLE",
    "STYLE",
    "load_style",
    "save_style",
    "set_style",
    "get_style",
    "resolve_style_value",
    # DPI utilities
    "get_default_dpi",
    "get_display_dpi",
    "get_preview_dpi",
    "DPI_SAVE",
    "DPI_DISPLAY",
    "DPI_PREVIEW",
]


# EOF
