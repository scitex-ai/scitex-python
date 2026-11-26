#!/usr/bin/env python3
# File: tests/scitex/test_lifecycle_leaves.py
"""Research-lifecycle leaves reachable through the umbrella (issue #428).

``scitex[all]`` must install scitex-dataset, scitex-hpc and scitex-live-paper,
and each installed leaf is reachable as ``stx.<leaf>`` (decision on record:
any installed leaf enables ``stx.<leaf>``).
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest
import tomllib

import scitex
from scitex.re_export import EXTERNAL_REEXPORTS

_PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"
_SELF_REF = re.compile(r"^scitex\[(?P<extras>[^\]]+)\]$")

LEAVES = {
    "dataset": ("scitex-dataset", "scitex_dataset"),
    "hpc": ("scitex-hpc", "scitex_hpc"),
    "live_paper": ("scitex-live-paper", "scitex_live_paper"),
}


def _all_requirement_names() -> set[str]:
    extras = tomllib.loads(_PYPROJECT.read_text())["project"]["optional-dependencies"]
    names, seen, stack = set(), set(), ["all"]
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
                names.add(re.split(r"[\s<>=!~;\[]", req.strip(), maxsplit=1)[0].lower())
    return names


@pytest.mark.parametrize("short", sorted(LEAVES))
def test_all_extra_installs_leaf_distribution(short):
    # Arrange
    distribution = LEAVES[short][0]
    # Act
    names = _all_requirement_names()
    # Assert
    assert distribution in names


@pytest.mark.parametrize("short", sorted(LEAVES))
def test_umbrella_maps_leaf_to_its_standalone(short):
    # Arrange
    module = LEAVES[short][1]
    # Act
    mapped = EXTERNAL_REEXPORTS.get(short)
    # Assert
    assert mapped == module


@pytest.mark.parametrize("short", sorted(LEAVES))
def test_umbrella_exposes_leaf_attribute(short):
    # Arrange
    # Act
    exported = (short in scitex.__all__, short in vars(scitex))
    # Assert
    assert exported == (True, True)


@pytest.fixture(params=sorted(LEAVES))
def installed_leaf(request):
    """(short, standalone module) for each leaf installed here; else skip."""
    short = request.param
    return short, pytest.importorskip(LEAVES[short][1])


def test_installed_leaf_resolves_through_umbrella(installed_leaf):
    # Arrange
    short, standalone = installed_leaf
    # Act
    via_umbrella = importlib.import_module(f"scitex.{short}")
    # Assert
    assert via_umbrella.__file__ == standalone.__file__
