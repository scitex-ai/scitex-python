"""SciTeX linalg — thin compatibility shim for scitex-linalg.

Every public name that used to live in ``scitex.linalg`` now lives in the
standalone ``scitex-linalg`` package (module ``scitex_linalg``). This file
aliases ``scitex.linalg`` to ``scitex_linalg`` via ``sys.modules`` so every
previous import path keeps resolving.

Public API:
    Distance:   euclidean_distance, cdist, edist
    Geometric:  geometric_median  (requires `scitex-linalg[torch]`)
    Misc:       cosine, nannorm, rebase_a_vec, three_line_lengths_to_coords

Install: ``pip install scitex[linalg]``  (or ``pip install scitex-linalg``).
See: https://github.com/ywatanabe1989/scitex-linalg
"""

import sys as _sys

try:
    import scitex_linalg as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.linalg requires the 'scitex-linalg' package. "
        "Install with: pip install scitex[linalg]  (or: pip install scitex-linalg)"
    ) from _e

_sys.modules[__name__] = _real
