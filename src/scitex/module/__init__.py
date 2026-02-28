#!/usr/bin/env python3
"""SciTeX Module — backward-compatibility shim.

Module management has moved to scitex_cloud.module.
This shim re-exports everything so existing code continues to work.

Usage (preferred — new code should use this):
    from scitex_cloud.module import module, output, html, INJECTED

Usage (legacy — still works):
    import scitex as stx
    @stx.module(...)
"""

from __future__ import annotations

import warnings

warnings.warn(
    "scitex.module is deprecated. Use scitex_cloud.module instead.",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from scitex_cloud.module import (
        INJECTED,
        ModuleManifest,
        ModuleOutput,
        ModuleOutputCollector,
        html,
        module,
        output,
        render_output,
        render_outputs,
    )
except ImportError:
    # Fallback: scitex_cloud not installed — use local copies
    from ._decorator import module
    from ._manifest import ModuleManifest
    from ._output import ModuleOutput, ModuleOutputCollector, html, output
    from ._renderer import render_output, render_outputs

    class _InjectedSentinel:
        def __repr__(self):
            return "<INJECTED>"

    INJECTED = _InjectedSentinel()

__all__ = [
    "INJECTED",
    "module",
    "ModuleManifest",
    "ModuleOutput",
    "ModuleOutputCollector",
    "output",
    "html",
    "render_output",
    "render_outputs",
]

# EOF
