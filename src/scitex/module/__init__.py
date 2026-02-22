#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/module/__init__.py

from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)

"""SciTeX Module Maker -- decorator and output APIs for custom workspace modules.

Usage:
    import scitex as stx

    @stx.module(label="My Analysis", icon="fa-brain", category="analysis")
    def my_analysis(project=stx.module.INJECTED, plt=stx.module.INJECTED):
        df = stx.io.load(project / "data.csv")
        stx.module.output(df, title="Raw Data")
        fig, ax = plt.subplots()
        ax.plot(df["x"], df["y"])
        stx.module.output(fig, title="Plot")
"""


# Sentinel object for decorator-injected parameters
class _InjectedSentinel:
    """Sentinel value indicating a parameter will be injected by the module runner."""

    def __repr__(self):
        return "<INJECTED>"


INJECTED = _InjectedSentinel()

from ._decorator import module
from ._manifest import ModuleManifest
from ._output import ModuleOutput, ModuleOutputCollector, html, output
from ._renderer import render_output, render_outputs

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
