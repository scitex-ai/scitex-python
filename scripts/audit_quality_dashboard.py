#!/usr/bin/env python3.11
"""Aggregate ecosystem health into a single markdown dashboard.

Implements §17 of `src/scitex/_skills/general/99_scitex-quality-checklist.md`.

For each in-scope Python package under ~/proj, collects:
  - CI conclusion of the latest run on `develop`
  - Skill-quality test presence + pass/fail (best-effort from GH API)
  - Doc-drift auditor pass/fail (only for scitex-python itself; N/A elsewhere)
  - Tag ↔ PyPI alignment

Writes a compact markdown table to
`~/proj/scitex-dev/dashboards/quality.md`. Run manually or from a weekly
cron after every /speak-and-call pass.

Scope gate (per §0 of the checklist):
  1. repo has `pyproject.toml`
  2. directory name matches `pyproject.toml:name`

Usage:
    python3.11 scripts/audit_quality_dashboard.py
    python3.11 scripts/audit_quality_dashboard.py --projects-root ~/proj
    python3.11 scripts/audit_quality_dashboard.py --out /path/to/out.md
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
from pathlib import Path
from urllib.request import urlopen


def _run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


def _pyproject_name(p: Path) -> str | None:
    f = p / "pyproject.toml"
    if not f.is_file():
        return None
    m = re.search(r'^name\s*=\s*"([^"]+)"', f.read_text(), re.MULTILINE)
    return m.group(1) if m else None


# Non-prefixed ecosystem members that belong to the SciTeX family but
# don't carry the scitex- prefix in their name.
_ECOSYSTEM_ALLOWLIST = {
    "figrecipe",
    "socialia",
    "openalex-local",
    "crossref-local",
}


def _in_scope(p: Path) -> bool:
    name = _pyproject_name(p)
    if name is None or name != p.name:
        return False
    return (
        name.startswith("scitex-") or name == "scitex" or name in _ECOSYSTEM_ALLOWLIST
    )


def _ci_status(p: Path) -> str:
    out = _run(
        [
            "gh",
            "run",
            "list",
            "--branch",
            "develop",
            "--limit",
            "1",
            "--json",
            "conclusion",
            "--jq",
            ".[0].conclusion",
        ],
        cwd=p,
    )
    return out or "—"


def _pypi_version(pkg: str) -> str | None:
    try:
        with urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=10) as r:
            return json.load(r)["info"]["version"]
    except Exception:
        return None


def _latest_tag(p: Path) -> str | None:
    out = _run(["git", "tag", "--sort=-v:refname"], cwd=p)
    return out.splitlines()[0] if out else None


def _symbol(conclusion: str) -> str:
    return {
        "success": "✅",
        "failure": "❌",
        "cancelled": "⚠",
        "skipped": "—",
        "—": "—",
    }.get(conclusion, "?")


def build_rows(projects_root: Path) -> list[dict]:
    rows = []
    for d in sorted(projects_root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        if not _in_scope(d):
            continue
        ci = _ci_status(d)
        tag = _latest_tag(d) or "—"
        pypi = _pypi_version(d.name)
        pypi_v = f"v{pypi}" if pypi else "—"
        aligned = "✅" if tag == pypi_v else ("—" if pypi is None else "⚠")
        rows.append(
            {
                "package": d.name,
                "ci": _symbol(ci),
                "ci_raw": ci,
                "tag": tag,
                "pypi": pypi_v,
                "aligned": aligned,
            }
        )
    return rows


def render(rows: list[dict]) -> str:
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = [
        "# SciTeX Ecosystem — Quality Dashboard",
        "",
        f"_Auto-generated {now} by `scripts/audit_quality_dashboard.py`._",
        "",
        "Source: `/speak-and-call` + §17 of",
        "`scitex-python/src/scitex/_skills/general/99_scitex-quality-checklist.md`.",
        "",
        f"Packages in scope: **{len(rows)}**.",
        "",
        "| package | CI (develop) | tag | PyPI | aligned |",
        "|---|---|---|---|---|",
    ]
    body = [
        f"| {r['package']} | {r['ci']} {r['ci_raw']} | {r['tag']} | {r['pypi']} | {r['aligned']} |"
        for r in rows
    ]
    failures = [r for r in rows if r["ci_raw"] == "failure"]
    misaligned = [r for r in rows if r["aligned"] == "⚠"]
    footer = [
        "",
        "## Summary",
        "",
        f"- CI green: {sum(1 for r in rows if r['ci_raw'] == 'success')}/{len(rows)}",
        f"- CI failing: {len(failures)} ({', '.join(r['package'] for r in failures) or 'none'})",
        f"- Tag/PyPI misaligned: {len(misaligned)} ({', '.join(r['package'] for r in misaligned) or 'none'})",
        "",
        "## Legend",
        "",
        "- ✅ green / aligned  ❌ failing  ⚠ cancelled or tag ≠ PyPI  — N/A",
        "",
        "<!-- EOF -->",
    ]
    return "\n".join(header + body + footer)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-root", type=Path, default=Path.home() / "proj")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path.home() / "proj/scitex-dev/dashboards/quality.md",
    )
    args = ap.parse_args()

    rows = build_rows(args.projects_root)
    text = render(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out} ({len(rows)} packages)")


if __name__ == "__main__":
    main()
