"""SciTeX security — thin compatibility shim for scitex-security.

Aliases ``scitex.security`` to the standalone ``scitex_security`` package via
``sys.modules``. ``scitex.security is scitex_security``.

Public API: check_github_alerts, save_alerts_to_file, get_latest_alerts_file,
            format_alerts_report, GitHubSecurityError

Install: ``pip install scitex[security]``  (or ``pip install scitex-security``).
See: https://github.com/ywatanabe1989/scitex-security
"""

import sys as _sys

try:
    import scitex_security as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.security requires the 'scitex-security' package. "
        "Install with: pip install scitex[security]  (or: pip install scitex-security)"
    ) from _e

_sys.modules[__name__] = _real
