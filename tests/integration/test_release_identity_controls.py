#!/usr/bin/env python3
# File: ./tests/integration/test_release_identity_controls.py
"""Run the release-identity controls on every PR, not only at tag time.

.github/ci/test_release_identity.py checks frozen producer metadata against the
committed pyproject.toml. It used to run only in the release workflow's
preflight, so a dependency change (scitex-security rename, member floor bumps)
went unnoticed until a pushed tag was refused (v2.30.9). Running it here makes
pytest-matrix fail on the PR that causes the drift; the fix is
``.github/ci/refresh_producer_headers.py`` (see its docstring).
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_CONTROLS = _ROOT / ".github" / "ci" / "test_release_identity.py"


def _inside_git_checkout() -> bool:
    if shutil.which("git") is None:
        return False
    probe = subprocess.run(
        ["git", "-C", str(_ROOT), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return probe.returncode == 0


@pytest.mark.skipif(not _inside_git_checkout(), reason="needs the git checkout")
@pytest.mark.timeout(600)
def test_release_identity_controls_pass_for_the_committed_source():
    # Arrange
    command = [sys.executable, str(_CONTROLS)]
    # Act
    result = subprocess.run(command, cwd=_ROOT, capture_output=True, text=True)
    # Assert
    assert result.returncode == 0, result.stderr[-4000:]


# EOF
