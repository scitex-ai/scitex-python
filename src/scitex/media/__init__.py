#!/usr/bin/env python3
"""scitex.media — Media handling (detection, rendering, display).

Submodules:
    render — Detect, classify, and format media for various targets
             (chat pane, terminal overlay, markdown embed).

Usage:
    from scitex.media import render

    refs = render.detect(text, root_path="/home/user/proj")
    render.show("figure.png", target="terminal")
"""

from . import render  # noqa: F401

__all__ = ["render"]

# EOF
