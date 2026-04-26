"""SciTeX benchmark — thin compatibility shim for scitex-benchmark.

Aliases ``scitex.benchmark`` to the standalone ``scitex_benchmark`` package
via ``sys.modules``. ``scitex.benchmark is scitex_benchmark``.

Install: ``pip install scitex[benchmark]``  (or ``pip install scitex-benchmark``).
See: https://github.com/ywatanabe1989/scitex-benchmark
"""

import sys as _sys

try:
    import scitex_benchmark as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.benchmark requires the 'scitex-benchmark' package. "
        "Install with: pip install scitex[benchmark]  (or: pip install scitex-benchmark)"
    ) from _e

_sys.modules[__name__] = _real
