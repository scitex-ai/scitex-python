#!/usr/bin/env python3
# Timestamp: 2026-03-12
# File: tests/scitex/dev/test__versions.py

"""Tests for scitex._dev._versions module.

Covers:
- _determine_status() for all status outcomes
- get_mismatches() filtering of non-ok packages
- list_versions() return structure
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scitex._dev._versions import (
    _determine_status,
    _normalize_version,
    _pep440_equal,
    get_mismatches,
    list_versions,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_info(
    toml: str | None = None,
    installed: str | None = None,
    tag: str | None = None,
    pypi: str | None = None,
    dirty: bool = False,
    ahead: int = 0,
    behind: int = 0,
) -> dict:
    """Build a version-info dict as list_versions produces per-package."""
    return {
        "local": {"pyproject_toml": toml, "installed": installed},
        "git": {
            "latest_tag": tag,
            "dirty": dirty,
            "ahead": ahead,
            "behind": behind,
        },
        "remote": {"pypi": pypi},
    }


# ---------------------------------------------------------------------------
# Tests for _normalize_version
# ---------------------------------------------------------------------------


class TestNormalizeVersion:
    """Tests for _normalize_version helper."""

    def test_strips_v_prefix(self):
        assert _normalize_version("v1.2.3") == "1.2.3"

    def test_no_prefix_unchanged(self):
        assert _normalize_version("1.2.3") == "1.2.3"

    def test_none_returns_none(self):
        assert _normalize_version(None) is None


# ---------------------------------------------------------------------------
# Tests for _pep440_equal
# ---------------------------------------------------------------------------


class TestPep440Equal:
    """Tests for PEP 440 version comparison."""

    def test_identical_versions_equal(self):
        assert _pep440_equal("1.0.0", "1.0.0") is True

    def test_v_prefix_normalized(self):
        assert _pep440_equal("v1.0.0", "1.0.0") is True

    def test_different_versions_not_equal(self):
        assert _pep440_equal("1.0.0", "2.0.0") is False

    def test_none_vs_none_equal(self):
        assert _pep440_equal(None, None) is True

    def test_none_vs_version_not_equal(self):
        assert _pep440_equal(None, "1.0.0") is False


# ---------------------------------------------------------------------------
# Tests for _determine_status
# ---------------------------------------------------------------------------


class TestDetermineStatus:
    """Unit tests for _determine_status — the core classification logic."""

    def test_ok_when_all_consistent(self):
        """Returns 'ok' when toml, installed, tag, and pypi all agree."""
        info = _make_info(toml="1.0.0", installed="1.0.0", tag="v1.0.0", pypi="1.0.0")
        status, issues = _determine_status(info)
        assert status == "ok"
        assert issues == []

    def test_mismatch_when_installed_differs_from_toml(self):
        """Returns 'mismatch' when installed version differs from toml."""
        info = _make_info(toml="2.0.0", installed="1.0.0")
        status, issues = _determine_status(info)
        assert status == "mismatch"
        assert any("installed" in i for i in issues)

    def test_mismatch_when_git_dirty(self):
        """Returns 'mismatch' with 'uncommitted changes' issue when dirty."""
        info = _make_info(toml="1.0.0", installed="1.0.0", dirty=True)
        status, issues = _determine_status(info)
        assert status == "mismatch"
        assert any("uncommitted" in i for i in issues)

    def test_mismatch_when_ahead_of_remote(self):
        """Returns 'mismatch' with ahead-of-remote issue."""
        info = _make_info(toml="1.0.0", installed="1.0.0", ahead=3)
        status, issues = _determine_status(info)
        assert status == "mismatch"
        assert any("ahead" in i for i in issues)

    def test_mismatch_when_behind_remote(self):
        """Returns 'mismatch' with behind-remote issue."""
        info = _make_info(toml="1.0.0", installed="1.0.0", behind=2)
        status, issues = _determine_status(info)
        assert status == "mismatch"
        assert any("behind" in i for i in issues)

    def test_unreleased_when_local_ahead_of_pypi(self):
        """Returns 'unreleased' when local version is greater than PyPI version."""
        info = _make_info(toml="2.0.0", installed="2.0.0", pypi="1.9.0")
        status, issues = _determine_status(info)
        assert status == "unreleased"
        assert any("ready to release" in i for i in issues)

    def test_outdated_when_local_behind_pypi(self):
        """Returns 'outdated' when local version is less than PyPI version."""
        info = _make_info(toml="1.0.0", installed="1.0.0", pypi="2.0.0")
        status, issues = _determine_status(info)
        assert status == "outdated"
        assert any("outdated" in i for i in issues)

    def test_unavailable_when_no_toml(self):
        """Returns 'unavailable' when toml version is absent."""
        info = _make_info(toml=None, installed=None)
        status, issues = _determine_status(info)
        assert status == "unavailable"

    def test_mismatch_when_toml_differs_from_tag(self):
        """Returns 'mismatch' when toml version doesn't match git tag."""
        info = _make_info(toml="2.0.0", installed="2.0.0", tag="v1.9.0")
        status, issues = _determine_status(info)
        assert status in ("mismatch", "unreleased", "outdated")
        assert any("git tag" in i for i in issues)


# ---------------------------------------------------------------------------
# Tests for get_mismatches
# ---------------------------------------------------------------------------


