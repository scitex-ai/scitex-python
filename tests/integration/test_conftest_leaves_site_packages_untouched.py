"""Regression test: importing tests/conftest.py must not touch site-packages.

Subprocess coverage is configured declaratively in pyproject.toml via
coverage.py's subprocess patch, so collecting tests must neither install
``.pth`` files into the interpreter's site-packages nor overwrite
caller-owned ``COVERAGE_PROCESS_START`` / ``COVERAGE_FILE`` values.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

CONFTEST_PATH = Path(__file__).resolve().parents[1] / "conftest.py"

_CHILD_CODE = textwrap.dedent(
    """\
    import os
    import runpy
    import site

    os.environ["COVERAGE_PROCESS_START"] = "SENTINEL_PROCESS_START"
    os.environ["COVERAGE_FILE"] = "SENTINEL_COVERAGE_FILE"

    site_dirs = list(site.getsitepackages()) + [site.getusersitepackages()]
    before = {
        d: sorted(os.listdir(d)) for d in site_dirs if os.path.isdir(d)
    }

    runpy.run_path(os.environ["CONFTEST_UNDER_TEST"])

    after = {
        d: sorted(os.listdir(d)) for d in site_dirs if os.path.isdir(d)
    }
    assert before == after, "conftest.py modified site-packages contents"
    assert (
        os.environ["COVERAGE_PROCESS_START"] == "SENTINEL_PROCESS_START"
    ), "conftest.py overwrote COVERAGE_PROCESS_START"
    assert (
        os.environ["COVERAGE_FILE"] == "SENTINEL_COVERAGE_FILE"
    ), "conftest.py overwrote COVERAGE_FILE"
    """
)


def test_conftest_leaves_site_packages_untouched():
    # Arrange
    env = dict(os.environ, CONFTEST_UNDER_TEST=str(CONFTEST_PATH))
    # Act
    proc = subprocess.run(
        [sys.executable, "-c", _CHILD_CODE],
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    # Assert
    assert proc.returncode == 0, proc.stderr
