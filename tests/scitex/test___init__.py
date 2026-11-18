#!/usr/bin/env python3
# File: tests/scitex/test___init__.py
"""``import scitex`` configures no logging (PS-220).

The umbrella no longer sets third-party logger levels. SQLAlchemy's
per-statement INFO records are held at WARNING by scitex_logging.configure(),
the code that raises the root logger to INFO.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

# Runs in a fresh interpreter so no earlier test has touched logging.
_PROBE = """
import json, logging
import scitex
names = ["sqlalchemy", "sqlalchemy.engine", "sqlalchemy.engine.Engine", "sqlalchemy.pool"]
print(json.dumps({
    "levels": [logging.getLogger(n).level for n in names],
    "root_handlers": len(logging.getLogger().handlers),
}))
"""


@pytest.fixture(scope="module")
def after_import():
    proc = subprocess.run(
        [sys.executable, "-c", _PROBE],
        capture_output=True,
        text=True,
        timeout=300,
        check=True,
    )
    return json.loads(proc.stdout.strip().splitlines()[-1])


def test_import_scitex_leaves_sqlalchemy_logger_levels_unset(after_import):
    # Arrange
    state = after_import
    # Act
    levels = state["levels"]
    # Assert
    assert levels == [0, 0, 0, 0]


def test_import_scitex_installs_no_root_handlers(after_import):
    # Arrange
    state = after_import
    # Act
    count = state["root_handlers"]
    # Assert
    assert count == 0


# EOF
