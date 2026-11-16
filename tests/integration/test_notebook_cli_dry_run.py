"""The installed notebook provider must honor automation preview controls."""

import nbformat
import pytest
from click.testing import CliRunner

from scitex.cli.main import cli


@pytest.mark.parametrize(
    "command,filename",
    [("compile-notebook", "planned.mmd"), ("convert-notebook", "planned.py")],
)
def test_real_notebook_provider_dry_run_preserves_input_and_creates_no_output(
    tmp_path, command, filename
):
    notebook = tmp_path / "owned.ipynb"
    nbformat.write(
        nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("value = 7")]),
        notebook,
    )
    before = notebook.read_bytes()
    output = tmp_path / filename
    result = CliRunner().invoke(
        cli,
        [
            "notebook",
            command,
            str(notebook),
            "--output",
            str(output),
            "--dry-run",
            "--yes",
        ],
    )
    assert result.exit_code == 0, result.output
    assert result.stdout
    assert not output.exists()
    assert notebook.read_bytes() == before
