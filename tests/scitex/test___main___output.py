"""The real module CLI retains its machine-readable version result channel."""

import subprocess
import sys

from scitex import __version__


def test_module_version_result_has_no_logging_prefix():
    # Arrange
    command = [sys.executable, "-m", "scitex", "--version"]
    # Act
    result = subprocess.run(command, capture_output=True, text=True, timeout=20)
    # Assert
    assert (result.returncode, result.stdout, result.stderr) == (
        0,
        f"python -m scitex, version {__version__}\n",
        "",
    )
