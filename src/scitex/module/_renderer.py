#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/module/_renderer.py

from __future__ import annotations

"""Converts collected ModuleOutput items to serializable dictionaries."""

import base64
import io
import json
from typing import Any

from ._output import ModuleOutput, _SafeHtml


def render_output(item: ModuleOutput) -> dict[str, Any]:
    """Convert a single ModuleOutput to a serializable dict.

    The returned dict always contains:
        - ``type``:  one of figure, table, text, html, json
        - ``title``: display title (may be empty)
        - ``data``:  the serialized payload

    Args:
        item: A ModuleOutput instance.

    Returns
    -------
        Dictionary suitable for JSON serialization.
    """
    renderer = _RENDERERS.get(item.output_type, _render_text)
    return {
        "type": item.output_type,
        "title": item.title,
        "data": renderer(item.value),
    }


def render_outputs(items: list[ModuleOutput]) -> list[dict[str, Any]]:
    """Render a list of ModuleOutput items.

    Args:
        items: List of ModuleOutput instances.

    Returns
    -------
        List of serializable dicts.
    """
    return [render_output(item) for item in items]


# -- Individual renderers ----------------------------------------------------


def _render_figure(value: Any) -> str:
    """Render a matplotlib Figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    value.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("ascii")
    buf.close()
    return f"data:image/png;base64,{encoded}"


def _render_table(value: Any) -> str:
    """Render a pandas DataFrame to an HTML table string."""
    try:
        return value.to_html(
            classes="table table-striped table-sm",
            index=True,
            border=0,
            max_rows=200,
        )
    except Exception:
        return str(value)


def _render_text(value: Any) -> str:
    """Render a plain string (or fallback for unknown types)."""
    return str(value)


def _render_html(value: Any) -> str:
    """Render a _SafeHtml wrapper or raw HTML string."""
    if isinstance(value, _SafeHtml):
        return value.content
    return str(value)


def _render_json(value: Any) -> str:
    """Render a dict as a formatted JSON string."""
    try:
        return json.dumps(value, indent=2, default=str)
    except (TypeError, ValueError):
        return str(value)


_RENDERERS: dict[str, Any] = {
    "figure": _render_figure,
    "table": _render_table,
    "text": _render_text,
    "html": _render_html,
    "json": _render_json,
}


# EOF
