"""Template documentation examples must parse against the real command tree."""

import shlex
from pathlib import Path

import pytest

from scitex.cli.template import template


@pytest.mark.parametrize(
    "name",
    [
        "modules/template.rst",
        "modules/writer.rst",
        "source/api/template.rst",
        "source/api/writer.rst",
    ],
)
def test_documented_template_commands_parse_without_running_providers(name):
    # Arrange
    root = Path(__file__).resolve().parents[3]
    document = root / "docs/sphinx" / name
    examples = [
        line.strip().split("#", 1)[0].strip()
        for line in document.read_text().splitlines()
        if line.strip().startswith("scitex dev template ")
    ]
    errors = []
    # Act
    for example in examples:
        arguments = shlex.split(example)[3:]
        try:
            command = template.commands[arguments[0]]
            with command.make_context(arguments[0], arguments[1:]):
                pass
        except Exception as error:
            errors.append((example, str(error)))
    # Assert
    assert (bool(examples), errors) == (True, [])
