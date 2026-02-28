#!/usr/bin/env python3
"""Display media to a target (terminal, chat, markdown)."""

from __future__ import annotations

import json
import sys

from ._targets import _to_chat, _to_markdown, _to_terminal


def show(
    path: str,
    target: str = "terminal",
    root_path: str | None = None,
    alt: str = "",
) -> str:
    """Display a media file to the specified target.

    Args:
        path: File path to display.
        target: One of ``"terminal"``, ``"chat"``, ``"markdown"``.
        root_path: Project root for chat target (makes path relative).
        alt: Alt text for markdown image embeds.

    Returns
    -------
        Formatted output string for the target.
        For ``"terminal"``, also prints the OSC escape to stdout.

    Raises
    ------
        ValueError: If *target* is not recognized.

    Examples
    --------
        >>> show("fig.png", target="markdown")
        '![fig.png](fig.png)'
    """
    if target == "terminal":
        osc = _to_terminal(path)
        sys.stdout.write(osc)
        sys.stdout.flush()
        return osc
    elif target == "chat":
        ref = _to_chat(path, root_path=root_path)
        return json.dumps(ref)
    elif target == "markdown":
        return _to_markdown(path, alt=alt)
    else:
        raise ValueError(
            f"Unknown target: {target!r}. Choose from: terminal, chat, markdown"
        )


# EOF
