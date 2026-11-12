"""Consent boundaries with real children and an inert local Socialia protocol."""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def social_workspace(tmp_path):
    """Only the owned protocol can receive a forwarded operation."""
    package = tmp_path / "socialia"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "__main__.py").write_text(
        "import json,sys\nfrom pathlib import Path\n"
        "args=sys.argv[1:]\n"
        "if '--yes' not in args or args[0] not in {'delete-post','mcp'}: raise SystemExit(2)\n"
        "Path('receipt.json').write_text(json.dumps(sys.argv[1:]))\n"
        "raise SystemExit(9 if Path('fail').exists() else 0)\n"
    )
    return tmp_path


def _invoke(workspace, arguments):
    source = Path(__file__).resolve().parents[3] / "src/scitex/cli/social.py"
    driver = (
        "import importlib.util,sys\n"
        "from click.testing import CliRunner\n"
        "spec=importlib.util.spec_from_file_location('social_cli',sys.argv[1])\n"
        "module=importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "result=CliRunner().invoke(module.social,sys.argv[2:])\n"
        "print(repr((result.exit_code,result.output)))\n"
    )
    environment = dict(os.environ)
    environment["COVERAGE_FILE"] = str(workspace / ".coverage")
    child = subprocess.run(
        [sys.executable, "-c", driver, str(source), *arguments],
        cwd=workspace,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    return ast.literal_eval(child.stdout)


OPERATIONS = [("delete", "twitter", "123"), ("mcp", "start")]
PROVIDER_OPERATIONS = {
    ("delete", "twitter", "123"): ["delete-post", "twitter", "123", "--yes"],
    ("mcp", "start"): ["mcp", "start", "--yes"],
}


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("flags", [[], ["--dry-run"], ["--yes", "--dry-run"]])
@pytest.mark.parametrize("as_json", [False, True])
def test_preview_never_starts_a_provider_process(
    social_workspace, operation, flags, as_json
):
    # Arrange
    arguments = [*operation, *flags, *(["--json"] if as_json else [])]
    receipt = social_workspace / "receipt.json"
    # Act
    code, output = _invoke(social_workspace, arguments)
    # Assert
    assert (code, receipt.exists(), bool(output)) == (0, False, True)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_preview_json_uses_the_shared_result_envelope(social_workspace, operation):
    # Arrange
    arguments = [*operation, "--json"]
    # Act
    code, output = _invoke(social_workspace, arguments)
    result = json.loads(output)
    # Assert
    assert (code, result["success"], result["data"]) == (
        0,
        True,
        {
            "dry_run": True,
            "command": [
                sys.executable,
                "-m",
                "socialia",
                *PROVIDER_OPERATIONS[operation],
                "--json",
            ],
        },
    )


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("as_json", [False, True])
def test_explicit_consent_preserves_the_actual_provider_arguments(
    social_workspace, operation, as_json
):
    # Arrange
    arguments = [*operation, "--yes", *(["--json"] if as_json else [])]
    expected = [*PROVIDER_OPERATIONS[operation], *(["--json"] if as_json else [])]
    # Act
    code, _ = _invoke(social_workspace, arguments)
    forwarded = json.loads((social_workspace / "receipt.json").read_text())
    # Assert
    assert (code, forwarded) == (0, expected)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_provider_failure_preserves_its_nonzero_exit(social_workspace, operation):
    # Arrange
    (social_workspace / "fail").touch()
    # Act
    code, _ = _invoke(social_workspace, [*operation, "--yes"])
    # Assert
    assert code == 9


@pytest.mark.parametrize("route", ["social", "socialia"])
@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("yes", [False, True])
def test_public_and_legacy_routes_share_the_same_consent_boundary(
    social_workspace, route, operation, yes
):
    # Arrange
    root = Path(__file__).resolve().parents[3]
    environment = dict(os.environ)
    for name in ["home", "state", "runtime"]:
        (social_workspace / name).mkdir()
    environment.update(
        PYTHONPATH=os.pathsep.join([str(root / "src"), str(social_workspace)]),
        HOME=str(social_workspace / "home"),
        SCITEX_DIR=str(social_workspace / "state"),
        XDG_RUNTIME_DIR=str(social_workspace / "runtime"),
        COVERAGE_FILE=str(social_workspace / ".coverage"),
    )
    arguments = [sys.executable, "-m", "scitex", route, *operation]
    if yes:
        arguments.append("--yes")
    receipt = social_workspace / "receipt.json"
    # Act
    child = subprocess.run(
        arguments,
        cwd=social_workspace,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    forwarded = json.loads(receipt.read_text()) if receipt.exists() else None
    # Assert
    assert (
        child.returncode,
        receipt.exists(),
        forwarded,
        yes or "[dry-run]" in child.stdout,
    ) == (0, yes, PROVIDER_OPERATIONS[operation] if yes else None, True), child.stderr