class TestGetMismatches:
    """Tests for get_mismatches — filters list_versions to non-ok packages."""

    def _make_versions(self, statuses: dict[str, str]) -> dict:
        """Build a fake list_versions result from a {pkg: status} mapping."""
        return {
            pkg: {"status": status, "issues": [], "local": {}, "git": {}, "remote": {}}
            for pkg, status in statuses.items()
        }

    def test_excludes_ok_packages(self):
        """Packages with status='ok' must not appear in mismatches."""
        fake_versions = self._make_versions({"scitex": "ok", "figrecipe": "ok"})
        with patch("scitex._dev._versions.list_versions", return_value=fake_versions):
            result = get_mismatches()
        assert result == {}

    def test_excludes_unavailable_packages(self):
        """Packages with status='unavailable' are also excluded."""
        fake_versions = self._make_versions({"missing-pkg": "unavailable"})
        with patch("scitex._dev._versions.list_versions", return_value=fake_versions):
            result = get_mismatches()
        assert result == {}

    def test_includes_mismatch_packages(self):
        """Packages with status='mismatch' appear in result."""
        fake_versions = self._make_versions({"scitex": "mismatch"})
        with patch("scitex._dev._versions.list_versions", return_value=fake_versions):
            result = get_mismatches()
        assert "scitex" in result

    def test_includes_unreleased_packages(self):
        """Packages with status='unreleased' appear in result."""
        fake_versions = self._make_versions({"figrecipe": "unreleased"})
        with patch("scitex._dev._versions.list_versions", return_value=fake_versions):
            result = get_mismatches()
        assert "figrecipe" in result

    def test_includes_outdated_packages(self):
        """Packages with status='outdated' appear in result."""
        fake_versions = self._make_versions({"scitex-io": "outdated"})
        with patch("scitex._dev._versions.list_versions", return_value=fake_versions):
            result = get_mismatches()
        assert "scitex-io" in result

    def test_mixed_statuses_filtered_correctly(self):
        """Only non-ok, non-unavailable packages appear in mismatches."""
        fake_versions = self._make_versions(
            {
                "scitex": "ok",
                "figrecipe": "mismatch",
                "scitex-io": "unavailable",
                "scitex-stats": "unreleased",
            }
        )
        with patch("scitex._dev._versions.list_versions", return_value=fake_versions):
            result = get_mismatches()

        assert "scitex" not in result
        assert "scitex-io" not in result
        assert "figrecipe" in result
        assert "scitex-stats" in result

    def test_passes_packages_arg_to_list_versions(self):
        """get_mismatches forwards the packages argument to list_versions."""
        with patch("scitex._dev._versions.list_versions", return_value={}) as mock_lv:
            get_mismatches(packages=["scitex"])
        mock_lv.assert_called_once_with(["scitex"])


# ---------------------------------------------------------------------------
# Tests for list_versions structure
# ---------------------------------------------------------------------------


class TestListVersions:
    """Tests for list_versions() return structure."""

    def test_unknown_package_flagged(self):
        """Package not in ECOSYSTEM gets status='unknown'."""
        result = list_versions(packages=["nonexistent-pkg-xyz"])
        assert "nonexistent-pkg-xyz" in result
        assert result["nonexistent-pkg-xyz"]["status"] == "unknown"

    def test_returns_dict_keyed_by_package_name(self):
        """Return value is a dict with package names as keys."""
        with (
            patch("scitex._dev._versions.get_version_from_toml", return_value="1.0.0"),
            patch("scitex._dev._versions.get_version_installed", return_value="1.0.0"),
            patch("scitex._dev._versions.get_git_latest_tag", return_value="v1.0.0"),
            patch("scitex._dev._versions.get_git_branch", return_value="main"),
            patch(
                "scitex._dev._versions.get_git_status",
                return_value={
                    "dirty": False,
                    "ahead": 0,
                    "behind": 0,
                    "short_hash": "abc1234",
                },
            ),
            patch("scitex._dev._versions.get_pypi_version", return_value="1.0.0"),
        ):
            result = list_versions(packages=["scitex"])

        assert isinstance(result, dict)
        assert "scitex" in result

    def test_each_entry_has_status_and_issues(self):
        """Every entry returned by list_versions has status and issues keys."""
        with (
            patch("scitex._dev._versions.get_version_from_toml", return_value="1.0.0"),
            patch("scitex._dev._versions.get_version_installed", return_value="1.0.0"),
            patch("scitex._dev._versions.get_git_latest_tag", return_value="v1.0.0"),
            patch("scitex._dev._versions.get_git_branch", return_value="main"),
            patch(
                "scitex._dev._versions.get_git_status",
                return_value={
                    "dirty": False,
                    "ahead": 0,
                    "behind": 0,
                    "short_hash": "abc1234",
                },
            ),
            patch("scitex._dev._versions.get_pypi_version", return_value="1.0.0"),
        ):
            result = list_versions(packages=["scitex"])

        entry = result["scitex"]
        assert "status" in entry
        assert "issues" in entry

    def test_each_entry_has_local_git_remote_sections(self):
        """Every entry has local, git, and remote sub-dicts."""
        with (
            patch("scitex._dev._versions.get_version_from_toml", return_value=None),
            patch("scitex._dev._versions.get_version_installed", return_value=None),
            patch("scitex._dev._versions.get_git_latest_tag", return_value=None),
            patch("scitex._dev._versions.get_git_branch", return_value=None),
            patch("scitex._dev._versions.get_git_status", return_value=None),
            patch("scitex._dev._versions.get_pypi_version", return_value=None),
        ):
            result = list_versions(packages=["scitex"])

        entry = result["scitex"]
        assert "local" in entry
        assert "git" in entry
        assert "remote" in entry


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
