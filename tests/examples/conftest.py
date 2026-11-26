"""Shared fixtures for the notebook example smoke-tests.

PS-505 requires each `tests/examples/test_<stem>.py` to drive
`jupyter nbconvert --execute`. The `jupyter_cli` fixture centralises the
"skip when the execution environment is incomplete" guard so each test
body keeps a single assertion (no mocks — it probes the real CLI + the
real kernelspec list on PATH).

`nbconvert --execute` needs BOTH the `jupyter` CLI *and* a registered
`python3` IPython kernelspec. Bare CI images (and the per-PR matrix) ship
the CLI but not the kernel, which surfaced as `NoSuchKernel: python3`
false-reds. The fixture skips cleanly on either gap rather than reporting
an environment defect as a test failure.
"""

import os
import shutil
import subprocess

import pytest


@pytest.fixture
def provenance_store():
    """The disposable PostgreSQL that Clew records into, or skip.

    Notebooks that save through `stx.io` or call Clew write provenance to the
    Clew store, which is PostgreSQL. tests/_database_isolation.py points
    SCITEX_STORE_DSN at a deliberately unreachable sentinel when no
    disposable database is configured (e.g. the release SIF test leg); there
    the notebook cannot run, which is an environment gap, not a code defect.
    """
    target = os.environ.get("SCITEX_STORE_DSN", "")
    if not target or "no_test_database_configured" in target:
        pytest.skip("No disposable PostgreSQL configured for the Clew store")
    return target


@pytest.fixture
def jupyter_cli():
    """Path to the `jupyter` CLI, skipping when execution is impossible.

    Skips when the `jupyter` CLI is absent, or when no `python3` IPython
    kernelspec is registered (without it, `nbconvert --execute` fails
    with `NoSuchKernel: python3` — an environment gap, not a code defect).
    """
    exe = shutil.which("jupyter")
    if exe is None:
        pytest.skip("jupyter CLI not installed")
    try:
        listed = subprocess.run(
            [exe, "kernelspec", "list"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover
        pytest.skip(f"could not enumerate jupyter kernelspecs: {exc}")
    if "python3" not in listed.stdout:
        pytest.skip(
            "no 'python3' IPython kernelspec registered "
            "(nbconvert --execute would fail with NoSuchKernel)"
        )
    return exe
