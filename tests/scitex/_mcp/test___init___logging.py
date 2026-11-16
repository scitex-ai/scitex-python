"""A real fresh process loads operator settings before configuring logging."""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from scitex_dev._ecosystem._core import ECOSYSTEM


def test_environment_level_precedes_logging_setup(tmp_path):
    # Arrange
    setting = tmp_path / "logging.env"
    setting.write_text("SCITEX_LOGGING_LEVEL=ERROR\n")
    environment = dict(os.environ)
    environment.pop("SCITEX_LOGGING_LEVEL", None)
    environment["SCITEX_ENV_SRC"] = str(setting)
    environment["PYTHONPATH"] = str(Path(__file__).parents[3] / "src")
    for package, info in ECOSYSTEM.items():
        namespace = info.get("umbrella_subcommand", package.removeprefix("scitex-"))
        environment["SCITEX_MCP_USE_" + namespace.upper().replace("-", "_")] = "0"
    environment["SCITEX_MCP_USE_UI"] = "0"
    environment["SCITEX_MCP_USE_APP"] = "0"
    program = (
        "from scitex import _mcp;import logging,json;"
        "print(json.dumps({'level':logging.root.level}))"
    )
    # Act
    result = subprocess.run(
        [sys.executable, "-c", program],
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    observed = json.loads(result.stdout)["level"]
    # Assert
    assert observed == logging.ERROR
