#!/usr/bin/env python3
"""Detect media file references in text output."""

from __future__ import annotations

import re
from typing import Any

from ._classify import classify


def detect(text: str, root_path: str | None = None) -> list[dict[str, Any]]:
    """Extract media file references from tool output text.

    Scans for absolute paths starting with *root_path*, strips the prefix
    to get a relative path, and classifies by file extension.

    Args:
        text: Tool output or any text containing file paths.
        root_path: Project root to match paths against.
            When None, returns empty list.

    Returns
    -------
        List of MediaRef dicts::

            [{"type": "image", "path": "figures/plot.png", "ext": ".png"}]

    Examples
    --------
        >>> detect("Saved to /home/u/proj/fig.png", "/home/u/proj")
        [{'type': 'image', 'path': 'fig.png', 'ext': '.png'}]
        >>> detect("no paths here")
        []
    """
    if not root_path or not text:
        return []

    refs: list[dict[str, Any]] = []
    seen: set[str] = set()

    # Match absolute paths: root followed by any non-whitespace chars.
    # Strip trailing punctuation that is likely sentence-level, not filename.
    pattern = re.escape(root_path.rstrip("/")) + r"(/\S+)"
    for match in re.finditer(pattern, text):
        rel_path = match.group(1).rstrip(".,;:!?)\"'").lstrip("/")
        if rel_path in seen:
            continue

        ref = classify(rel_path)
        if ref is not None:
            seen.add(rel_path)
            refs.append(ref)

    return refs


# EOF
