#!/usr/bin/env python3
# File: ./scripts/release/sync_member_floors.py
"""Keep the umbrella's SciTeX member floors at the latest PyPI release.

The umbrella declares its members (``scitex-*``, figrecipe, ...) with ``>=``
floors (scitex-dev release-and-pin doctrine, scitex-python#393). A floor that
lags far behind PyPI lets ``pip install scitex`` keep -- or a resolver pick --
an old member that the released umbrella was never tested against; an exact
``==`` pin is worse, because it actively DOWNGRADES a newer installed member
(scitex 2.30.8 on PyPI downgraded scitex-dev 0.62.30 -> 0.28.0 on
``pip install -U 'scitex[all]'``).

Usage::

    python scripts/release/sync_member_floors.py --check   # release gate, exit 1 on drift
    python scripts/release/sync_member_floors.py --write   # raise every floor to PyPI latest

``--check`` refuses (exit 1) when any member is exact-pinned, has no floor, or
has a floor older than its PyPI latest, and when PyPI cannot be queried: a
release gate that silently passes on a network error is no gate. ``--write``
rewrites only the version text of each member declaration, preserving
comments, ordering and extras.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

from packaging.version import Version

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"

# The publishable ecosystem members the umbrella depends on (the set the
# scitex-dev PS-170 audit and tests/integration/test_dependency_floors.py use).
_ECOSYSTEM = r"figrecipe|newb|socialia|crossref-local|openalex-local"
_MEMBER_RE = re.compile(
    r'"(?P<name>scitex-[a-z0-9-]+|' + _ECOSYSTEM + r")"
    r"(?P<extras>\[[^\]]*\])?"
    r"(?P<op>==|>=|~=|<=|<|>|!=)?"
    r'(?P<ver>[0-9][0-9A-Za-z.+\-]*)?"'
)

PypiQuery = Callable[[str], Optional[str]]


def query_pypi_latest(name: str, timeout: float = 20.0) -> Optional[str]:
    """Return PyPI's current latest version of ``name``, or None on failure."""
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.load(response)["info"]["version"]
    except (OSError, ValueError, KeyError):
        return None


def find_members(text: str) -> list[re.Match]:
    """Every member declaration in the pyproject text, in file order."""
    return list(_MEMBER_RE.finditer(text))


def resolve_latest(names: set[str], query: PypiQuery) -> dict[str, Optional[str]]:
    """Query PyPI latest for each name concurrently."""
    ordered = sorted(names)
    with ThreadPoolExecutor(max_workers=16) as pool:
        return dict(zip(ordered, pool.map(query, ordered)))


def find_problems(text: str, latest: dict[str, Optional[str]]) -> list[str]:
    """Human-readable problems; an empty list means every floor is current."""
    problems: list[str] = []
    for match in find_members(text):
        name, op, ver = match["name"], match["op"], match["ver"]
        newest = latest.get(name)
        if newest is None:
            problems.append(f"{name}: could not resolve PyPI latest")
        elif op != ">=" or ver is None:
            problems.append(f"{match[0]}: needs a '>=' floor (latest {newest})")
        elif Version(ver) < Version(newest):
            problems.append(f"{match[0]}: floor older than PyPI latest {newest}")
    return problems


def raise_floors(text: str, latest: dict[str, Optional[str]]) -> str:
    """Rewrite every member declaration to ``>=<PyPI latest>``."""

    def _replace(match: re.Match) -> str:
        newest = latest.get(match["name"])
        if newest is None:
            raise RuntimeError(f"no PyPI latest for {match['name']}; refusing")
        if match["op"] == ">=" and Version(match["ver"]) > Version(newest):
            return match[0]  # never lower a floor (e.g. a just-tagged member)
        return f'"{match["name"]}{match["extras"] or ""}>={newest}"'

    return _MEMBER_RE.sub(_replace, text)


def main(argv: Optional[list[str]] = None, query: PypiQuery = query_pypi_latest) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="exit 1 on any stale floor")
    mode.add_argument(
        "--write", action="store_true", help="raise floors to PyPI latest"
    )
    parser.add_argument("--pyproject", type=Path, default=PYPROJECT)
    args = parser.parse_args(argv)

    text = args.pyproject.read_text()
    latest = resolve_latest({m["name"] for m in find_members(text)}, query)

    if args.write:
        updated = raise_floors(text, latest)
        args.pyproject.write_text(updated)
        changed = sum(a != b for a, b in zip(text.splitlines(), updated.splitlines()))
        print(f"raised {changed} member declaration line(s) in {args.pyproject}")
        return 0

    problems = find_problems(text, latest)
    for problem in problems:
        print(f"STALE: {problem}", file=sys.stderr)
    if problems:
        print(
            f"{len(problems)} stale member declaration(s); "
            "run: python scripts/release/sync_member_floors.py --write",
            file=sys.stderr,
        )
        return 1
    print(f"OK: all {len(latest)} member floors are at PyPI latest")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# EOF
