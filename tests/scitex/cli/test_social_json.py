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
    (tmp_path / "runtime").mkdir()
    return tmp_path


def _invoke(workspace, arguments):
    source = Path(__file__).resolve().parents[3] / "src/scitex/cli/social.py"
    driver = (
        "import importlib.util,sys,json\nfrom click.testing import CliRunner\n"
        "spec=importlib.util.spec_from_file_location('social_cli',sys.argv[1])\n"
        "module=importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "result=CliRunner().invoke(module.social,sys.argv[2:])\n"
        "print('\\nROOT_RESULT='+json.dumps({'code':result.exit_code,'output':result.stdout,'stderr':result.stderr}))\n"
    )
    environment = dict(os.environ)
    environment.update(
        COVERAGE_FILE=str(workspace / ".coverage"),
        XDG_RUNTIME_DIR=str(workspace / "runtime"),
    )
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
    return (
        result["code"],
        provider_output + result["output"],
        child.stderr + result["stderr"],
    )


READS = [
    (["status"], ["status"]),
    (["check", "twitter"], ["check", "twitter"]),
    (["feed", "twitter", "--limit", "3"], ["feed", "twitter", "--limit", "3"]),
    (["show-me", "twitter"], ["show-me", "twitter"]),
    (["me", "twitter"], ["show-me", "twitter"]),
    (["mcp", "list-tools"], ["mcp", "list-tools"]),
    (["mcp", "show-installation"], ["mcp", "show-installation"]),
    (["mcp", "installation"], ["mcp", "show-installation"]),
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


@pytest.mark.parametrize("name", ["show-installation", "installation"])
def test_installation_names_forward_the_canonical_provider_read(
    social_read_workspace, name
):
    # Arrange
    receipt = social_read_workspace / "receipt.json"
    # Act
    code, _, _ = _invoke(social_read_workspace, ["mcp", name])
    # Assert
    assert (code, json.loads(receipt.read_text())) == (0, ["mcp", "show-installation"])


@pytest.mark.parametrize(
    "arguments,canonical",
    [(["me", "twitter"], "show-me"), (["mcp", "installation"], "show-installation")],
)
def test_legacy_reads_warn_on_stderr(social_read_workspace, arguments, canonical):
    # Arrange
    receipt = social_read_workspace / "receipt.json"
    # Act
    code, _, stderr = _invoke(social_read_workspace, arguments)
    # Assert
    assert (code, receipt.exists(), canonical in stderr, "deprecated" in stderr) == (
        0,
        True,
        True,
        True,
    )


@pytest.mark.parametrize(
    "arguments,canonical,legacy",
    [
        (["--help"], "show-me", "me"),
        (["mcp", "--help"], "show-installation", "installation"),
    ],
)
def test_read_help_advertises_only_canonical_names(
    social_read_workspace, arguments, canonical, legacy
):
    # Arrange
    receipt = social_read_workspace / "receipt.json"
    # Act
    code, output, _ = _invoke(social_read_workspace, arguments)
    # Assert
    assert (code, canonical in output, f"  {legacy} " in output, receipt.exists()) == (
        0,
        True,
        False,
        False,
    )


ANALYTICS_READS = [
    (["analytics", "show-realtime"], ["analytics", "show-realtime"]),
    (
        [
            "analytics",
            "show-pageviews",
            "--start",
            "30daysAgo",
            "--end",
            "today",
            "--path",
            "/research notes",
        ],
        [
            "analytics",
            "show-pageviews",
            "--start",
            "30daysAgo",
            "--end",
            "today",
            "--path",
            "/research notes",
        ],
    ),
    (
        ["analytics", "show-sources"],
        ["analytics", "show-sources", "--start", "7daysAgo", "--end", "today"],
    ),
]


@pytest.mark.parametrize("arguments,expected", ANALYTICS_READS)
@pytest.mark.parametrize("as_json", [False, True])
def test_analytics_reads_forward_real_provider_contracts(
    social_read_workspace, arguments, expected, as_json
):
    # Arrange
    request = [*arguments, *(["--json"] if as_json else [])]
    receipt = social_read_workspace / "receipt.json"
    # Act
    code, _, _ = _invoke(social_read_workspace, request)
    # Assert
    assert (code, receipt.exists()) == (0, True)
    assert json.loads(receipt.read_text()) == [
        *expected,
        *(["--json"] if as_json else []),
    ]


@pytest.mark.parametrize(
    "arguments", [["analytics", "twitter"], ["analytics", "ga", "--days", "30"]]
)
def test_unsupported_platform_analytics_never_launches_provider(
    social_read_workspace, arguments
):
    # Arrange
    receipt = social_read_workspace / "receipt.json"
    # Act
    code, _, _ = _invoke(social_read_workspace, arguments)
    # Assert
    assert (code, receipt.exists()) == (2, False)


def test_analytics_help_lists_provider_reads_without_running_them(
    social_read_workspace,
):
    # Arrange
    receipt = social_read_workspace / "receipt.json"
    # Act
    code, output, _ = _invoke(social_read_workspace, ["analytics", "--help"])
    # Assert
    assert (
        code,
        all(
            name in output
            for name in ["show-realtime", "show-pageviews", "show-sources"]
        ),
        receipt.exists(),
    ) == (0, True, False)
