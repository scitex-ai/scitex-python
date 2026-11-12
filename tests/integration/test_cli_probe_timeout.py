"""Timeout evidence stays bounded without replacing the original failure."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ._cli_probe_timeout import annotate_timeout


def test_actual_blocked_child_emits_stack_before_its_parent_timeout(tmp_path):
    # Arrange: exercise the actual watchdog in a disposable child, not CI's deadline.
    probe = Path(__file__).with_name("_cli_operator_policy_probe.py")
    code = (
        "import importlib.util, time\n"
        f"spec = importlib.util.spec_from_file_location('probe', {str(probe)!r})\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "module.run_with_diagnostics(lambda: time.sleep(30), seconds=0.05)\n"
    )
    # Act
    with pytest.raises(subprocess.TimeoutExpired) as caught:
        subprocess.run(
            [sys.executable, "-I", "-B", "-c", code],
            cwd=tmp_path, capture_output=True, timeout=2,
        )
    error = caught.value
    annotate_timeout(error)
    # Assert
    assert error.timeout == 2
    assert b"run_with_diagnostics" in error.stderr
    assert b"Timeout" in error.stderr
    assert error.stdout in (None, b"")


def test_successful_probe_cancels_watchdog_and_preserves_result():
    # Arrange
    probe = Path(__file__).with_name("_cli_operator_policy_probe.py")
    spec = importlib.util.spec_from_file_location("_watchdog_probe", probe)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Act
    value = module.run_with_diagnostics(lambda: {"ok": True})
    # Assert
    assert json.dumps(value) == '{"ok": true}'


@pytest.mark.parametrize("stderr", [None, "", b"", "child stack", b"child stack"])
def test_original_exception_and_output_are_preserved(stderr, capsys):
    # Arrange
    error = subprocess.TimeoutExpired(["probe"], 50, output=b"partial", stderr=stderr)
    # Act
    annotate_timeout(error)
    # Assert
    assert error.timeout == 50 and error.output == b"partial"
    assert error.stderr == stderr
    text = "\n".join(getattr(error, "__notes__", [])) + capsys.readouterr().err
    assert "original 50-second deadline" in text
    assert ("child stack" if stderr else "No child stack was captured.") in text


@pytest.mark.parametrize("padding", [b"x", b"\xff", "例".encode()])
def test_large_child_stderr_is_bounded_and_keeps_both_ends(capsys, padding):
    # Arrange
    error = subprocess.TimeoutExpired(
        ["probe"], 50, stderr=b"HEAD" + padding * 20000 + b"TAIL"
    )
    # Act
    annotate_timeout(error)
    # Assert
    text = "\n".join(getattr(error, "__notes__", [])) + capsys.readouterr().err
    assert "HEAD" in text and "TAIL" in text and "truncated" in text
    assert len(text.encode()) < 8400
