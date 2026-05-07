"""Re-export shim — implementation moved to figrecipe._utils.

Phase 1 of the figrecipe-owns-plt rebalance (2026-05-08). Implementation
lives in `figrecipe._utils._dimension_viewer`; this module re-exports the public
API for backward compatibility with existing
`from scitex.plt.utils._dimension_viewer import …` callers.
"""
from figrecipe._utils._dimension_viewer import *  # noqa: F401, F403
