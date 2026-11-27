#!/usr/bin/env python3
# File: ./scripts/release/member_floors.py
"""Keep the umbrella's SciTeX member floors minimal and honest.

The umbrella declares every member (``scitex-*``, figrecipe, ...) with a
``>=`` floor: the OLDEST release that provides what the umbrella imports or
re-exports. It never exact-pins a member and never requires a floor to be
PyPI latest. Either one forces an umbrella release for every member release,
and an exact pin also downgrades members that users installed directly
(scitex 2.30.8 downgraded scitex-dev 0.62.30 -> 0.28.0 on
``pip install -U 'scitex[all]'``).

The ``min-versions`` CI leg keeps the floors honest: it installs the umbrella
with every member constrained to exactly its floor (``constraints``) and runs
the test suite against that set.

Usage::

    python scripts/release/member_floors.py check
        # exit 1 on an exact pin, a missing floor, or a floor that is not a
        # published PyPI release (network; fails closed). Release preflight.
    python scripts/release/member_floors.py constraints OUT
        # write `name==floor` for every member (stdlib only; used by CI
        # through UV_CONSTRAINT before uv is installed)
    python scripts/release/member_floors.py lowest [--python 3.12]
        # developer aid (needs uv): resolve the member requirements with
        # `--resolution lowest-direct` and list floors that cannot be
        # installed together, with the version each must be raised to

A member release that depends on the umbrella itself is circular (scitex-dev
PS-139); ``lowest`` excludes every such release with the constraint
``scitex<0``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

import tomllib

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"
UMBRELLA = "scitex"

# The publishable ecosystem members the umbrella depends on (the set the
# scitex-dev PS-170 audit and tests/integration/test_dependency_floors.py use).
_MEMBER = r"scitex-[a-z0-9-]+|figrecipe|newb|socialia|crossref-local|openalex-local"
# `name[extras] <specifiers> ; marker` -- a PEP 508 string without a URL.
_REQ_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*"
    r"(?P<spec>[^;]*)(?:;.*)?$"
)
_CLAUSE_RE = re.compile(r"(===|==|>=|<=|~=|!=|<|>)\s*([^\s,]+)")
_PIN_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)", re.MULTILINE)

ReleasesQuery = Callable[[str], Optional[set]]


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _version_key(version: str) -> tuple:
    return tuple(int(p) if p.isdigit() else -1 for p in re.split(r"[.+-]", version))


def member_declarations(pyproject_text: str) -> list[tuple[str, str, list]]:
    """``(requirement, name, [(op, version), ...])`` for every member line."""
    project = tomllib.loads(pyproject_text)["project"]
    raw = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        raw.extend(group)
    out = []
    for line in raw:
        match = _REQ_RE.match(line)
        if not match:
            continue
        name = _canonical(match["name"])
        if name == UMBRELLA or not re.fullmatch(_MEMBER, name):
            continue
        out.append((line, name, _CLAUSE_RE.findall(match["spec"])))
    return out


def declared_floors(pyproject_text: str) -> dict[str, str]:
    """The highest ``>=`` floor declared for each member across all tables."""
    floors: dict[str, str] = {}
    for _line, name, clauses in member_declarations(pyproject_text):
        for op, version in clauses:
            if op == ">=" and (
                name not in floors or _version_key(version) > _version_key(floors[name])
            ):
                floors[name] = version
    return floors


def query_pypi_releases(name: str, timeout: float = 20.0) -> Optional[set]:
    """Return the set of non-yanked release versions of ``name``, or None."""
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            releases = json.load(response)["releases"]
    except (OSError, ValueError, KeyError):
        return None
    return {
        version
        for version, files in releases.items()
        if files and not all(f.get("yanked") for f in files)
    }


def find_problems(pyproject_text: str, releases: dict) -> list[str]:
    """Human-readable problems; an empty list means every declaration is sound."""
    problems: list[str] = []
    for line, name, clauses in member_declarations(pyproject_text):
        ops = {op for op, _ in clauses}
        if ops & {"==", "==="}:
            problems.append(f"{line}: exact pin; declare the minimum with '>='")
            continue
        floors = [v for op, v in clauses if op == ">="]
        if not floors:
            problems.append(f"{line}: needs a '>=' floor")
            continue
        published = releases.get(name)
        if published is None:
            problems.append(f"{name}: could not query PyPI releases")
        elif max(floors, key=_version_key) not in published:
            problems.append(f"{line}: the floor is not a published release")
    return problems


def cmd_check(path: Path, query: ReleasesQuery) -> int:
    text = path.read_text()
    names = sorted({name for _l, name, _c in member_declarations(text)})
    with ThreadPoolExecutor(max_workers=16) as pool:
        releases = dict(zip(names, pool.map(query, names)))
    problems = find_problems(text, releases)
    for problem in problems:
        print(f"FLOOR: {problem}", file=sys.stderr)
    if problems:
        print(f"{len(problems)} member declaration problem(s)", file=sys.stderr)
        return 1
    print(f"OK: {len(names)} members declare published '>=' floors")
    return 0


def cmd_constraints(path: Path, out: Path) -> int:
    floors = declared_floors(path.read_text())
    out.write_text("".join(f"{n}=={v}\n" for n, v in sorted(floors.items())))
    print(f"wrote {len(floors)} member floor constraints to {out}")
    return 0


def lowest_mismatches(floors: dict[str, str], lock_text: str) -> list[str]:
    """Floors that a lowest-direct resolution had to raise (or drop)."""
    pins = {_canonical(n): v for n, v in _PIN_RE.findall(lock_text)}
    problems = []
    for name, floor in sorted(floors.items()):
        got = pins.get(name)
        if got is None:
            problems.append(f"{name}: missing from the lowest-direct resolution")
        elif _version_key(got) != _version_key(floor):
            problems.append(
                f"{name}>={floor}: cannot be installed with the other floors; "
                f"lowest-direct resolves {got} -- raise the floor to {got}"
            )
    return problems


def cmd_lowest(path: Path, python: str) -> int:
    text = path.read_text()
    lines = sorted({line for line, _n, _c in member_declarations(text)})
    with tempfile.TemporaryDirectory() as tmp:
        req, con, lock = (Path(tmp) / n for n in ("req.in", "con.txt", "lock.txt"))
        req.write_text("\n".join(lines) + "\n")
        con.write_text(f"{UMBRELLA}<0\n")
        run = subprocess.run(
            [
                "uv",
                "pip",
                "compile",
                "--quiet",
                "--resolution",
                "lowest-direct",
                "--python-version",
                python,
                str(req),
                "-c",
                str(con),
                "-o",
                str(lock),
            ],
            capture_output=True,
            text=True,
        )
        if run.returncode:
            print(run.stderr, file=sys.stderr)
            return run.returncode
        problems = lowest_mismatches(declared_floors(text), lock.read_text())
    for problem in problems:
        print(f"FLOOR: {problem}", file=sys.stderr)
    if problems:
        return 1
    print("OK: every member floor resolves at lowest-direct")
    return 0


def main(
    argv: Optional[list[str]] = None, query: ReleasesQuery = query_pypi_releases
) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pyproject", type=Path, default=PYPROJECT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="exit 1 on an exact pin or an unpublished floor")
    con = sub.add_parser("constraints", help="write name==floor constraints")
    con.add_argument("out", type=Path)
    low = sub.add_parser("lowest", help="lowest-direct consistency of the floors")
    low.add_argument("--python", default="3.12")
    args = parser.parse_args(argv)

    if args.command == "check":
        return cmd_check(args.pyproject, query)
    if args.command == "constraints":
        return cmd_constraints(args.pyproject, args.out)
    return cmd_lowest(args.pyproject, args.python)


if __name__ == "__main__":
    sys.exit(main())

# EOF
