"""Smoke test for examples/10_app.ipynb.

PS-505: a notebook smoke-test must actually execute the cells. We drive
`jupyter nbconvert --to notebook --execute` so the demo runs end-to-end;
`importlib` / `runpy` would never run `.ipynb` cells. No mocks — the real
notebook is executed in a subprocess. The `jupyter_cli` fixture skips
cleanly on minimal environments rather than reporting a false red.
"""

import subprocess
import sys
from pathlib import Path

import pytest

NOTEBOOK = Path(__file__).resolve().parents[2] / "examples" / "10_app.ipynb"


def test_example_notebook_exists():
    # Arrange
    notebook = NOTEBOOK
    # Act
    exists = notebook.is_file()
    # Assert
    assert exists, f"missing example notebook: {notebook}"


@pytest.mark.timeout(300)
def test_example_notebook_executes_via_nbconvert(jupyter_cli, tmp_path):
    # Arrange
    cmd = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--output",
        str(tmp_path / "executed.ipynb"),
        str(NOTEBOOK),
    ]
    # Act
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=290)
    # Assert
    assert proc.returncode == 0, proc.stderr
