#!/usr/bin/env python3
# Timestamp: "2026-02-22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/tests/scitex/notebook/test__parse.py

"""Tests for scitex.notebook._parse module.

Covers parse_notebook(), get_code_cells(), and get_notebook_name().
All file operations use tmp_path; no external dependencies required.
"""

import json

import pytest

from scitex.notebook._parse import get_code_cells, get_notebook_name, parse_notebook

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_NB = {
    "cells": [
        {
            "cell_type": "markdown",
            "source": ["# Title"],
            "metadata": {},
            "id": "md1",
        },
        {
            "cell_type": "code",
            "source": ["x = 1\n", "y = 2"],
            "metadata": {},
            "id": "code1",
            "outputs": [],
        },
        {
            "cell_type": "code",
            "source": ["print(x + y)"],
            "metadata": {},
            "id": "code2",
            "outputs": [],
        },
    ],
    "metadata": {"kernelspec": {"name": "python3"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}


@pytest.fixture
def notebook_path(tmp_path):
    """Write a minimal .ipynb fixture and return its path."""
    nb_file = tmp_path / "test_notebook.ipynb"
    nb_file.write_text(json.dumps(MINIMAL_NB), encoding="utf-8")
    return nb_file


# ---------------------------------------------------------------------------
# parse_notebook() tests
# ---------------------------------------------------------------------------


def test_parse_notebook_returns_all_cells(notebook_path):
    """parse_notebook should return all cells including markdown ones."""
    cells = parse_notebook(notebook_path)
    assert len(cells) == 3


def test_parse_notebook_cell_types(notebook_path):
    """parse_notebook should preserve cell_type for each cell."""
    cells = parse_notebook(notebook_path)
    types = [c["cell_type"] for c in cells]
    assert types == ["markdown", "code", "code"]


def test_parse_notebook_cell_index(notebook_path):
    """parse_notebook should assign sequential index starting at 0."""
    cells = parse_notebook(notebook_path)
    indices = [c["index"] for c in cells]
    assert indices == [0, 1, 2]


def test_parse_notebook_source_joined(notebook_path):
    """parse_notebook should join list-format source lines into a single string."""
    cells = parse_notebook(notebook_path)
    # cell at index 1 has source ["x = 1\n", "y = 2"]
    code_cell = cells[1]
    assert code_cell["source"] == "x = 1\ny = 2"


def test_parse_notebook_cell_id_preserved(notebook_path):
    """parse_notebook should preserve cell id from the notebook JSON."""
    cells = parse_notebook(notebook_path)
    assert cells[0]["cell_id"] == "md1"
    assert cells[1]["cell_id"] == "code1"
    assert cells[2]["cell_id"] == "code2"


def test_parse_notebook_missing_file_raises(tmp_path):
    """parse_notebook should raise FileNotFoundError for a missing file."""
    missing = tmp_path / "does_not_exist.ipynb"
    with pytest.raises(FileNotFoundError):
        parse_notebook(missing)


def test_parse_notebook_non_ipynb_raises(tmp_path):
    """parse_notebook should raise ValueError for a non-.ipynb path."""
    py_file = tmp_path / "script.py"
    py_file.write_text("x = 1", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_notebook(py_file)


def test_parse_notebook_string_path(notebook_path):
    """parse_notebook should accept a plain string path, not only Path objects."""
    cells = parse_notebook(str(notebook_path))
    assert len(cells) == 3


def test_parse_notebook_source_string_cell(tmp_path):
    """parse_notebook should handle cells where source is already a plain string."""
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "source": "result = 42",
                "metadata": {},
                "id": "c0",
                "outputs": [],
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_file = tmp_path / "str_source.ipynb"
    nb_file.write_text(json.dumps(nb), encoding="utf-8")
    cells = parse_notebook(nb_file)
    assert cells[0]["source"] == "result = 42"


def test_parse_notebook_empty_notebook(tmp_path):
    """parse_notebook should return an empty list for a notebook with no cells."""
    nb = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
    nb_file = tmp_path / "empty.ipynb"
    nb_file.write_text(json.dumps(nb), encoding="utf-8")
    cells = parse_notebook(nb_file)
    assert cells == []


def test_parse_notebook_missing_id_uses_fallback(tmp_path):
    """parse_notebook should generate a fallback cell_id when 'id' key is absent."""
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["pass"],
                "metadata": {},
                "outputs": [],
                # no "id" key
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_file = tmp_path / "no_id.ipynb"
    nb_file.write_text(json.dumps(nb), encoding="utf-8")
    cells = parse_notebook(nb_file)
    assert cells[0]["cell_id"] == "cell_0"


# ---------------------------------------------------------------------------
# get_code_cells() tests
# ---------------------------------------------------------------------------


def test_get_code_cells_returns_only_code(notebook_path):
    """get_code_cells should return only cells with cell_type == 'code'."""
    cells = get_code_cells(notebook_path)
    assert len(cells) == 2
    for cell in cells:
        assert cell["cell_type"] == "code"


def test_get_code_cells_excludes_markdown(notebook_path):
    """get_code_cells should not include markdown cells."""
    cells = get_code_cells(notebook_path)
    cell_ids = [c["cell_id"] for c in cells]
    assert "md1" not in cell_ids


def test_get_code_cells_source_correct(notebook_path):
    """get_code_cells should preserve joined source for code cells."""
    cells = get_code_cells(notebook_path)
    sources = [c["source"] for c in cells]
    assert "x = 1\ny = 2" in sources
    assert "print(x + y)" in sources


def test_get_code_cells_empty_notebook(tmp_path):
    """get_code_cells should return empty list for a notebook with no code cells."""
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Only markdown"],
                "metadata": {},
                "id": "md1",
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_file = tmp_path / "markdown_only.ipynb"
    nb_file.write_text(json.dumps(nb), encoding="utf-8")
    cells = get_code_cells(nb_file)
    assert cells == []


# ---------------------------------------------------------------------------
# get_notebook_name() tests
# ---------------------------------------------------------------------------


def test_get_notebook_name_returns_stem(notebook_path):
    """get_notebook_name should return filename stem without extension."""
    name = get_notebook_name(notebook_path)
    assert name == "test_notebook"


def test_get_notebook_name_string_input(notebook_path):
    """get_notebook_name should accept string path, not only Path."""
    name = get_notebook_name(str(notebook_path))
    assert name == "test_notebook"


def test_get_notebook_name_complex_name(tmp_path):
    """get_notebook_name should handle names with underscores and numbers."""
    nb_file = tmp_path / "my_experiment_01.ipynb"
    nb_file.write_text("{}", encoding="utf-8")
    assert get_notebook_name(nb_file) == "my_experiment_01"


# EOF
