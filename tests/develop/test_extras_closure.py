#!/usr/bin/env python3
# File: tests/develop/test_extras_closure.py
"""``pip install scitex[all]`` must install every public extra.

Policy (quality-audit PS-221): every public extra is a subset of ``all``;
a public requirement missing from ``all`` silently under-installs.
"""

from __future__ import annotations

import re
from pathlib import Path

import tomllib

_PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"
_SELF_REF = re.compile(r"^scitex\[(?P<extras>[^\]]+)\]$")


def _extras() -> dict[str, list[str]]:
    data = tomllib.loads(_PYPROJECT.read_text())
    return data["project"]["optional-dependencies"]


def _requirement_name(req: str) -> str:
    return re.split(r"[\s<>=!~;\[]", req.strip(), maxsplit=1)[0].lower()


def _closure(extras: dict[str, list[str]], name: str) -> set[str]:
    seen: set[str] = set()
    reqs: set[str] = set()
    stack = [name]
    while stack:
        extra = stack.pop()
        if extra in seen:
            continue
        seen.add(extra)
        for req in extras[extra]:
            match = _SELF_REF.match(req.strip())
            if match:
                stack.extend(e.strip() for e in match["extras"].split(","))
            else:
                reqs.add(_requirement_name(req))
    return reqs


def _missing_from_all() -> dict[str, set[str]]:
    extras = _extras()
    in_all = _closure(extras, "all")
    missing = {}
    for name in extras:
        if name == "all" or name.startswith("_"):
            continue
        gap = _closure(extras, name) - in_all
        if gap:
            missing[name] = gap
    return missing


def test_every_public_extra_is_closed_under_all():
    # Arrange
    pyproject = _PYPROJECT
    # Act
    missing = _missing_from_all()
    # Assert
    assert missing == {}, f"{pyproject}: requirements absent from [all]: {missing}"


def test_all_pulls_scitex_hub_for_cloud_module_project():
    # Arrange
    extras = _extras()
    # Act
    in_all = _closure(extras, "all")
    # Assert
    assert "scitex-hub" in in_all


# EOF
