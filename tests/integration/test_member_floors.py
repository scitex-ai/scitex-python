#!/usr/bin/env python3
# File: ./tests/integration/test_member_floors.py
"""scripts/release/member_floors.py: minimal, honest member floors.

The release preflight runs ``check`` (no exact pin, every member has a
published ``>=`` floor) and the ``min-versions`` CI leg installs the umbrella
through ``constraints`` (every member at exactly its floor). These tests drive
the real script on real temp files; PyPI is replaced through the ``query``
dependency-injection seam (a plain function, no mocks, no network).
"""

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "scripts" / "release" / "member_floors.py"
_spec = importlib.util.spec_from_file_location("member_floors", _SCRIPT)
floors = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(floors)

_RELEASES = {
    "scitex-io": {"0.2.16", "0.4.3", "0.7.0"},
    "scitex-dev": {"0.66.1", "0.67.0"},
    "figrecipe": {"0.28.13", "0.45.1"},
}

_PYPROJECT = """\
[project]
name = "scitex"
dependencies = [
    "numpy",
    "scitex-io>=0.4.3",  # comment kept
    "figrecipe>=0.28.13",
]
[project.optional-dependencies]
dev = ["scitex-dev[local-store]>=0.67.0"]
io = ["scitex-io>=0.2.16; python_version >= '3.10'"]
"""


def _query(name):
    return _RELEASES.get(name)


def _write(tmp_path, text=_PYPROJECT):
    path = tmp_path / "pyproject.toml"
    path.write_text(text)
    return path


def _check(path):
    return floors.main(["--pyproject", str(path), "check"], query=_query)


def test_check_passes_on_published_minimum_floors(tmp_path):
    # Arrange
    path = _write(tmp_path)
    # Act
    rc = _check(path)
    # Assert
    assert rc == 0


def test_check_refuses_an_exact_member_pin(tmp_path, capsys):
    # Arrange
    path = _write(
        tmp_path, _PYPROJECT.replace("figrecipe>=0.28.13", "figrecipe==0.45.1")
    )
    # Act
    rc = _check(path)
    # Assert
    assert rc == 1 and "figrecipe==0.45.1: exact pin" in capsys.readouterr().err


def test_check_refuses_a_member_without_a_floor(tmp_path, capsys):
    # Arrange
    path = _write(tmp_path, _PYPROJECT.replace('"figrecipe>=0.28.13"', '"figrecipe"'))
    # Act
    rc = _check(path)
    # Assert
    assert rc == 1 and "figrecipe: needs a '>=' floor" in capsys.readouterr().err


def test_check_refuses_an_unpublished_floor(tmp_path, capsys):
    # Arrange: a floor that names no release can never be installed
    path = _write(tmp_path, _PYPROJECT.replace("scitex-io>=0.4.3", "scitex-io>=0.4.4"))
    # Act
    rc = _check(path)
    # Assert
    assert rc == 1 and "not a published release" in capsys.readouterr().err


def test_check_accepts_a_floor_older_than_pypi_latest(tmp_path):
    # Arrange: 0.4.3 < latest 0.7.0 is the POINT of a minimum, not drift
    path = _write(tmp_path)
    # Act
    rc = _check(path)
    # Assert
    assert rc == 0 and max(_RELEASES["scitex-io"], key=floors._version_key) == "0.7.0"


def test_check_fails_closed_when_pypi_is_unreachable(tmp_path, capsys):
    # Arrange
    path = _write(tmp_path)
    # Act
    rc = floors.main(["--pyproject", str(path), "check"], query=lambda name: None)
    # Assert
    assert rc == 1 and "could not query PyPI" in capsys.readouterr().err


def test_constraints_pin_every_member_to_its_highest_floor(tmp_path):
    # Arrange: scitex-io carries 0.4.3 (core) and 0.2.16 (extra)
    path = _write(tmp_path)
    out = tmp_path / "min.txt"
    # Act
    floors.main(["--pyproject", str(path), "constraints", str(out)])
    # Assert
    assert out.read_text().splitlines() == [
        "figrecipe==0.28.13",
        "scitex-dev==0.67.0",
        "scitex-io==0.4.3",
    ]


def test_lowest_mismatches_name_the_floor_to_raise():
    # Arrange: lowest-direct had to lift scitex-io above its floor
    lock = "figrecipe==0.28.13\nscitex-io==0.4.5\n    # via -r req.in\n"
    # Act
    problems = floors.lowest_mismatches(
        {"figrecipe": "0.28.13", "scitex-io": "0.4.3", "scitex-dev": "0.67.0"}, lock
    )
    # Assert
    assert problems == [
        "scitex-dev: missing from the lowest-direct resolution",
        "scitex-io>=0.4.3: cannot be installed with the other floors; "
        "lowest-direct resolves 0.4.5 -- raise the floor to 0.4.5",
    ]


def test_repository_pyproject_passes_the_offline_part_of_check():
    # Arrange: the real umbrella, every floor treated as published
    text = (_ROOT / "pyproject.toml").read_text()
    declared = floors.declared_floors(text)
    releases = {name: {version} for name, version in declared.items()}
    # Act
    problems = floors.find_problems(text, releases)
    # Assert
    assert problems == []


# EOF
