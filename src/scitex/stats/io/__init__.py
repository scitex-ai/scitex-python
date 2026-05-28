#!/usr/bin/env python3
"""Re-export shim for ``scitex.stats.io``.

Stats bundle I/O lives in the ``scitex_stats`` standalone package
(``scitex_stats.io``); this umbrella module re-exports the public
surface so legacy ``from scitex.stats.io import …`` callers continue
to work. ``scitex_io.save("results.stats.zip", …)`` consumes the same
implementation via the optional provider registered in
``scitex_io._optional_providers``.
"""

from scitex_stats.io import (  # noqa: F401
    STATS_SCHEMA_SPEC,
    load_stats_bundle,
    save_stats_bundle,
    validate_stats_spec,
)

__all__ = [
    "STATS_SCHEMA_SPEC",
    "load_stats_bundle",
    "save_stats_bundle",
    "validate_stats_spec",
]
