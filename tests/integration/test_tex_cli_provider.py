"""The umbrella TeX adapter preserves the actual provider's compile contract."""

import shutil

import pytest
from click.testing import CliRunner

from scitex.cli.tex import tex


def test_missing_compiler_reports_provider_failure_without_adapter_type_error(
    tmp_path, monkeypatch
):
    # Arrange
    source = tmp_path / "paper.tex"
    source.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")
    monkeypatch.setenv("PATH", "")
    # Act
    result = CliRunner().invoke(tex, ["compile", str(source), "--verbose"])
    # Assert
    assert (result.exit_code, "Compiler not found" in result.output) == (127, True)


def test_compile_preview_preserves_source_auxiliary_files_and_output_directory(
    tmp_path, monkeypatch
):
    # Arrange
    source = tmp_path / "paper.tex"
    source.write_text("owned source")
    auxiliary = source.with_suffix(".aux")
    auxiliary.write_text("keep existing auxiliary data")
    output = tmp_path / "not-created" / "renamed.pdf"
    monkeypatch.setenv("PATH", "")
    # Act
    result = CliRunner().invoke(
        tex,
        [
            "compile",
            str(source),
            "--output",
            str(output),
            "--clean",
            "--dry-run",
            "--yes",
        ],
    )
    # Assert
    assert (
        result.exit_code,
        "Would compile" in result.output,
        source.read_text(),
        auxiliary.read_text(),
        output.parent.exists(),
    ) == (0, True, "owned source", "keep existing auxiliary data", False)


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="requires real pdflatex")
def test_real_compilation_honors_output_filename_and_cleans_generated_auxiliary_files(
    tmp_path,
):
    # Arrange
    source = tmp_path / "paper.tex"
    source.write_text(
        r"\documentclass{article}\begin{document}Owned test\end{document}"
    )
    target = tmp_path / "compiled" / "renamed.pdf"
    # Act
    result = CliRunner().invoke(
        tex, ["compile", str(source), "--output", str(target), "--clean", "--yes"]
    )
    # Assert
    assert (
        result.exit_code,
        target.read_bytes()[:5] if target.exists() else None,
        target.with_name("paper.pdf").exists(),
        target.with_name("paper.aux").exists(),
        target.with_name("paper.log").exists(),
    ) == (0, b"%PDF-", False, False, False)


def test_compile_refuses_to_replace_its_input_source(tmp_path):
    # Arrange
    source = tmp_path / "paper.tex"
    source.write_text("keep source")
    # Act
    result = CliRunner().invoke(tex, ["compile", str(source), "--output", str(source)])
    # Assert
    assert (result.exit_code, source.read_text()) == (2, "keep source")


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="requires real pdflatex")
def test_real_compilation_failure_does_not_report_success(tmp_path):
    # Arrange
    source = tmp_path / "broken.tex"
    source.write_text(
        r"\documentclass{article}\begin{document}\DefinitelyUndefined\end{document}"
    )
    # Act
    result = CliRunner().invoke(tex, ["compile", str(source), "--verbose", "--yes"])
    # Assert
    assert (result.exit_code != 0, "Compilation failed" in result.output) == (
        True,
        True,
    )
