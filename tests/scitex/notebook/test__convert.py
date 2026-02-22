#!/usr/bin/env python3
# Timestamp: "2026-02-22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/tests/scitex/notebook/test__convert.py

"""Tests for scitex.notebook._convert module.

Covers convert_notebook() in 'cell' order mode.
All file operations use tmp_path; no clew DB access is needed.
"""

import json

import pytest

from scitex.notebook._convert import convert_notebook

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_NB = {
    "cells": [
        {
            "cell_type": "markdown",
            "source": ["# Analysis Notebook"],
            "metadata": {},
            "id": "md1",
        },
        {
            "cell_type": "code",
            "source": ["import numpy as np\n", "x = np.array([1, 2, 3])"],
            "metadata": {},
            "id": "code1",
            "outputs": [],
        },
        {
            "cell_type": "code",
            "source": [
                "%matplotlib inline\n",
                "import matplotlib.pyplot as plt\n",
                "plt.plot(x)",
            ],
            "metadata": {},
            "id": "code2",
            "outputs": [],
        },
        {
            "cell_type": "code",
            "source": ["!pip install scipy\n", "from scipy import stats"],
            "metadata": {},
            "id": "code3",
            "outputs": [],
        },
    ],
    "metadata": {"kernelspec": {"name": "python3"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}


@pytest.fixture
def notebook_path(tmp_path):
    """Write the sample notebook to tmp_path and return its Path."""
    nb_file = tmp_path / "sample_analysis.ipynb"
    nb_file.write_text(json.dumps(SAMPLE_NB), encoding="utf-8")
    return nb_file


# ---------------------------------------------------------------------------
# convert_notebook() — cell order
# ---------------------------------------------------------------------------


def test_convert_notebook_returns_string(notebook_path):
    """convert_notebook should return a Python source string."""
    result = convert_notebook(notebook_path, order="cell")
    assert isinstance(result, str)
    assert len(result) > 0


def test_convert_notebook_contains_shebang(notebook_path):
    """Converted script must contain a Python shebang."""
    result = convert_notebook(notebook_path, order="cell")
    assert "#!/usr/bin/env python3" in result


def test_convert_notebook_contains_import(notebook_path):
    """Converted script must import scitex as stx."""
    result = convert_notebook(notebook_path, order="cell")
    assert "import scitex as stx" in result


def test_convert_notebook_each_code_cell_becomes_function(notebook_path):
    """Each non-empty code cell should produce a function definition."""
    result = convert_notebook(notebook_path, order="cell")
    # SAMPLE_NB has 3 code cells, each with non-magic content
    def_count = result.count("def cell_")
    assert def_count == 3


def test_convert_notebook_session_decorator_per_cell(notebook_path):
    """Every generated function should be decorated with @stx.session."""
    result = convert_notebook(notebook_path, order="cell")
    session_count = result.count("@stx.session")
    assert session_count == 3


def test_convert_notebook_magic_percent_stripped(notebook_path):
    """IPython % magic commands should be stripped from the output."""
    result = convert_notebook(notebook_path, order="cell")
    assert "%matplotlib" not in result


def test_convert_notebook_magic_bang_stripped(notebook_path):
    """IPython ! shell commands should be stripped from the output."""
    result = convert_notebook(notebook_path, order="cell")
    assert "!pip" not in result


def test_convert_notebook_markdown_cells_excluded(notebook_path):
    """Markdown cell content should not appear in the generated script."""
    result = convert_notebook(notebook_path, order="cell")
    assert "# Analysis Notebook" not in result


def test_convert_notebook_code_content_preserved(notebook_path):
    """Code cell content (excluding magics) should appear in the output."""
    result = convert_notebook(notebook_path, order="cell")
    assert "import numpy as np" in result
    assert "x = np.array([1, 2, 3])" in result


def test_convert_notebook_output_file_written(notebook_path, tmp_path):
    """When output path is given, the script should be written to disk."""
    out_file = tmp_path / "output_script.py"
    result = convert_notebook(notebook_path, output=out_file, order="cell")
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert content == result


def test_convert_notebook_output_none_no_file_written(notebook_path, tmp_path):
    """When output is None, no file should be created."""
    # Capture files before
    before = set(tmp_path.iterdir())
    convert_notebook(notebook_path, output=None, order="cell")
    after = set(tmp_path.iterdir())
    # Only the notebook itself should be present; no new .py file
    new_files = after - before
    py_files = [f for f in new_files if f.suffix == ".py"]
    assert py_files == []


def test_convert_notebook_creates_output_parent_dirs(tmp_path, notebook_path):
    """convert_notebook should create missing parent directories for output."""
    out_file = tmp_path / "nested" / "deep" / "script.py"
    convert_notebook(notebook_path, output=out_file, order="cell")
    assert out_file.exists()


def test_convert_notebook_function_calls_present(notebook_path):
    """Each generated function should also be called (function_name() line)."""
    result = convert_notebook(notebook_path, order="cell")
    # The pattern 'cell_XX()' (call) should appear as many times as 'def cell_XX'
    import re

    defs = re.findall(r"def (cell_\d+)\(\):", result)
    for name in defs:
        assert f"{name}()" in result


def test_convert_notebook_empty_notebook(tmp_path):
    """convert_notebook on a notebook with no code cells should produce a header."""
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
    nb_file = tmp_path / "empty_code.ipynb"
    nb_file.write_text(json.dumps(nb), encoding="utf-8")
    result = convert_notebook(nb_file, order="cell")
    # Should still produce a valid header
    assert "#!/usr/bin/env python3" in result
    # No function definitions expected
    assert "def cell_" not in result


def test_convert_notebook_string_path_accepted(notebook_path):
    """convert_notebook should accept a plain string path."""
    result = convert_notebook(str(notebook_path), order="cell")
    assert isinstance(result, str)
    assert "stx" in result


def test_convert_notebook_notebook_name_in_header(notebook_path):
    """Converted script docstring should reference the source notebook name."""
    result = convert_notebook(notebook_path, order="cell")
    assert "sample_analysis.ipynb" in result


# ---------------------------------------------------------------------------
# Invalid order
# ---------------------------------------------------------------------------


def test_convert_notebook_invalid_order_raises(notebook_path):
    """convert_notebook with invalid order should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid order"):
        convert_notebook(notebook_path, order="notebook")


def test_convert_notebook_invalid_order_message(notebook_path):
    """Error message should mention the bad value."""
    with pytest.raises(ValueError, match="notebook"):
        convert_notebook(notebook_path, order="notebook")


# ---------------------------------------------------------------------------
# DAG order with mock
# ---------------------------------------------------------------------------


def test_convert_notebook_dag_order_fallback(tmp_path):
    """DAG order with no execution history should fall back to cell order."""
    from unittest.mock import MagicMock, patch

    nb = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["x = 1"],
                "metadata": {},
                "id": "c1",
                "outputs": [],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_file = tmp_path / "dag_test.ipynb"
    nb_file.write_text(json.dumps(nb), encoding="utf-8")

    mock_db = MagicMock()
    mock_db.list_runs.return_value = []

    with patch("scitex.clew.get_db", return_value=mock_db):
        result = convert_notebook(nb_file, order="dag")

    # Falls back to cell order — should contain cell function
    assert "def cell_" in result
    assert "@stx.session" in result


def test_convert_notebook_dag_order_with_history(tmp_path):
    """DAG order with execution history should use compiled script format."""
    from unittest.mock import MagicMock, patch

    nb_file = tmp_path / "dag_hist.ipynb"
    nb_file.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": ["x = 1"],
                        "metadata": {},
                        "id": "c1",
                        "outputs": [],
                    }
                ],
                "metadata": {},
                "nbformat": 4,
                "nbformat_minor": 5,
            }
        ),
        encoding="utf-8",
    )

    runs = [
        {
            "session_id": "run-001",
            "started_at": "2026-01-01T00:00:00",
            "script_path": str(nb_file),
            "metadata": json.dumps({"notebook_path": str(nb_file.resolve())}),
        },
    ]

    mock_db = MagicMock()
    mock_db.list_runs.return_value = runs
    mock_db.get_file_hashes.return_value = {}

    with patch("scitex.clew.get_db", return_value=mock_db):
        result = convert_notebook(nb_file, order="dag")

    # Uses compiled script format (step_ functions, not cell_ functions)
    assert "def step_" in result
    assert "@stx.session" in result
    assert "Auto-compiled" in result


# EOF
