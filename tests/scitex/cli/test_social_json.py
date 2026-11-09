"""Social JSON reads keep provider-owned output and command-level flags."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def social_read_workspace(tmp_path):
    """Local protocol distinguishes command JSON from the unused root flag."""
    package = tmp_path / "socialia"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "__main__.py").write_text(
        "import json,sys\nfrom pathlib import Path\n"
        "args=sys.argv[1:]\n"
        "Path('receipt.json').write_text(json.dumps(args))\n"
        "if Path('fail').exists():\n"
        " print('controlled provider refusal',file=sys.stderr)\n"
        " raise SystemExit(7)\n"
        "if args and args[-1]=='--json':\n"
        " print(json.dumps({'provider':'socialia','arguments':args[:-1]}))\n"
        "else:\n"
        " print('provider text: '+repr(args))\n"
    )
    return tmp_path


def _invoke(workspace, arguments):
    source = Path(__file__).resolve().parents[3] / "src/scitex/cli/social.py"
    driver = (
        "import importlib.util,sys,json\nfrom click.testing import CliRunner\n"
        "spec=importlib.util.spec_from_file_location('social_cli',sys.argv[1])\n"
        "module=importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "result=CliRunner().invoke(module.social,sys.argv[2:])\n"
        "print('\\nROOT_RESULT='+json.dumps({'code':result.exit_code,'output':result.output}))\n"
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
    provider_output, footer = child.stdout.rsplit("\nROOT_RESULT=", 1)
    result = json.loads(footer)
    return result["code"], provider_output + result["output"], child.stderr


READS = [
    (["status"], ["status"]),
    (["check", "twitter"], ["check", "twitter"]),
    (["feed", "twitter", "--limit", "3"], ["feed", "twitter", "--limit", "3"]),
    (["me", "twitter"], ["me", "twitter"]),
    (["mcp", "list-tools"], ["mcp", "list-tools"]),
]


@pytest.mark.parametrize("arguments,expected", READS)
def test_json_read_preserves_provider_data(social_read_workspace, arguments, expected):
    # Arrange
    request = [*arguments, "--json"]
    # Act
    code, output, _ = _invoke(social_read_workspace, request)
    result = json.loads(output)
    # Assert
    assert (code, result) == (0, {"provider": "socialia", "arguments": expected})


@pytest.mark.parametrize("arguments,expected", READS)
def test_plain_read_keeps_its_original_provider_arguments(
    social_read_workspace, arguments, expected
):
    # Arrange
    receipt = social_read_workspace / "receipt.json"
    # Act
    code, output, _ = _invoke(social_read_workspace, arguments)
    forwarded = json.loads(receipt.read_text())
    # Assert
    assert (code, forwarded, output) == (
        0,
        expected,
        "provider text: " + repr(expected) + "\n",
    )


def test_provider_refusal_is_not_replaced_by_success_json(social_read_workspace):
    # Arrange
    (social_read_workspace / "fail").touch()
    # Act
    code, output, stderr = _invoke(
        social_read_workspace, ["mcp", "list-tools", "--json"]
    )
    # Assert
    assert (code, output, stderr) == (7, "", "controlled provider refusal\n")
