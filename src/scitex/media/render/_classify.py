#!/usr/bin/env python3
"""Classify files by media type based on extension."""

from __future__ import annotations

import os
from types import MappingProxyType
from typing import Any

MEDIA_EXTENSIONS: MappingProxyType[str, frozenset[str]] = MappingProxyType(
    {
        "image": frozenset({".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}),
        "audio": frozenset({".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".webm"}),
        "video": frozenset({".mp4", ".webm", ".avi", ".mov", ".mkv"}),
        "pdf": frozenset({".pdf"}),
        "csv": frozenset({".csv", ".tsv"}),
        "plotly": frozenset({".html"}),
        "mermaid": frozenset({".mmd", ".mermaid"}),
        "graphviz": frozenset({".dot", ".gv"}),
    }
)

# Reverse lookup: extension → media type
_EXT_TO_TYPE: dict[str, str] = {}
for _media_type, _exts in MEDIA_EXTENSIONS.items():
    for _ext in _exts:
        _EXT_TO_TYPE[_ext] = _media_type


def classify(path: str) -> dict[str, Any] | None:
    """Classify a file path by media type.

    Args:
        path: File path (absolute or relative).

    Returns
    -------
        {"type": "image", "path": "fig.png", "ext": ".png"} or None
        if the extension is not recognized.

    Examples
    --------
        >>> classify("figures/plot.png")
        {'type': 'image', 'path': 'figures/plot.png', 'ext': '.png'}
        >>> classify("data.csv")
        {'type': 'csv', 'path': 'data.csv', 'ext': '.csv'}
        >>> classify("unknown.xyz") is None
        True
    """
    ext = os.path.splitext(path)[1].lower()
    media_type = _EXT_TO_TYPE.get(ext)
    if media_type is None:
        return None
    return {"type": media_type, "path": path, "ext": ext}


# EOF
