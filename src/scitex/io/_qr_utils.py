#!/usr/bin/env python3
"""Deprecated location for ``add_qr_to_figure``.

Moved to ``figrecipe.add_qr_to_figure`` (2026-05-29) per SoC: QR
annotation is figure-domain, not I/O-domain. This shim keeps the
umbrella import path working for legacy callers and will be removed
in a future release.
"""

from __future__ import annotations

from scitex_compat import deprecated


@deprecated(
    reason="moved to figrecipe.add_qr_to_figure",
    forward_to="figrecipe.add_qr_to_figure",
)
def add_qr_to_figure(fig, metadata, position="bottom-right", size=0.08):
    """Compat shim — forwards to :func:`figrecipe.add_qr_to_figure`."""
    raise RuntimeError("unreachable: @deprecated forwards before body runs")


__all__ = ["add_qr_to_figure"]
