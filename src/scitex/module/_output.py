#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/module/_output.py

from __future__ import annotations

"""Thread-local output collection for SciTeX module execution."""

import threading
from dataclasses import dataclass, field
from typing import Any


class _SafeHtml:
    """Wrapper marking a string as pre-sanitized HTML.

    The renderer will emit this content as-is without escaping.
    """

    def __init__(self, content: str):
        self._content = str(content)

    @property
    def content(self) -> str:
        return self._content

    def __str__(self) -> str:
        return self._content

    def __repr__(self) -> str:
        truncated = (
            self._content[:60] + "..." if len(self._content) > 60 else self._content
        )
        return f"_SafeHtml({truncated!r})"


_OUTPUT_TYPE_AUTO = ""


@dataclass
class ModuleOutput:
    """Single output item produced by a module function.

    Attributes
    ----------
        value: The output object (Figure, DataFrame, str, dict, or HTML).
        title: Optional display title for this output.
        output_type: Detected type string. Auto-detected when left empty.
    """

    value: Any = None
    title: str = ""
    output_type: str = field(default=_OUTPUT_TYPE_AUTO)

    def __post_init__(self):
        if self.output_type == _OUTPUT_TYPE_AUTO:
            self.output_type = _detect_type(self.value)


def _detect_type(value: Any) -> str:
    """Infer a human-readable output type from value."""
    if isinstance(value, _SafeHtml):
        return "html"

    # Check for matplotlib Figure without importing matplotlib eagerly
    type_name = type(value).__name__
    module_name = type(value).__module__ or ""
    if "matplotlib" in module_name and type_name == "Figure":
        return "figure"

    # Check for pandas DataFrame
    if "pandas" in module_name and type_name == "DataFrame":
        return "table"

    if isinstance(value, dict):
        return "json"

    if isinstance(value, str):
        return "text"

    # Fallback
    return "text"


class ModuleOutputCollector:
    """Thread-local collector that accumulates outputs during module execution.

    Each thread maintains its own independent list so concurrent module
    executions do not interfere with each other.
    """

    _local = threading.local()

    @classmethod
    def get_current(cls) -> list[ModuleOutput]:
        """Return the output list for the current thread."""
        if not hasattr(cls._local, "outputs"):
            cls._local.outputs = []
        return list(cls._local.outputs)

    @classmethod
    def add(cls, value: Any, title: str = "") -> None:
        """Append an output item for the current thread."""
        if not hasattr(cls._local, "outputs"):
            cls._local.outputs = []
        cls._local.outputs.append(ModuleOutput(value=value, title=title))

    @classmethod
    def clear(cls) -> None:
        """Discard all collected outputs for the current thread."""
        cls._local.outputs = []


def output(value: Any, title: str = "") -> None:
    """Add an output to the current module execution.

    This is the primary API researchers call inside their module function
    to register figures, tables, text, or HTML for display.

    Args:
        value: Figure, DataFrame, string, dict, or _SafeHtml instance.
        title: Optional display title.
    """
    ModuleOutputCollector.add(value, title)


def html(content: str) -> _SafeHtml:
    """Mark a string as safe HTML so the renderer emits it without escaping.

    Args:
        content: Raw HTML string.

    Returns
    -------
        _SafeHtml wrapper.
    """
    return _SafeHtml(content)


# EOF
