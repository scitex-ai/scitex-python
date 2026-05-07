"""Re-export shim — implementation moved to figrecipe._utils.

Phase 1 of the figrecipe-owns-plt rebalance (2026-05-08). Implementation
lives in `figrecipe._utils._get_actual_font`; this module re-exports the public
API for backward compatibility with existing
`from scitex.plt.utils._get_actual_font import …` callers.
"""
from figrecipe._utils._get_actual_font import *  # noqa: F401, F403
