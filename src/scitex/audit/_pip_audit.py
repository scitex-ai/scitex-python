#!/usr/bin/env python3
# File: scitex/audit/_pip_audit.py

"""
pip-audit (dependency vulnerability) checker.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run_pip_audit(path: Path) -> dict:
    """Run pip-audit and return normalized results.

    If a requirements.txt exists under *path*, it is used as the input.
    Otherwise pip-audit scans the current environment.

    Parameters
    ----------
    path : Path
        Directory that may contain a requirements.txt.

    Returns
    -------
    dict
        {status, findings, summary} where findings are normalized dicts.
    """
    cmd = ["pip-audit", "--format=json", "--progress-spinner=off"]

    requirements = path / "requirements.txt"
    if requirements.is_file():
        cmd.extend(["-r", str(requirements)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {"status": "error", "findings": [], "summary": "Timed out"}
    except Exception as exc:
        return {"status": "error", "findings": [], "summary": str(exc)}

    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return {
            "status": "error",
            "findings": [],
            "summary": f"Failed to parse pip-audit output: {result.stderr[:200]}",
        }

    raw = data.get("dependencies", [])
    findings = []
    for dep in raw:
        for vuln in dep.get("vulns", []):
            findings.append(
                {
                    "package": dep.get("name", ""),
                    "version": dep.get("version", ""),
                    "vuln_id": vuln.get("id", ""),
                    "description": vuln.get("description", ""),
                    "fix_versions": vuln.get("fix_versions", []),
                }
            )

    if not findings:
        return {"status": "ok", "findings": [], "summary": "No vulnerabilities found"}

    affected_packages = len({f["package"] for f in findings})
    summary = f"{len(findings)} vulnerabilities in {affected_packages} packages"

    return {"status": "findings", "findings": findings, "summary": summary}


# EOF
