#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/plt/_render.py
"""Render figrecipe spec dicts to image bytes.

This module wraps figrecipe's ``create_figure_from_spec`` with style loading,
tick finalization, and byte serialization — the complete render pipeline.

Usage
-----
>>> from scitex.plt import render_spec_to_bytes
>>> png = render_spec_to_bytes(spec)
>>> with open("figure.png", "wb") as f:
...     f.write(png)
"""

import io
from typing import Literal

__all__ = ["render_spec_to_bytes"]


def render_spec_to_bytes(
    spec: dict,
    *,
    dpi: int = 300,
    fmt: Literal["png", "pdf", "svg"] = "png",
    facecolor: str = "white",
) -> bytes:
    """Render a figrecipe spec dict to image bytes.

    Parameters
    ----------
    spec : dict
        Figrecipe-compatible spec dict (as produced by ``build_spec``).
    dpi : int
        Output resolution (default 300).
    fmt : str
        Image format: ``"png"``, ``"pdf"``, or ``"svg"`` (default ``"png"``).
    facecolor : str
        Background colour (default ``"white"``).

    Returns
    -------
    bytes
        Encoded image bytes.

    Raises
    ------
    ImportError
        If figrecipe is not installed.
    """
    import scitex.plt as splt

    splt.load_style()

    from figrecipe._api._plot import create_figure_from_spec
    from figrecipe.styles._finalize import finalize_ticks

    result = create_figure_from_spec(spec)
    fig = result["figure"]

    for ax in fig.get_axes():
        finalize_ticks(ax)

    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, facecolor=facecolor, bbox_inches="tight")
    buf.seek(0)
    image_bytes = buf.read()

    splt.close("all")

    return image_bytes


# EOF
