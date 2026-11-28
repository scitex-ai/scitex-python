"""``import scitex`` must not copy ``.env`` into os.environ (scitex-config#47).

Through scitex-config 0.3.x, ``import scitex`` ran ``PATHS = ScitexPaths()``.
That called ``get_scitex_dir()`` and then ``load_dotenv()``, which exported
every key of ``./.env`` / ``$HOME/.env``, credentials included, to the process
and all of its subprocesses. A fresh interpreter here gets a real temporary
HOME/cwd holding a real ``.env``; nothing is mocked.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

FAKE_KEYS = ("FAKE_SERVICE_API_KEY", "FAKE_DB_PASSWORD")

_PROBE = textwrap.dedent(
    """
    import os, subprocess, sys
    import scitex
    scitex.PATHS.base
    child = subprocess.run(
        [sys.executable, "-c", "import os; print(' '.join(sorted(os.environ)))"],
        capture_output=True, text=True, check=True,
    )
    print(" ".join(k for k in os.environ if k.startswith("FAKE_")) or "<none>")
    print(" ".join(k for k in child.stdout.split() if k.startswith("FAKE_")) or "<none>")
    """
)


@pytest.fixture
def probe_lines(tmp_path: Path) -> list:
    """Import scitex in a child whose HOME and cwd .env hold secret-shaped keys."""
    body = "".join(f"{key}=fake-value-not-a-secret\n" for key in FAKE_KEYS)
    (tmp_path / ".env").write_text(body)
    env = {k: v for k, v in os.environ.items() if not k.startswith("FAKE_")}
    env["HOME"] = str(tmp_path)
    env["PYTHONPATH"] = os.pathsep.join(p for p in sys.path if p)
    result = subprocess.run(
        [sys.executable, "-c", _PROBE],
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout.strip().splitlines()[-2:]


def test_import_scitex_exports_no_dotenv_key(probe_lines: list) -> None:
    # Arrange
    expected = "<none>"
    # Act
    in_process = probe_lines[0]
    # Assert
    assert in_process == expected


def test_subprocess_after_import_inherits_no_dotenv_key(probe_lines: list) -> None:
    # Arrange
    expected = "<none>"
    # Act
    in_child = probe_lines[1]
    # Assert
    assert in_child == expected
