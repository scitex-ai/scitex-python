"""SciTeX datetime — thin compatibility shim for scitex-datetime.

Aliases ``scitex.datetime`` to the standalone ``scitex_datetime`` package via
``sys.modules``. ``scitex.datetime is scitex_datetime``.

Public API: linspace, normalize_timestamp, to_datetime, validate_timestamp_format,
            format_for_filename, format_for_display, get_time_delta_seconds,
            parse_patient_recording_start_format, STANDARD_FORMAT, ALTERNATIVE_FORMATS

Install: ``pip install scitex[datetime]``  (or ``pip install scitex-datetime``).
See: https://github.com/ywatanabe1989/scitex-datetime
"""

import sys as _sys

try:
    import scitex_datetime as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.datetime requires the 'scitex-datetime' package. "
        "Install with: pip install scitex[datetime]  (or: pip install scitex-datetime)"
    ) from _e

_sys.modules[__name__] = _real
