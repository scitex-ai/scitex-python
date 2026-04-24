#!/usr/bin/env python3.11
"""Flag non-ASCII (Hiragana / Katakana / Kanji) in source + docs.

Policy: the SciTeX ecosystem is English-only. This auditor catches
Japanese leaking into comments, docstrings, or prose. Intentional i18n
content (TTS example strings, foreign brand names in data-extraction
code) can be exempted by appending an `# i18n-ok` (or `<!-- i18n-ok -->`
for markdown) marker to the line.

Scope (per §0 of 99_scitex-quality-checklist.md):
  - `src/**/*.py` and `src/**/*.md` under each ecosystem repo
  - directory name must match `pyproject.toml:name`
  - excludes `__pycache__/`, `node_modules/`, vendored `.claude/`
    skill mirrors, and `docs/to_claude/` skill mirrors (those clean up
    automatically when the upstream translates)

Exit 0 if every file is English-or-exempted; exit 1 if any file has a
non-exempted CJK hit. Prints one line per violating file with line
numbers.

Usage:
    python3.11 scripts/audit_english_only.py
    python3.11 scripts/audit_english_only.py --projects-root ~/proj
    python3.11 scripts/audit_english_only.py --format github  # ::error:: annotations
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CJK_RE = re.compile(r"[\u3000-\u30ff\u4e00-\u9faf]")
I18N_OK_RE = re.compile(r"(?:#|<!--)\s*i18n-ok\b")
EXCLUDE_PATH_PARTS = {
    "__pycache__",
    "node_modules",
    ".claude",
    "docs/to_claude",
}
ALLOWED_SUFFIXES = {".py", ".md"}


def _pyproject_name(p: Path) -> str | None:
    f = p / "pyproject.toml"
    if not f.is_file():
        return None
    m = re.search(r'^name\s*=\s*"([^"]+)"', f.read_text(), re.MULTILINE)
    return m.group(1) if m else None


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


def _excluded(path: Path) -> bool:
    s = str(path)
    return any(part in s for part in EXCLUDE_PATH_PARTS)


def scan_file(fp: Path) -> list[tuple[int, str]]:
    """Return (lineno, line) for lines with non-exempt CJK.

    A line is considered exempted if an `# i18n-ok` or `<!-- i18n-ok -->`
    marker appears on the line itself OR on one of the two preceding
    lines (covers docstring/class pairs and formatter-split lines).
    """
    try:
        text = fp.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    lines = text.splitlines()
    hits = []
    for i, line in enumerate(lines):
        if not CJK_RE.search(line):
            continue
        # Check ±2 lines — covers docstring/class pairs and formatter
        # splits where the marker may land on the next line.
        window = lines[max(0, i - 2) : min(len(lines), i + 3)]
        if any(I18N_OK_RE.search(w) for w in window):
            continue
        hits.append((i + 1, line))
    return hits


def scan_repo(repo: Path) -> dict[Path, list[tuple[int, str]]]:
    out: dict[Path, list[tuple[int, str]]] = {}
    src = repo / "src"
    if not src.is_dir():
        return out
    for fp in src.rglob("*"):
        if not fp.is_file():
            continue
        if fp.suffix not in ALLOWED_SUFFIXES:
            continue
        if _excluded(fp):
            continue
        hits = scan_file(fp)
        if hits:
            out[fp] = hits
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-root", type=Path, default=Path.home() / "proj")
    ap.add_argument("--format", choices=["plain", "github"], default="plain")
    args = ap.parse_args()

    total_files = 0
    total_hits = 0
    any_fail = False

    for d in sorted(args.projects_root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        if not _in_scope(d):
            continue
        violations = scan_repo(d)
        if not violations:
            continue
        any_fail = True
        print(f"\n[{d.name}]")
        for fp, hits in violations.items():
            rel = fp.relative_to(d)
            total_files += 1
            total_hits += len(hits)
            for lineno, line in hits:
                preview = line.strip()[:120]
                if args.format == "github":
                    print(
                        f"::error file={fp},line={lineno}::"
                        f"non-English content (add `# i18n-ok` if intentional): {preview}"
                    )
                else:
                    print(f"  {rel}:{lineno}  {preview}")

    if any_fail:
        print(
            f"\nFAIL — {total_files} file(s), {total_hits} line(s) with "
            "non-English content. Translate to English or annotate the line "
            "with `# i18n-ok` / `<!-- i18n-ok -->` if the non-ASCII string is "
            "legitimate data (TTS demo, foreign brand name, etc)."
        )
        return 1

    print("PASS — every source/doc file is English or i18n-ok annotated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
