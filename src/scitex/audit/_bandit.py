#!/usr/bin/env python3
# File: scitex/audit/_bandit.py

"""
Bandit (Python static security analysis) checker.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_EXCLUDE_DIRS = ".venv,node_modules,__pycache__,.git"


def run_bandit(path: Path) -> dict:
    """Run bandit on the given path and return normalized results.

    Parameters
    ----------
    path : Path
        Directory to scan recursively.

    Returns
    -------
    dict
        {status, findings, summary} where findings are normalized dicts.
    """
    try:
        result = subprocess.run(
            [
                "bandit",
                "-r",
                str(path),
                "-f",
                "json",
                "--exclude",
                _EXCLUDE_DIRS,
                "-q",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "findings": [], "summary": "Timed out"}
    except Exception as exc:
        return {"status": "error", "findings": [], "summary": str(exc)}

    # Bandit returns exit code 1 when findings exist -- that is not an error
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return {
            "status": "error",
            "findings": [],
            "summary": f"Failed to parse bandit output: {result.stderr[:200]}",
        }

    raw_findings = data.get("results", [])
    findings = [
        {
            "severity": f.get("issue_severity", "UNDEFINED"),
            "confidence": f.get("issue_confidence", "UNDEFINED"),
            "file": f.get("filename", ""),
            "line": f.get("line_number", 0),
            "test_id": f.get("test_id", ""),
            "message": f.get("issue_text", ""),
        }
        for f in raw_findings
    ]

    if not findings:
        return {"status": "ok", "findings": [], "summary": "No issues found"}

    high = sum(1 for f in findings if f["severity"] == "HIGH")
    medium = sum(1 for f in findings if f["severity"] == "MEDIUM")
    low = sum(1 for f in findings if f["severity"] == "LOW")
    summary = f"{len(findings)} issues ({high} high, {medium} medium, {low} low)"

    return {"status": "findings", "findings": findings, "summary": summary}


# EOF
