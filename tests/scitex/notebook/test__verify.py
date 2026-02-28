#!/usr/bin/env python3
# Timestamp: "2026-02-22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/tests/scitex/notebook/test__verify.py

"""Tests for scitex.notebook._verify module.

Covers check_notebook() — static analysis of notebook cells for untracked IO.
No clew DB or network access is required; all tests use tmp_path fixtures.
"""

import json

import pytest

from scitex.notebook._verify import check_notebook

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_notebook(cells, tmp_path, name="nb.ipynb"):
    """Write a notebook JSON to tmp_path and return its Path."""
    nb = {
        "cells": cells,
        "metadata": {"kernelspec": {"name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_file = tmp_path / name
    nb_file.write_text(json.dumps(nb), encoding="utf-8")
    return nb_file


def _code_cell(source, cell_id):
    """Helper to build a code cell dict."""
    return {
        "cell_type": "code",
        "source": source,
        "metadata": {},
        "id": cell_id,
        "outputs": [],
    }


def _markdown_cell(source, cell_id):
    """Helper to build a markdown cell dict."""
    return {
        "cell_type": "markdown",
        "source": source,
        "metadata": {},
        "id": cell_id,
    }


# ---------------------------------------------------------------------------
# check_notebook() tests
# ---------------------------------------------------------------------------


def test_check_notebook_detects_untracked_load(tmp_path):
    """Cell with scitex.io.load() but no @stx.session should be flagged."""
    nb_path = _make_notebook(
        [
            _code_cell(
                "data = scitex.io.load('input.csv')",
                "c1",
            )
        ],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert len(issues) == 1
    assert issues[0]["has_load"] is True
    assert issues[0]["has_session"] is False


def test_check_notebook_detects_stx_alias_load(tmp_path):
    """Cell with stx.io.load() (alias) but no session decorator should be flagged."""
    nb_path = _make_notebook(
        [_code_cell("result = stx.io.load('data.pkl')", "c1")],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert len(issues) == 1
    assert issues[0]["has_load"] is True


def test_check_notebook_detects_untracked_save(tmp_path):
    """Cell with scitex.io.save() but no @stx.session should be flagged."""
    nb_path = _make_notebook(
        [_code_cell("scitex.io.save(result, 'output.pkl')", "c1")],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert len(issues) == 1
    assert issues[0]["has_save"] is True
    assert issues[0]["has_session"] is False


def test_check_notebook_detects_stx_alias_save(tmp_path):
    """Cell with stx.io.save() (alias) but no session decorator should be flagged."""
    nb_path = _make_notebook(
        [_code_cell("stx.io.save(df, 'results.csv')", "c1")],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert len(issues) == 1
    assert issues[0]["has_save"] is True


def test_check_notebook_tracked_cell_not_flagged(tmp_path):
    """Cell with IO and @stx.session should NOT appear in issues."""
    source = (
        "@stx.session\n"
        "def run():\n"
        "    data = stx.io.load('input.csv')\n"
        "    stx.io.save(data, 'out.csv')\n"
    )
    nb_path = _make_notebook([_code_cell(source, "c1")], tmp_path)
    issues = check_notebook(nb_path)
    assert issues == []


def test_check_notebook_scitex_session_decorator_accepted(tmp_path):
    """Cell with @scitex.session (long form) should NOT be flagged."""
    source = "@scitex.session\ndef run():\n    data = scitex.io.load('f.pkl')\n"
    nb_path = _make_notebook([_code_cell(source, "c1")], tmp_path)
    issues = check_notebook(nb_path)
    assert issues == []


def test_check_notebook_clean_notebook_returns_empty(tmp_path):
    """Notebook with no IO calls should return an empty list."""
    nb_path = _make_notebook(
        [
            _code_cell("x = 1 + 2", "c1"),
            _code_cell("print(x)", "c2"),
        ],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert issues == []


def test_check_notebook_markdown_cells_ignored(tmp_path):
    """Markdown cells mentioning IO functions should not be flagged."""
    nb_path = _make_notebook(
        [
            _markdown_cell("Use `stx.io.load('file')` to load data.", "md1"),
            _code_cell("x = 42", "c1"),
        ],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert issues == []


def test_check_notebook_cell_index_reported(tmp_path):
    """Issues should report the correct cell index."""
    nb_path = _make_notebook(
        [
            _code_cell("x = 1", "c0"),
            _code_cell("data = stx.io.load('f.csv')", "c1"),
        ],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert len(issues) == 1
    # Second cell (index=1) is the one with untracked IO
    assert issues[0]["index"] == 1


def test_check_notebook_multiple_issues(tmp_path):
    """Multiple cells with untracked IO should all appear in the result."""
    nb_path = _make_notebook(
        [
            _code_cell("stx.io.load('a.csv')", "c0"),
            _code_cell("stx.io.save(x, 'b.csv')", "c1"),
            _code_cell("y = 99", "c2"),
        ],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert len(issues) == 2
    indices = [iss["index"] for iss in issues]
    assert 0 in indices
    assert 1 in indices


def test_check_notebook_issue_dict_has_required_keys(tmp_path):
    """Each issue dict must have index, has_load, has_save, has_session."""
    nb_path = _make_notebook(
        [_code_cell("stx.io.load('f.pkl')", "c0")],
        tmp_path,
    )
    issues = check_notebook(nb_path)
    assert len(issues) == 1
    issue = issues[0]
    for key in ("index", "has_load", "has_save", "has_session"):
        assert key in issue, f"Missing key: {key}"


def test_check_notebook_cell_with_load_and_save_both_flagged(tmp_path):
    """Cell with both load and save but no session should have both flags True."""
    source = "data = stx.io.load('in.csv')\nstx.io.save(data, 'out.csv')"
    nb_path = _make_notebook([_code_cell(source, "c0")], tmp_path)
    issues = check_notebook(nb_path)
    assert len(issues) == 1
    assert issues[0]["has_load"] is True
    assert issues[0]["has_save"] is True


# ---------------------------------------------------------------------------
# verify_notebook() with mock DB tests
# ---------------------------------------------------------------------------


def test_verify_notebook_no_sessions(tmp_path):
    """verify_notebook should return empty list when no matching sessions."""
    from unittest.mock import MagicMock, patch

    nb_path = _make_notebook([_code_cell("x = 1", "c0")], tmp_path)

    mock_db = MagicMock()
    mock_db.list_runs.return_value = []

    with (
        patch("scitex.clew.get_db", return_value=mock_db),
        patch("scitex.clew.verify_run"),
    ):
        from scitex.notebook._verify import verify_notebook

        results = verify_notebook(nb_path)

    assert results == []


def test_verify_notebook_with_verified_session(tmp_path):
    """verify_notebook should report verified sessions."""
    from unittest.mock import MagicMock, patch

    nb_path = _make_notebook([_code_cell("x = 1", "c0")], tmp_path)

    mock_verification = MagicMock()
    mock_verification.status.value = "verified"
    mock_verification.is_verified = True

    runs = [
        {
            "session_id": "s1",
            "started_at": "2026-01-01T00:00:00",
            "script_path": str(nb_path),
            "metadata": json.dumps({"notebook_path": str(nb_path.resolve())}),
        },
    ]

    mock_db = MagicMock()
    mock_db.list_runs.return_value = runs

    with (
        patch("scitex.clew.get_db", return_value=mock_db),
        patch(
            "scitex.clew.verify_run",
            return_value=mock_verification,
        ),
    ):
        from scitex.notebook._verify import verify_notebook

        results = verify_notebook(nb_path)

    assert len(results) == 1
    assert results[0]["is_verified"] is True
    assert results[0]["session_id"] == "s1"


def test_verify_notebook_with_failed_session(tmp_path):
    """verify_notebook should report failed sessions."""
    from unittest.mock import MagicMock, patch

    nb_path = _make_notebook([_code_cell("x = 1", "c0")], tmp_path)

    mock_verification = MagicMock()
    mock_verification.status.value = "mismatch"
    mock_verification.is_verified = False

    runs = [
        {
            "session_id": "s1",
            "started_at": "2026-01-01T00:00:00",
            "metadata": json.dumps({"notebook_path": str(nb_path.resolve())}),
        },
    ]

    mock_db = MagicMock()
    mock_db.list_runs.return_value = runs

    with (
        patch("scitex.clew.get_db", return_value=mock_db),
        patch(
            "scitex.clew.verify_run",
            return_value=mock_verification,
        ),
    ):
        from scitex.notebook._verify import verify_notebook

        results = verify_notebook(nb_path)

    assert len(results) == 1
    assert results[0]["is_verified"] is False


def test_verify_notebook_handles_exception(tmp_path):
    """verify_notebook should catch verification errors gracefully."""
    from unittest.mock import MagicMock, patch

    nb_path = _make_notebook([_code_cell("x = 1", "c0")], tmp_path)

    runs = [
        {
            "session_id": "s1",
            "started_at": "2026-01-01T00:00:00",
            "metadata": json.dumps({"notebook_path": str(nb_path.resolve())}),
        },
    ]

    mock_db = MagicMock()
    mock_db.list_runs.return_value = runs

    with (
        patch("scitex.clew.get_db", return_value=mock_db),
        patch(
            "scitex.clew.verify_run",
            side_effect=RuntimeError("DB error"),
        ),
    ):
        from scitex.notebook._verify import verify_notebook

        results = verify_notebook(nb_path)

    assert len(results) == 1
    assert results[0]["status"] == "error"
    assert results[0]["is_verified"] is False


# ---------------------------------------------------------------------------
# _get_runs_for_notebook() tests
# ---------------------------------------------------------------------------


def test_get_runs_for_notebook_matches_metadata(tmp_path):
    """_get_runs_for_notebook should match runs via metadata.notebook_path."""
    from unittest.mock import MagicMock

    from scitex.notebook._verify import _get_runs_for_notebook

    nb_path = tmp_path / "nb.ipynb"
    nb_path.write_text("{}", encoding="utf-8")

    runs = [
        {
            "session_id": "s1",
            "started_at": "2026-01-01T00:00:00",
            "metadata": json.dumps({"notebook_path": str(nb_path.resolve())}),
        },
        {
            "session_id": "s2",
            "started_at": "2026-01-02T00:00:00",
            "metadata": json.dumps({"notebook_path": "/other/nb.ipynb"}),
        },
    ]

    mock_db = MagicMock()
    mock_db.list_runs.return_value = runs

    result = _get_runs_for_notebook(mock_db, str(nb_path.resolve()))
    assert len(result) == 1
    assert result[0]["session_id"] == "s1"


def test_get_runs_for_notebook_empty_metadata_skipped():
    """Runs with no metadata should be skipped (unless script_path matches)."""
    from unittest.mock import MagicMock

    from scitex.notebook._verify import _get_runs_for_notebook

    runs = [
        {
            "session_id": "s1",
            "started_at": "2026-01-01T00:00:00",
            "script_path": "/some/script.py",
        },
    ]

    mock_db = MagicMock()
    mock_db.list_runs.return_value = runs

    result = _get_runs_for_notebook(mock_db, "/target/nb.ipynb")
    assert len(result) == 0


# EOF
