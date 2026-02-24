#!/usr/bin/env python3
"""scitex.media.render — Unified media rendering for chat, terminal, and files.

Detect, classify, and format media for various targets: AI chat pane,
terminal overlay (OSC escape), or markdown embed.

Usage:
    from scitex.media import render

    # Detect media in text
    refs = render.detect(tool_output, root_path="/home/user/proj")

    # Display in terminal (OSC escape)
    render.show("figure.png")  # prints OSC escape to stdout

    # Display as markdown
    render.show("figure.png", target="markdown")  # → "![figure.png](figure.png)"

    # Classify a file
    ref = render.classify("data.csv")  # → {"type": "csv", ...}

CLI:
    python -m scitex.media.render show figure.png --target terminal
    python -m scitex.media.render classify data.csv
    python -m scitex.media.render detect "Saved /proj/fig.png" --root /proj
"""

from ._classify import MEDIA_EXTENSIONS, classify
from ._detect import detect
from ._show import show

__all__ = [
    "classify",
    "detect",
    "show",
    "MEDIA_EXTENSIONS",
]

# EOF
