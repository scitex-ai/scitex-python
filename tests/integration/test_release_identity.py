"""Current documented source selection keeps private checkouts out of releases."""

import copy
import importlib.util
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10; tomli is a declared dependency.
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "_current_release_selection", ROOT / ".github/ci/release-identity.py"
)
RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELEASE)


def _current_source():
    commit = RELEASE.git_read(["rev-parse", "HEAD"], ROOT).decode().strip()
    entries = RELEASE.git_tree(commit, ROOT)
    project = tomllib.loads(
        RELEASE.git_read(["show", commit + ":pyproject.toml"], ROOT).decode()
    )
    ignore = RELEASE.git_read(["show", commit + ":.gitignore"], ROOT)
    return entries, project, ignore


def test_current_source_selects_the_canonical_dictionary_and_documentation():
    # Arrange
    entries, project, ignore = _current_source()
    # Act
    wheel, selected = RELEASE.selected_paths(entries, project, ignore)
    # Assert
    assert wheel["scitex/_cli_audit_dict.yaml"] == "src/scitex/_cli_audit_dict.yaml"
    assert "pyproject.toml" in selected
    assert {p for p in entries if p.startswith("docs/sphinx/")} <= selected


def test_private_worktree_payload_is_excluded_by_the_reviewed_source_policy():
    # Arrange
    entries, project, ignore = _current_source()
    private = ".worktrees/private/source.py"
    entries[private] = entries["src/scitex/__init__.py"]
    # Act
    wheel, selected = RELEASE.selected_paths(entries, project, ignore)
    # Assert
    assert private not in selected
    assert private not in wheel.values()


def test_other_ignore_changes_remain_refused():
    # Arrange
    entries, project, ignore = _current_source()
    # Act
    # Assert
    with pytest.raises(ValueError, match="reviewed umbrella ignore selection changed"):
        RELEASE.selected_paths(entries, project, ignore + b"\n*.py\n")


def test_removing_private_worktree_protection_remains_refused():
    # Arrange
    entries, project, ignore = _current_source()
    exclusion = (
        b"# Local checkouts are runtime development state, not repository submodules.\n"
        b"/.worktrees/\n"
    )
    assert exclusion in ignore
    # Act
    # Assert
    with pytest.raises(ValueError, match="reviewed umbrella ignore selection changed"):
        RELEASE.selected_paths(entries, project, ignore.replace(exclusion, b""))


def test_unreviewed_forced_package_mapping_remains_refused():
    # Arrange
    entries, project, ignore = _current_source()
    project = copy.deepcopy(project)
    project["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"] = {
        "foreign": "scitex/foreign"
    }
    # Act
    # Assert
    with pytest.raises(ValueError, match="reviewed umbrella Hatch mapping changed"):
        RELEASE.selected_paths(entries, project, ignore)
