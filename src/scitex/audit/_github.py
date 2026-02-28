#!/usr/bin/env python3
# File: scitex/audit/_github.py

"""
GitHub security alerts checker.

Delegates to scitex.security for the actual API calls.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def run_github_check(repo: Optional[str] = None) -> dict:
    """Fetch GitHub security alerts and return normalized results.

    Parameters
    ----------
    repo : str | None
        Repository in "owner/repo" format. None uses the current repo.

    Returns
    -------
    dict
        {status, findings, summary} in the standard audit format.
    """
    try:
        from scitex.security import GitHubSecurityError, check_github_alerts
    except ImportError:
        return {
            "status": "error",
            "findings": [],
            "summary": "scitex.security module not available",
        }

    try:
        alerts = check_github_alerts(repo)
    except GitHubSecurityError as exc:
        return {"status": "error", "findings": [], "summary": str(exc)}

    total = sum(len(v) for v in alerts.values())
    findings = []
    for category, items in alerts.items():
        for item in items:
            findings.append({"category": category, **item})

    if total == 0:
        return {"status": "ok", "findings": [], "summary": "No open alerts"}

    parts = [f"{len(alerts[k])} {k}" for k in alerts if alerts[k]]
    summary = f"{total} alerts ({', '.join(parts)})"

    return {"status": "findings", "findings": findings, "summary": summary}


# EOF
