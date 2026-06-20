"""Shared fixtures for the notebook example smoke-tests.

PS-505 requires each `tests/examples/test_<stem>.py` to drive
`jupyter nbconvert --execute`. The `jupyter_cli` fixture centralises the
"skip when Jupyter is absent" guard so each test body keeps a single
assertion (no mocks — it probes the real CLI on PATH).
"""

import shutil

import pytest


@pytest.fixture
def jupyter_cli():
    """Path to the `jupyter` CLI, or skip the test if it is not installed."""
    exe = shutil.which("jupyter")
    if exe is None:
        pytest.skip("jupyter CLI not installed")
    return exe
