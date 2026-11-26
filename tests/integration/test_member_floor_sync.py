#!/usr/bin/env python3
# File: ./tests/integration/test_member_floor_sync.py
"""The release gate that refuses umbrella member floors older than PyPI latest.

scripts/release/sync_member_floors.py runs ``--check`` in the release
workflow's preflight. These tests drive the real script through its
``query`` dependency-injection seam (a plain function, no mocks, no network).
"""

import importlib.util
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "release"
    / "sync_member_floors.py"
)
_spec = importlib.util.spec_from_file_location("sync_member_floors", _SCRIPT)
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)

_LATEST = {"scitex-io": "0.7.0", "figrecipe": "0.45.1", "scitex-dev": "0.66.1"}

_PYPROJECT = """\
[project]
name = "scitex"
dependencies = [
    "numpy",
    "scitex-io>=0.4.3",  # comment kept
    "figrecipe==0.29.9",
]
[project.optional-dependencies]
dev = ["scitex-dev[mcp]>=0.66.1"]
"""


def _query(name):
    return _LATEST.get(name)


def _write(tmp_path, text=_PYPROJECT):
    path = tmp_path / "pyproject.toml"
    path.write_text(text)
    return path


def _check(path):
    return sync.main(["--check", "--pyproject", str(path)], query=_query)


def _write_floors(path):
    sync.main(["--write", "--pyproject", str(path)], query=_query)
    return path.read_text()


def test_check_exits_nonzero_on_stale_members(tmp_path, capsys):
    # Arrange
    path = _write(tmp_path)
    # Act
    code = _check(path)
    # Assert
    assert code == 1


def test_check_reports_a_floor_older_than_pypi(tmp_path, capsys):
    # Arrange
    path = _write(tmp_path)
    # Act
    _check(path)
    err = capsys.readouterr().err
    # Assert
    assert '"scitex-io>=0.4.3": floor older than PyPI latest 0.7.0' in err


def test_check_reports_an_exact_pin(tmp_path, capsys):
    # Arrange
    path = _write(tmp_path)
    # Act
    _check(path)
    err = capsys.readouterr().err
    # Assert
    assert "\"figrecipe==0.29.9\": needs a '>=' floor" in err


def test_write_raises_a_floor_and_keeps_its_comment(tmp_path):
    # Arrange
    path = _write(tmp_path)
    # Act
    text = _write_floors(path)
    # Assert
    assert '"scitex-io>=0.7.0",  # comment kept' in text


def test_write_turns_an_exact_pin_into_a_current_floor(tmp_path):
    # Arrange
    path = _write(tmp_path)
    # Act
    text = _write_floors(path)
    # Assert
    assert '"figrecipe>=0.45.1"' in text


def test_write_preserves_extras(tmp_path):
    # Arrange
    path = _write(tmp_path)
    # Act
    text = _write_floors(path)
    # Assert
    assert '"scitex-dev[mcp]>=0.66.1"' in text


def test_write_leaves_third_party_requirements_alone(tmp_path):
    # Arrange
    path = _write(tmp_path)
    # Act
    text = _write_floors(path)
    # Assert
    assert '"numpy",' in text


def test_check_passes_after_write(tmp_path):
    # Arrange
    path = _write(tmp_path)
    sync.main(["--write", "--pyproject", str(path)], query=_query)
    # Act
    code = sync.main(["--check", "--pyproject", str(path)], query=_query)
    # Assert
    assert code == 0


def test_check_refuses_when_pypi_is_unreachable(tmp_path):
    # Arrange: a gate that passes on a network error is no gate.
    path = _write(tmp_path, '[project]\ndependencies = ["scitex-io>=0.7.0"]\n')
    # Act
    code = sync.main(["--check", "--pyproject", str(path)], query=lambda name: None)
    # Assert
    assert code == 1


def test_write_never_lowers_a_floor_ahead_of_pypi(tmp_path):
    # Arrange: a member tagged moments ago may not be on the index yet.
    path = _write(tmp_path, '[project]\ndependencies = ["scitex-io>=0.8.0"]\n')
    # Act
    sync.main(["--write", "--pyproject", str(path)], query=_query)
    # Assert
    assert '"scitex-io>=0.8.0"' in path.read_text()


def test_repository_pyproject_members_are_all_detected():
    # Arrange: every member the floor-policy test recognises must also be
    # seen by the release gate, or the gate could skip a stale member.
    text = sync.PYPROJECT.read_text()
    # Act
    names = {m["name"] for m in sync.find_members(text)}
    # Assert
    assert {"scitex-clew", "scitex-io", "scitex-writer", "figrecipe"} <= names


# EOF
