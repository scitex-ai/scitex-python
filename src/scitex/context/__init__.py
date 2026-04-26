"""SciTeX context — thin compatibility shim for scitex-context.

Aliases ``scitex.context`` to the standalone ``scitex_context`` package via
``sys.modules``. ``scitex.context is scitex_context``.

Public API: detect_environment, is_script, is_notebook, is_ipython,
get_output_directory, get_notebook_path, get_notebook_directory,
get_notebook_name, get_notebook_info_simple, suppress_output, quiet

Install: ``pip install scitex[context]``  (or ``pip install scitex-context``).
See: https://github.com/ywatanabe1989/scitex-context
"""

import sys as _sys

try:
    import scitex_context as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.context requires the 'scitex-context' package. "
        "Install with: pip install scitex[context]  (or: pip install scitex-context)"
    ) from _e

_sys.modules[__name__] = _real
