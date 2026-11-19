"""Smoke test for examples/01_session.py.

`01_session.py` is a `@stx.session`-decorated CLI demo that writes output
artifacts when run, so a full end-to-end execution needs a session CONFIGS
layout and is exercised by the e2e journey test. Here we keep a fast,
side-effect-free smoke check: the file exists and compiles cleanly (a
syntax/parse regression in the published demo surfaces immediately). No
mocks.
"""

import re
from pathlib import Path

import yaml

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "01_session.py"
ANALYSIS_YAML = EXAMPLE.parent / "config" / "ANALYSIS.yaml"


def test_example_file_exists():
    # Arrange
    example = EXAMPLE
    # Act
    exists = example.is_file()
    # Assert
    assert exists, f"missing example file: {example}"


def test_example_compiles_without_syntax_error():
    # Arrange
    source = EXAMPLE.read_text(encoding="utf-8")
    # Act
    code = compile(source, str(EXAMPLE), "exec")
    # Assert
    assert code is not None


def test_example_reads_every_analysis_parameter_from_config_yaml():
    # Arrange
    source = EXAMPLE.read_text(encoding="utf-8")
    config = yaml.safe_load(ANALYSIS_YAML.read_text(encoding="utf-8"))
    # Act
    used_keys = set(re.findall(r"\bparams\.([A-Z][A-Z0-9_]*)", source))
    # Assert
    assert used_keys and used_keys <= set(config), (
        f"keys used by the example {sorted(used_keys)} must all be defined in "
        f"{ANALYSIS_YAML} (found {sorted(config)})"
    )
