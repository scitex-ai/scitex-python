"""Re-export shim — implementation moved to figrecipe.

Phase 2 of the figrecipe-owns-plt rebalance (2026-05-08). figrecipe now
hosts the canonical ``configure_mpl`` (no scitex.* deps, leaf
dependency invariant). This module re-exports for backward
compatibility with existing
``from scitex.plt.utils._configure_mpl import configure_mpl`` callers.

Notes on the migration:
- The figrecipe port drops env-var resolution
  (``SCITEX_PLT_AXES_WIDTH_MM=…``). If you relied on that, set the
  value via the kwarg directly or via ``figrecipe.load_style``.
- The scitex.str.set_fallback_mode font-fallback hook is dropped.
  matplotlib's own font search covers the SCITEX font list adequately.
- Same return shape: ``(plt, COLORS_DotDict)``.
"""

from figrecipe import configure_mpl  # noqa: F401

__all__ = ["configure_mpl"]
