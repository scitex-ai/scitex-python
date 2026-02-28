#!/usr/bin/env python3
# File: scitex/audit/_runner.py

"""
Core audit orchestrator.

Discovers available tools and runs each requested checker,
returning a unified results dictionary.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Optional

from ._bandit import run_bandit
from ._format import format_json
from ._github import run_github_check
from ._pip_audit import run_pip_audit
from ._shellcheck import run_shellcheck

logger = logging.getLogger(__name__)

ALL_CHECKS = ("python", "shell", "deps", "github")

_TOOL_REQUIREMENTS = {
    "python": "bandit",
    "shell": "shellcheck",
    "deps": "pip-audit",
}


def _is_tool_available(tool_name: str) -> bool:
    """Check whether a CLI tool is on PATH."""
    return shutil.which(tool_name) is not None


def _is_gh_authenticated() -> bool:
    """Check whether gh CLI is installed and authenticated."""
    if not _is_tool_available("gh"):
        return False
    try:
        from scitex.security import check_gh_auth

        return check_gh_auth()
    except ImportError:
        return False


def _skipped_result(tool_name: str) -> dict:
    """Return a standard skipped result."""
    return {
        "status": "skipped",
        "findings": [],
        "summary": f"Skipped ({tool_name} not installed)",
    }


def audit(
    path: str = ".",
    checks: Optional[list[str]] = None,
    output_file: Optional[str] = None,
) -> dict:
    """Run security audit across multiple tools.

    Parameters
    ----------
    path : str
        Directory to scan. Defaults to current directory.
    checks : list[str] | None
        Which checks to run. Options: "python", "shell", "deps", "github".
        None means run all available checks.
    output_file : str | None
        If given, write JSON report to this path.

    Returns
    -------
    dict
        Keys are check names, values have {status, findings, summary}.
    """
    target = Path(path).resolve()
    requested = list(checks) if checks else list(ALL_CHECKS)
    results: dict = {}

    for check in requested:
        if check not in ALL_CHECKS:
            logger.warning("Unknown check %r, skipping", check)
            continue

        if check == "github":
            if not _is_gh_authenticated():
                logger.info("GitHub CLI not available or not authenticated, skipping")
                results["github"] = _skipped_result("gh")
                continue
            results["github"] = run_github_check()

        else:
            tool_name = _TOOL_REQUIREMENTS[check]
            if not _is_tool_available(tool_name):
                logger.info("%s not installed, skipping %s check", tool_name, check)
                results[check] = _skipped_result(tool_name)
                continue

            if check == "python":
                results["python"] = run_bandit(target)
            elif check == "shell":
                results["shell"] = run_shellcheck(target)
            elif check == "deps":
                results["deps"] = run_pip_audit(target)

    if output_file:
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(format_json(results))
        logger.info("Report written to %s", out_path)

    return results


# EOF
