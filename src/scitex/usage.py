#!/usr/bin/env python3
# Timestamp: 2026-02-09
# File: src/scitex/usage.py

"""Discoverable usage examples for scitex modules.

Thin wrapper over scitex.template code templates, providing a natural
entry point: ``stx.usage("plt")`` instead of ``stx.template.get_code_template("plt")``.
"""

from __future__ import annotations

import scitex_logging as slogging

log = slogging.getLogger(__name__)


def show(topic: str | None = None) -> str:
    """Show usage examples for a scitex module.

    Parameters
    ----------
    topic : str, optional
        Module name (e.g. "plt", "stats", "session").
        If None, prints an overview of all available topics.

    Returns
    -------
    str
        Usage text.
    """
    from .template._code._code_templates import CODE_TEMPLATES, get_code_template

    if topic is None:
        lines = ["SciTeX Usage Topics", "=" * 40, ""]
        lines.append("Call stx.usage('<topic>') for detailed examples.\n")
        for tid, info in CODE_TEMPLATES.items():
            lines.append(f"  {tid:<20s} {info['description']}")
        lines.append("")
        lines.append("Example: stx.usage('plt')")
        text = "\n".join(lines)
        log.info(text)
        return text

    if topic not in CODE_TEMPLATES:
        available = ", ".join(CODE_TEMPLATES.keys())
        msg = f"Unknown topic: '{topic}'. Available: {available}"
        log.info(msg)
        return msg

    content = get_code_template(topic)
    log.info(content)
    return content


def topics() -> list[str]:
    """List available usage topics.

    Returns
    -------
    list[str]
        Topic names that can be passed to ``show()``.
    """
    from .template._code._code_templates import CODE_TEMPLATES

    return list(CODE_TEMPLATES.keys())


__all__ = ["show", "topics"]

# EOF
