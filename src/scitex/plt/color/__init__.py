#!/usr/bin/env python3
"""Scitex color module — delegates to figrecipe.colors (single source of truth).

Public API mirrors figrecipe.colors public exports.
Internal functions remain accessible via figrecipe.colors._colors.bgr2rgb etc.
but are not re-exported here to keep the public API clean.
"""

# Public API from figrecipe.colors
from figrecipe.colors import (
    DEF_ALPHA,
    HEX,
    PARAMS,
    RGB,
    RGB_NORM,
    RGBA,
    RGBA_NORM,
    cycle_color,
    gen_interpolate,
    get_categorical_colors_from_cmap,
    get_color_from_cmap,
    get_colors_from_cmap,
    gradiate_color,
    interpolate,
    to_hex,
    to_rgb,
    to_rgba,
    update_alpha,
)

# scitex-specific extras (not in figrecipe)
from ._add_hue_col import add_hue_col
from ._vizualize_colors import vizualize_colors

__all__ = [
    # Constants
    "PARAMS",
    "DEF_ALPHA",
    "RGB",
    "RGB_NORM",
    "RGBA",
    "RGBA_NORM",
    "HEX",
    # Universal converters
    "to_hex",
    "to_rgb",
    "to_rgba",
    "update_alpha",
    # Color cycling
    "cycle_color",
    # Gradients & interpolation
    "gradiate_color",
    "interpolate",
    "gen_interpolate",
    # Colormap utilities
    "get_color_from_cmap",
    "get_colors_from_cmap",
    "get_categorical_colors_from_cmap",
    # scitex extras
    "add_hue_col",
    "vizualize_colors",
]

# EOF
