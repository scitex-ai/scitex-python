#!/usr/bin/env python3
# Timestamp: 2026-03-12
# File: tests/scitex/dev/test__fix.py

"""Tests for scitex._dev._fix module.

Covers fix_mismatches() and _find_local_mismatches() behavior,
focusing on the safety model (dry_run by default) and structure
of the returned dict.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scitex._dev._fix import _find_local_mismatches, fix_mismatches

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_mismatch_info(
    toml: str | None = "1.0.0",
    installed: str | None = "0.9.0",
    status: str = "mismatch",
    issues: list[str] | None = None,
) -> dict:
    """Build a typical mismatches dict entry for a single package."""
    return {
        "status": status,
        "issues": issues or [f"pyproject.toml ({toml}) != installed ({installed})"],
        "local": {"pyproject_toml": toml, "installed": installed},
        "git": {},
        "remote": {},
    }


# ---------------------------------------------------------------------------
# Tests for _find_local_mismatches
# ---------------------------------------------------------------------------


class TestFindLocalMismatches:
    """Unit tests for _find_local_mismatches."""

    def test_returns_package_when_toml_installed_differ(self):
        """Package included when toml version differs from installed."""
        mismatches = {
            "scitex": _make_mismatch_info(toml="2.0.0", installed="1.9.0"),
        }
        result = _find_local_mismatches(mismatches)
        assert "scitex" in result

    def test_returns_package_when_installed_missing(self):
        """Package included when installed is None (not installed at all)."""
        mismatches = {
            "figrecipe": _make_mismatch_info(toml="1.0.0", installed=None),
        }
        result = _find_local_mismatches(mismatches)
        assert "figrecipe" in result

    def test_excludes_package_when_versions_match(self):
        """Package excluded when toml and installed are identical."""
        mismatches = {
            "scitex": _make_mismatch_info(toml="1.0.0", installed="1.0.0"),
        }
        result = _find_local_mismatches(mismatches)
        assert "scitex" not in result

    def test_excludes_package_when_toml_missing(self):
        """Package excluded when toml version is None (no pyproject.toml)."""
        mismatches = {
            "unknown-pkg": _make_mismatch_info(toml=None, installed="1.0.0"),
        }
        result = _find_local_mismatches(mismatches)
        assert "unknown-pkg" not in result

    def test_returns_empty_list_for_empty_input(self):
        """Empty mismatches dict yields empty list."""
        assert _find_local_mismatches({}) == []

    def test_handles_multiple_packages(self):
        """Correctly separates fixable from non-fixable packages."""
        mismatches = {
            "pkg-needs-fix": _make_mismatch_info(toml="2.0.0", installed="1.0.0"),
            "pkg-ok-locally": _make_mismatch_info(toml="1.0.0", installed="1.0.0"),
            "pkg-not-installed": _make_mismatch_info(toml="1.0.0", installed=None),
        }
        result = _find_local_mismatches(mismatches)
        assert "pkg-needs-fix" in result
        assert "pkg-not-installed" in result
        assert "pkg-ok-locally" not in result


# ---------------------------------------------------------------------------
# Tests for fix_mismatches
# ---------------------------------------------------------------------------


class TestFixMismatchesStructure:
    """Tests that fix_mismatches always returns the expected top-level keys."""

    def _call_with_mock_mismatches(self, mismatches: dict) -> dict:
        """Helper: patch get_mismatches and both sync functions, call fix_mismatches."""
        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value=mismatches),
            patch("scitex._dev._fix.sync_local", return_value={}),
            patch("scitex._dev._fix.sync_all", return_value={}),
        ):
            return fix_mismatches(config=fake_config)

    def test_returned_dict_has_required_keys(self):
        """fix_mismatches always returns detected, local_fixes, remote_fixes, summary."""
        mismatches = {"scitex": _make_mismatch_info()}
        result = self._call_with_mock_mismatches(mismatches)

        assert "detected" in result
        assert "local_fixes" in result
        assert "remote_fixes" in result
        assert "summary" in result

    def test_summary_has_correct_sub_keys(self):
        """summary contains detected, local_fixed, remote_fixed counts."""
        mismatches = {"scitex": _make_mismatch_info()}
        result = self._call_with_mock_mismatches(mismatches)

        summary = result["summary"]
        assert "detected" in summary
        assert "local_fixed" in summary
        assert "remote_fixed" in summary

    def test_detected_reflects_get_mismatches_output(self):
        """detected key mirrors the packages returned by get_mismatches."""
        mismatches = {
            "scitex": _make_mismatch_info(toml="2.0.0", installed="1.0.0"),
            "figrecipe": _make_mismatch_info(
                toml="0.5.0", installed=None, status="unavailable"
            ),
        }
        result = self._call_with_mock_mismatches(mismatches)

        assert "scitex" in result["detected"]
        assert "figrecipe" in result["detected"]
        assert result["summary"]["detected"] == 2

    def test_detected_entry_contains_status_and_issues(self):
        """Each detected entry has status and issues fields."""
        mismatches = {"scitex": _make_mismatch_info()}
        result = self._call_with_mock_mismatches(mismatches)

        entry = result["detected"]["scitex"]
        assert "status" in entry
        assert "issues" in entry

    def test_dry_run_does_not_increment_fixed_counts(self):
        """With confirm=False (default), local_fixed and remote_fixed stay at 0."""
        mismatches = {"scitex": _make_mismatch_info()}
        result = self._call_with_mock_mismatches(mismatches)

        assert result["summary"]["local_fixed"] == 0
        assert result["summary"]["remote_fixed"] == 0


class TestFixMismatchesNoMismatches:
    """Tests when get_mismatches returns nothing (all packages ok)."""

    def test_returns_empty_detected_when_no_mismatches(self):
        """fix_mismatches with no mismatches returns empty detected dict."""
        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value={}),
            patch("scitex._dev._fix.sync_local", return_value={}) as mock_sync_local,
            patch("scitex._dev._fix.sync_all", return_value={}) as mock_sync_all,
        ):
            result = fix_mismatches(config=fake_config)

        assert result["detected"] == {}
        assert result["summary"]["detected"] == 0

    def test_sync_not_called_when_no_mismatches(self):
        """sync_local and sync_all are never invoked when there are no mismatches."""
        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value={}),
            patch("scitex._dev._fix.sync_local") as mock_sync_local,
            patch("scitex._dev._fix.sync_all") as mock_sync_all,
        ):
            fix_mismatches(config=fake_config)

        mock_sync_local.assert_not_called()
        mock_sync_all.assert_not_called()


class TestFixMismatchesConfirm:
    """Tests confirm=True path increments counters from sync results."""

    def test_local_fixed_counted_on_confirm(self):
        """local_fixed increments for each sync_local result with status=ok."""
        mismatches = {
            "scitex": _make_mismatch_info(toml="2.0.0", installed="1.0.0"),
        }
        sync_local_result = {"scitex": {"status": "ok"}}

        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value=mismatches),
            patch("scitex._dev._fix.sync_local", return_value=sync_local_result),
            patch("scitex._dev._fix.sync_all", return_value={}),
        ):
            result = fix_mismatches(confirm=True, config=fake_config)

        assert result["summary"]["local_fixed"] == 1

    def test_remote_fixed_counted_on_confirm(self):
        """remote_fixed increments for each sync_all result with status=ok."""
        mismatches = {
            "scitex": _make_mismatch_info(),
        }
        sync_all_result = {
            "host1": {"scitex": {"status": "ok"}},
        }

        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value=mismatches),
            patch("scitex._dev._fix.sync_local", return_value={}),
            patch("scitex._dev._fix.sync_all", return_value=sync_all_result),
        ):
            result = fix_mismatches(confirm=True, config=fake_config)

        assert result["summary"]["remote_fixed"] == 1

    def test_partial_failures_not_counted(self):
        """Only sync results with status=ok are counted, not failed ones."""
        mismatches = {
            "pkg-a": _make_mismatch_info(toml="2.0.0", installed="1.0.0"),
            "pkg-b": _make_mismatch_info(toml="3.0.0", installed="2.0.0"),
        }
        sync_local_result = {
            "pkg-a": {"status": "ok"},
            "pkg-b": {"status": "error", "message": "pip failed"},
        }

        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value=mismatches),
            patch("scitex._dev._fix.sync_local", return_value=sync_local_result),
            patch("scitex._dev._fix.sync_all", return_value={}),
        ):
            result = fix_mismatches(confirm=True, config=fake_config)

        assert result["summary"]["local_fixed"] == 1


class TestFixMismatchesFlags:
    """Tests local/remote flag behavior."""

    def test_local_false_skips_sync_local(self):
        """sync_local is not called when local=False."""
        mismatches = {"scitex": _make_mismatch_info(toml="2.0.0", installed="1.0.0")}

        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value=mismatches),
            patch("scitex._dev._fix.sync_local") as mock_sync_local,
            patch("scitex._dev._fix.sync_all", return_value={}),
        ):
            fix_mismatches(local=False, config=fake_config)

        mock_sync_local.assert_not_called()

    def test_remote_false_skips_sync_all(self):
        """sync_all is not called when remote=False."""
        mismatches = {"scitex": _make_mismatch_info()}

        fake_config = MagicMock()
        with (
            patch("scitex._dev._fix.get_mismatches", return_value=mismatches),
            patch("scitex._dev._fix.sync_local", return_value={}),
            patch("scitex._dev._fix.sync_all") as mock_sync_all,
        ):
            fix_mismatches(remote=False, config=fake_config)

        mock_sync_all.assert_not_called()


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
