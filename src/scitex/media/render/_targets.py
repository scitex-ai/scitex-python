#!/usr/bin/env python3
"""Target-specific rendering formatters."""

from __future__ import annotations

import base64
import json
import os
from typing import Any

from ._classify import classify


def _to_terminal(path: str) -> str:
    """Format media as OSC escape for terminal display.

    The OSC escape ``\\033]9998;media:<base64-json>\\007`` is intercepted
    by the SciTeX terminal frontend and displayed as a floating overlay.

    Args:
        path: File path (resolved to absolute).

    Returns
    -------
        OSC escape string ready to print to stdout.

    Examples
    --------
        >>> esc = _to_terminal("figure.png")
        >>> esc.startswith("\\033]9998;media:")
        True
    """
    abs_path = os.path.realpath(path)
    ref = classify(abs_path) or {"type": "file", "path": abs_path, "ext": ""}
    ref["url"] = abs_path
    payload = base64.b64encode(json.dumps(ref).encode()).decode()
    return f"\033]9998;media:{payload}\007"


def _to_chat(path: str, root_path: str | None = None) -> dict[str, Any]:
    """Format media as dict for AI chat pane SSE events.

    Args:
        path: File path.
        root_path: If provided, path is made relative to this root.

    Returns
    -------
        MediaRef dict: {"type": <media_type>, "path": <path>, "ext": <ext>}

    Examples
    --------
        >>> _to_chat("figures/plot.png")
        {'type': 'image', 'path': 'figures/plot.png', 'ext': '.png'}
    """
    display_path = path
    if root_path and os.path.isabs(path):
        root = root_path.rstrip("/")
        if path.startswith(root + "/"):
            display_path = path[len(root) + 1 :]

    ref = classify(display_path)
    if ref is None:
        return {"type": "file", "path": display_path, "ext": ""}
    return ref


def _to_markdown(path: str, alt: str = "") -> str:
    """Format media as markdown embed string.

    Images use ``![alt](path)`` syntax. Other types use ``[filename](path)``.

    Args:
        path: File path.
        alt: Alt text for images (default: filename).

    Returns
    -------
        Markdown string.

    Examples
    --------
        >>> _to_markdown("figure.png")
        '![figure.png](figure.png)'
        >>> _to_markdown("data.csv")
        '[data.csv](data.csv)'
    """
    ref = classify(path)
    filename = os.path.basename(path)
    alt = alt or filename

    if ref and ref["type"] == "image":
        return f"![{alt}]({path})"
    return f"[{filename}]({path})"


# EOF
