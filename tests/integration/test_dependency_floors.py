#!/usr/bin/env python3
# File: ./tests/integration/test_dependency_floors.py
"""Regression guard: the umbrella declares minimum floors, never exact pins.

Installing ``scitex`` must never silently downgrade an already-installed
(newer) SciTeX component. Exact ``==`` pins on components in the umbrella's
library metadata did exactly that (2026-11-16: installing the umbrella
replaced develop scitex-io 0.4.x / scitex-dev 0.62.30 / scitex-session 0.3.2
with the old pinned wheels, and made develop scitex-session uninstallable
next to the umbrella). Exact versions belong in experiment / deployment lock
files, not in a library's dependency declaration.

These tests read the REAL declarations -- the repository's pyproject.toml and,
when present, the installed ``scitex`` distribution metadata -- no mocks.
"""

import importlib.metadata
from pathlib import Path

import pytest
import tomllib
from packaging.requirements import Requirement

_PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"

# Publishable SciTeX ecosystem components (the set the scitex-dev PS-170
# umbrella-pin audit recognises, plus the branded scholar backends).
_ECOSYSTEM_NAMES = {"figrecipe", "newb", "socialia", "crossref-local", "openalex-local"}


def _is_component(req: Requirement) -> bool:
    name = req.name.lower().replace("_", "-")
    return (name.startswith("scitex-") or name in _ECOSYSTEM_NAMES) and name != "scitex"


def _exact_pins(requirement_strings) -> list[str]:
    offenders = []
    for raw in requirement_strings:
        req = Requirement(raw)
        if not _is_component(req):
            continue
        if any(spec.operator in ("==", "===") for spec in req.specifier):
            offenders.append(raw)
    return offenders


def _missing_floors(requirement_strings) -> list[str]:
    missing = []
    for raw in requirement_strings:
        req = Requirement(raw)
        if _is_component(req) and not any(s.operator == ">=" for s in req.specifier):
            missing.append(raw)
    return missing


def _pyproject_requirements() -> list[str]:
    project = tomllib.loads(_PYPROJECT.read_text())["project"]
    reqs = list(project.get("dependencies", []))
    for extra_reqs in project.get("optional-dependencies", {}).values():
        reqs.extend(extra_reqs)
    return reqs


def _installed_requirements_or_skip() -> list[str]:
    try:
        return importlib.metadata.requires("scitex") or []
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("scitex distribution metadata not installed")


def test_pyproject_declares_no_exact_component_pins():
    # Arrange
    requirements = _pyproject_requirements()
    # Act
    offenders = _exact_pins(requirements)
    # Assert
    assert offenders == []


def test_pyproject_component_requirements_all_have_a_floor():
    # Arrange: a bare name would let a resolver pick an ancient wheel
    # lacking APIs the umbrella imports, so every component needs >=.
    requirements = _pyproject_requirements()
    # Act
    missing = _missing_floors(requirements)
    # Assert
    assert missing == []


def test_installed_scitex_metadata_declares_no_exact_component_pins():
    # Arrange
    requirements = _installed_requirements_or_skip()
    # Act
    offenders = _exact_pins(requirements)
    # Assert
    assert offenders == []


def test_exact_pin_detector_flags_an_exact_pin():
    # Arrange: positive control so the guards above cannot pass vacuously.
    requirements = ["scitex-io==0.3.3", "scitex-dev>=0.62.2", "numpy==2.0"]
    # Act
    offenders = _exact_pins(requirements)
    # Assert
    assert offenders == ["scitex-io==0.3.3"]


# EOF
