#!/usr/bin/env python3
# File: scitex/audit/_shellcheck.py

"""
ShellCheck (shell script analysis) checker.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_SKIP_DIRS = {".venv", "node_modules", ".git"}


def _collect_shell_files(path: Path) -> list[Path]:
    """Find all *.sh files, skipping excluded directories."""
    files = []
    for sh_file in path.glob("**/*.sh"):
        if any(part in _SKIP_DIRS for part in sh_file.parts):
            continue
        files.append(sh_file)
    return sorted(files)


def run_shellcheck(path: Path) -> dict:
    """Run shellcheck on all shell scripts under the given path.

    Parameters
    ----------
    path : Path
        Directory to scan recursively for *.sh files.

    Returns
    -------
    dict
        {status, findings, summary} where findings are normalized dicts.
    """
    shell_files = _collect_shell_files(path)

    if not shell_files:
        return {"status": "ok", "findings": [], "summary": "No shell files found"}

    try:
        result = subprocess.run(
            ["shellcheck", "-f", "json"] + [str(f) for f in shell_files],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "findings": [], "summary": "Timed out"}
    except Exception as exc:
        return {"status": "error", "findings": [], "summary": str(exc)}

    # shellcheck returns exit code 1 when findings exist
    try:
        raw = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        return {
            "status": "error",
            "findings": [],
            "summary": f"Failed to parse shellcheck output: {result.stderr[:200]}",
        }

    findings = [
        {
            "level": item.get("level", "unknown"),
            "file": item.get("file", ""),
            "line": item.get("line", 0),
            "code": item.get("code", 0),
            "message": item.get("message", ""),
        }
        for item in raw
    ]

    if not findings:
        return {"status": "ok", "findings": [], "summary": "No issues found"}

    affected_files = len({f["file"] for f in findings})
    summary = f"{len(findings)} issues in {affected_files} files"

    return {"status": "findings", "findings": findings, "summary": summary}


# EOF
