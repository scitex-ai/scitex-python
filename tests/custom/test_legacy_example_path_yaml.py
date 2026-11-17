#!/usr/bin/env python3
# File: tests/custom/test_legacy_example_path_yaml.py
"""The bundled example project's ``config/PATH.yaml`` must match its accessors.

@stx.session exposes the top-level keys of ``config/PATH.yaml`` directly as
``CONFIG.PATH.<KEY>``. An outer ``PATH:`` wrapper (quality-audit
PS-PATH-001) moves everything to ``CONFIG.PATH.PATH.<KEY>`` and every
``CONFIG.PATH.<KEY>`` access in the example's scripts fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

_EXAMPLE = (
    Path(__file__).resolve().parents[2]
    / "examples/_legacy/scitex/session/docs/to_claude/examples"
    / "example-python-project-scitex"
)
_ACCESS = re.compile(r"CONFIG\.PATH\.([A-Z_][A-Z0-9_]*(?:\.[A-Z_][A-Z0-9_]*)*)")


def _path_config() -> dict:
    return yaml.safe_load((_EXAMPLE / "config" / "PATH.yaml").read_text())


def _accessed_key_paths() -> set[str]:
    found = set()
    for script in sorted((_EXAMPLE / "scripts").rglob("*.py")):
        found.update(_ACCESS.findall(script.read_text()))
    return found


def _unresolvable(config: dict, key_paths: set[str]) -> list[str]:
    missing = []
    for key_path in sorted(key_paths):
        node = config
        for key in key_path.split("."):
            if not isinstance(node, dict) or key not in node:
                missing.append(key_path)
                break
            node = node[key]
    return missing


def test_path_yaml_has_no_outer_path_wrapper():
    # Arrange
    config = _path_config()
    # Act
    top_level = set(config)
    # Assert
    assert "PATH" not in top_level


def test_every_config_path_access_in_example_scripts_resolves():
    # Arrange
    config = _path_config()
    key_paths = _accessed_key_paths()
    # Act
    missing = _unresolvable(config, key_paths)
    # Assert
    assert key_paths and missing == []


# EOF
