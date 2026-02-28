#!/usr/bin/env python3
# File: scitex/audit/_format.py

"""
Formatters for audit results.

Provides colored terminal output and JSON serialization.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone

_STATUS_LABELS = {
    "ok": "OK",
    "findings": "FINDINGS",
    "skipped": "SKIPPED",
    "error": "ERROR",
}

_STATUS_COLORS = {
    "ok": "green",
    "findings": "red",
    "skipped": "yellow",
    "error": "magenta",
}

_MAX_DISPLAY_FINDINGS = 5


def _style(text: str, fg: str, bold: bool = False) -> str:
    """Apply click.style if available, else return plain text."""
    try:
        import click

        return click.style(text, fg=fg, bold=bold)
    except ImportError:
        return text


def format_text(results: dict) -> str:
    """Format audit results for terminal display with color.

    Parameters
    ----------
    results : dict
        Audit results from ``audit()``.

    Returns
    -------
    str
        Colored text suitable for terminal output.
    """
    lines: list[str] = []
    lines.append("")
    lines.append(_style("Security Audit Report", fg="white", bold=True))
    lines.append("=" * 50)
    lines.append("")

    for check_name, data in results.items():
        status = data.get("status", "error")
        label = _STATUS_LABELS.get(status, status.upper())
        color = _STATUS_COLORS.get(status, "white")

        badge = _style(f"[{label}]", fg=color, bold=True)
        title = _style(check_name.upper(), fg="white", bold=True)
        lines.append(f"  {title}  {badge}")
        lines.append(f"    {data.get('summary', 'No summary')}")

        findings = data.get("findings", [])
        if findings:
            shown = findings[:_MAX_DISPLAY_FINDINGS]
            for f in shown:
                detail = _format_finding_line(check_name, f)
                lines.append(f"      - {detail}")
            remaining = len(findings) - len(shown)
            if remaining > 0:
                lines.append(_style(f"      ... and {remaining} more", fg="yellow"))
        lines.append("")

    lines.append("=" * 50)
    return "\n".join(lines)


def _format_finding_line(check_name: str, finding: dict) -> str:
    """Build a one-line summary for a single finding."""
    if check_name == "python":
        return (
            f"[{finding.get('severity', '?')}] "
            f"{finding.get('file', '?')}:{finding.get('line', '?')} "
            f"{finding.get('message', '')}"
        )
    if check_name == "shell":
        return (
            f"[{finding.get('level', '?')}] "
            f"{finding.get('file', '?')}:{finding.get('line', '?')} "
            f"SC{finding.get('code', '?')}: {finding.get('message', '')}"
        )
    if check_name == "deps":
        return (
            f"{finding.get('package', '?')}=={finding.get('version', '?')} "
            f"({finding.get('vuln_id', '?')})"
        )
    if check_name == "github":
        return (
            f"[{finding.get('category', '?')}] "
            f"{finding.get('summary', finding.get('secretType', ''))}"
        )
    return str(finding)


def _get_tool_version(tool: str) -> str:
    """Try to get tool version string."""
    import subprocess

    try:
        result = subprocess.run(
            [tool, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        first_line = result.stdout.strip().split("\n")[0]
        return first_line
    except Exception:
        return "unknown"


def format_json(results: dict) -> str:
    """Serialize audit results to a JSON string with metadata.

    Parameters
    ----------
    results : dict
        Audit results from ``audit()``.

    Returns
    -------
    str
        Pretty-printed JSON string.
    """
    tool_map = {
        "python": "bandit",
        "shell": "shellcheck",
        "deps": "pip-audit",
        "github": "gh",
    }

    versions = {}
    for check_name in results:
        tool = tool_map.get(check_name)
        if tool and shutil.which(tool):
            versions[check_name] = _get_tool_version(tool)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_versions": versions,
        "results": results,
    }
    return json.dumps(report, indent=2, default=str)


# EOF
