"""Real umbrella help describes the installed version and delegated config."""

from importlib.metadata import version

from click.testing import CliRunner

from scitex.cli.main import cli


def test_root_help_uses_installed_distribution_version():
    # Arrange
    installed = version("scitex")
    # Act
    result = CliRunner().invoke(cli, ["--help"], prog_name="scitex")
    # Assert
    assert f"scitex (v{installed})" in result.output


def test_root_help_describes_actual_path_fallback():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help"], prog_name="scitex")
    # Assert
    assert all(text in result.output for text in ("SCITEX_DIR", "~/.scitex", ".env"))


def test_root_help_keeps_peer_configuration_delegated():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help"], prog_name="scitex")
    # Assert
    assert "Peer commands resolve their own settings" in result.output


def test_api_alias_help_has_concrete_invocation():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["list-python-apis", "--help"], prog_name="scitex")
    # Assert
    assert "scitex list-python-apis --json" in result.output
