"""Installation results remain prefix-free when routed through logging's result API."""

from scitex.helpers._install_guide import show_install_guide


def test_cli_installation_guide_preserves_exact_stdout(capsys):
    # Arrange — Click is a required core dependency, so availability is deterministic.
    expected = (
        "\n"
        + "=" * 70
        + "\nSciTeX Installation Guide\n"
        + "=" * 70
        + "\n\ncli - Command Line Interface\n  Status: Installed"
        + "\n  Install: pip install scitex[cli]\n\n"
        + "=" * 70
        + "\n\n"
    )
    # Act
    result = show_install_guide("cli")
    captured = capsys.readouterr()
    # Assert
    assert (result, captured.out, captured.err) == (None, expected, "")


def test_unknown_installation_module_remains_a_rendered_result(capsys):
    # Arrange
    name = "missing-module-for-result-test"
    # Act
    show_install_guide(name)
    captured = capsys.readouterr()
    # Assert
    assert (f"Module '{name}' not found." in captured.out, captured.err) == (True, "")
