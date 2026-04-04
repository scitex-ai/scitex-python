#!/usr/bin/env python3
"""SciTeX gists module — delegates to scitex-gists if available."""

try:
    from scitex_gists import (
        SigMacro_processFigure_S,
        SigMacro_toBlue,
        sigmacro_process_figure_s,
        sigmacro_to_blue,
    )

    _BACKEND = "scitex-gists"
except ImportError:
    from ._SigMacro_processFigure_S import (
        SigMacro_processFigure_S,
        sigmacro_process_figure_s,
    )
    from ._SigMacro_toBlue import SigMacro_toBlue, sigmacro_to_blue

    _BACKEND = "local"

__all__ = [
    "SigMacro_processFigure_S",
    "SigMacro_toBlue",
    "sigmacro_process_figure_s",
    "sigmacro_to_blue",
]

# EOF
