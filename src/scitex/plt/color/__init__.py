#!/usr/bin/env python3
"""Scitex color module — delegates to figrecipe.colors (single source of truth).

Public API mirrors figrecipe.colors public exports.
Internal converters (BGR, str2*) importable via _prefixed names for backward compat.
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

# Internal — importable but not public (figrecipe hid these)
from figrecipe.colors import _bgr2bgra as bgr2bgra
from figrecipe.colors import _bgr2rgb as bgr2rgb
from figrecipe.colors import _bgra2bgr as bgra2bgr
from figrecipe.colors import _bgra2hex as bgra2hex
from figrecipe.colors import _bgra2rgba as bgra2rgba
from figrecipe.colors import _cycle_color_bgr as cycle_color_bgr
from figrecipe.colors import _cycle_color_rgb as cycle_color_rgb
from figrecipe.colors import (
    _get_categorical_colors_from_conf_matap as get_categorical_colors_from_conf_matap,
)
from figrecipe.colors import _get_color_from_conf_matap as get_color_from_conf_matap
from figrecipe.colors import _get_colors_from_conf_matap as get_colors_from_conf_matap
from figrecipe.colors import _gradiate_color_bgr as gradiate_color_bgr
from figrecipe.colors import _gradiate_color_bgra as gradiate_color_bgra
from figrecipe.colors import _gradiate_color_rgb as gradiate_color_rgb
from figrecipe.colors import _gradiate_color_rgba as gradiate_color_rgba
from figrecipe.colors import _rgb2bgr as rgb2bgr
from figrecipe.colors import _rgb2rgba as rgb2rgba
from figrecipe.colors import _rgba2bgra as rgba2bgra
from figrecipe.colors import _rgba2hex as rgba2hex
from figrecipe.colors import _rgba2rgb as rgba2rgb
from figrecipe.colors import _str2bgr as str2bgr
from figrecipe.colors import _str2bgra as str2bgra
from figrecipe.colors import _str2hex as str2hex
from figrecipe.colors import _str2rgb as str2rgb
from figrecipe.colors import _str2rgba as str2rgba

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
    # Universal converters (public)
    "to_hex",
    "to_rgb",
    "to_rgba",
    "update_alpha",
    # Color cycling (public)
    "cycle_color",
    # Gradients & interpolation (public)
    "gradiate_color",
    "interpolate",
    "gen_interpolate",
    # Colormap utilities (public)
    "get_color_from_cmap",
    "get_colors_from_cmap",
    "get_categorical_colors_from_cmap",
    # scitex extras
    "add_hue_col",
    "vizualize_colors",
]

# EOF
