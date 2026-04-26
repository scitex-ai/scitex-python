"""SciTeX events — thin compatibility shim for scitex-events.

Aliases ``scitex.events`` to the standalone ``scitex_events`` package via
``sys.modules``. ``scitex.events is scitex_events``.

Public API: emit, latest, history, list_types, get_type_info, Event

Install: ``pip install scitex[events]``  (or ``pip install scitex-events``).
See: https://github.com/ywatanabe1989/scitex-events
"""

import sys as _sys

try:
    import scitex_events as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.events requires the 'scitex-events' package. "
        "Install with: pip install scitex[events]  (or: pip install scitex-events)"
    ) from _e

_sys.modules[__name__] = _real
