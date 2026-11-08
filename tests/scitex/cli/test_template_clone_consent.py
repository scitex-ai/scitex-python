"""Template clone consent with the installed provider and a local Git remote."""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def clone_workspace(tmp_path):
    """Create a real template remote; prohibit all non-file Git protocols."""
    remote = tmp_path / "remote"
    remote.mkdir()
    environment = {
        "PATH": os.environ["PATH"],
        "HOME": str(tmp_path),
        "SCITEX_DIR": str(tmp_path / "state"),
        "COVERAGE_FILE": str(tmp_path / ".coverage"),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_ALLOW_PROTOCOL": "file",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": f"url.{remote.as_uri()}.insteadOf",
        "GIT_CONFIG_VALUE_0": "https://github.com/ywatanabe1989/pip-project-template.git",
    }
    subprocess.run(
        ["git", "init", "-b", "fixture", str(remote)],
        env=environment,
        capture_output=True,
        check=True,
    )
    (remote / "payload.txt").write_text("Owned offline template contents\n")
    subprocess.run(
        ["git", "-C", str(remote), "add", "payload.txt"],
        env=environment,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(remote),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "fixture",
        ],
        env=environment,
        capture_output=True,
        check=True,
    )
    return tmp_path, environment


def _invoke(workspace, flags):
    directory, environment = workspace
    source = Path(__file__).resolve().parents[3] / "src/scitex/cli/template.py"
    driver = (
        "import importlib.util,sys\n"
        "from click.testing import CliRunner\n"
        "spec=importlib.util.spec_from_file_location('template_cli',sys.argv[1])\n"
        "module=importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "result=CliRunner().invoke(module.template,sys.argv[2:])\n"
        "print(repr((result.exit_code,result.output)))\n"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            driver,
            str(source),
            "clone",
            "pip-project",
            str(directory / "destination"),
            "--branch",
            "fixture",
            "--git-strategy",
            "none",
            *flags,
        ],
        env=environment,
        cwd=directory,
        capture_output=True,
        text=True,
        check=True,
    )
    return ast.literal_eval(result.stdout)


@pytest.mark.parametrize("flags", [[], ["--dry-run"], ["--yes", "--dry-run"]])
def test_clone_preview_leaves_destination_absent(flags, clone_workspace):
    # Arrange
    directory, _ = clone_workspace
    # Act
    code, output = _invoke(clone_workspace, flags)
    # Assert
    assert (code, "Would clone" in output, (directory / "destination").exists()) == (
        0,
        True,
        False,
    )


def test_clone_yes_uses_the_real_provider_to_copy_local_git_contents(clone_workspace):
    # Arrange
    directory, _ = clone_workspace
    # Act
    code, output = _invoke(clone_workspace, ["--yes"])
    payload = (directory / "destination/payload.txt").read_text()
    # Assert
    assert (code, payload, "Successfully cloned" in output) == (
        0,
        "Owned offline template contents\n",
        True,
    )


def test_json_clone_preview_is_a_result_without_creating_the_destination(
    clone_workspace,
):
    # Arrange
    directory, _ = clone_workspace
    # Act
    code, output = _invoke(clone_workspace, ["--json"])
    result = json.loads(output)
    # Assert
    assert (
        code,
        result["success"],
        result["data"],
        (directory / "destination").exists(),
    ) == (
        0,
        True,
        {
            "dry_run": True,
            "template_id": "pip-project",
            "project_dir": str(directory / "destination"),
            "git_strategy": None,
            "branch": "fixture",
            "tag": None,
        },
        False,
    )
