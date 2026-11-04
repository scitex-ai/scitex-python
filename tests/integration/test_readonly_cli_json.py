"""Real CLI reads retain JSON boundaries and installed identity without effects."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_CHILD = r"""
import importlib,json,os,sys
from pathlib import Path
source,operation,fixture=sys.argv[1:]
sys.path.insert(0,source)
if fixture != '-':
    sys.path.insert(0,fixture)
from click.testing import CliRunner
if operation == 'missing-metadata':
    from scitex.cli._metadata import cli_metadata
    print(json.dumps(cli_metadata('owned-nonexistent-cli-package')))
elif operation == 'metadata':
    from importlib import metadata
    from scitex.cli.main import cli
    from scitex.cli._metadata import cli_metadata
    expected=cli_metadata('scitex')
    help_result=CliRunner().invoke(cli,['--help'])
    result=CliRunner().invoke(cli,['--json'])
    payload=json.loads(result.stdout)['data']
    print(json.dumps({'exit':result.exit_code,'metadata':payload['metadata'],
                      'header_in_help':' '.join(expected['header'].split()) in ' '.join(help_result.stdout.split()),
                      'metadata_equal':payload['metadata']==expected,
                      'version':metadata.version('scitex'),
                      'summary':metadata.metadata('scitex').get('Summary'),
                      'help_exit':help_result.exit_code}))
else:
    module_name,args=json.loads(operation)
    module=importlib.import_module('scitex.cli.'+module_name)
    command=getattr(module,module_name)
    def guard(event,args):
        if event in {'subprocess.Popen','socket.connect','socket.bind','os.mkdir','os.remove','os.rename'}:
            raise AssertionError('read-only CLI attempted effects: '+event)
        if event=='open':
            mode,flags=args[1:3]
            if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
                raise AssertionError('read-only CLI attempted file writes')
    sys.addaudithook(guard)
    if args[0] == '__parse__':
        with command.make_context('audit',args[1:]) as context:
            print(json.dumps({'parsed':context.params}))
        raise SystemExit(0)
    result=CliRunner().invoke(command,args)
    print(json.dumps({'exit':result.exit_code,'stdout':result.stdout,'stderr':result.stderr,
                      'exception':type(result.exception).__name__ if result.exception else None}))
"""


def _invoke(tmp_path, operation, fixture="-"):
    source = Path(__file__).resolve().parents[2] / "src"
    environment = dict(
        os.environ,
        HOME=str(tmp_path),
        SCITEX_DIR=str(tmp_path / "state"),
        SHELL="/bin/bash",
        PYTHONDONTWRITEBYTECODE="1",
        COVERAGE_FILE=str(tmp_path / ".coverage"),
    )
    child = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            _CHILD,
            str(source),
            operation if isinstance(operation, str) else json.dumps(operation),
            str(fixture),
        ],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        timeout=30,
        check=True,
    )
    return json.loads(child.stdout)


@pytest.mark.parametrize(
    "summary", ["Owned installed package summary", "研究 tools — Δ", ""]
)
def test_owned_distribution_identity_is_shared_by_help_and_json(tmp_path, summary):
    # Arrange
    dist = tmp_path / "scitex-9.8.7.dist-info"
    dist.mkdir()
    (dist / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: scitex\nVersion: 9.8.7\nSummary: "
        + summary
        + "\n"
    )
    # Act
    observed = _invoke(tmp_path, "metadata", tmp_path)
    # Assert
    assert (
        observed["exit"],
        observed["help_exit"],
        observed["metadata_equal"],
        observed["header_in_help"],
        observed["metadata"]["version"],
        observed["metadata"]["summary"],
    ) == (
        0,
        0,
        True,
        True,
        "9.8.7",
        summary or "Summary unavailable: no installed Summary",
    )


def test_actual_installed_identity_is_shared_by_help_and_json(tmp_path):
    # Arrange
    operation = "metadata"
    # Act
    observed = _invoke(tmp_path, operation)
    # Assert
    assert (
        observed["exit"],
        observed["metadata_equal"],
        observed["header_in_help"],
        observed["metadata"]["version"],
        observed["metadata"]["summary"],
    ) == (0, True, True, observed["version"], observed["summary"])


@pytest.mark.parametrize(
    "sessions", [None, {}, {"owned-id": {"pid": None, "url": "about:blank"}}]
)
def test_browser_inventory_reports_stored_sessions_without_liveness_claim(
    tmp_path, sessions
):
    # Arrange
    if sessions is not None:
        state = tmp_path / ".scitex/browser"
        state.mkdir(parents=True)
        (state / "sessions.json").write_text(json.dumps(sessions))
    # Act
    observed = _invoke(tmp_path, ["browser", ["list", "--json"]])
    # Assert
    assert (observed["exit"], json.loads(observed["stdout"]), observed["stderr"]) == (
        0,
        {"sessions": sessions or {}},
        "",
    )


@pytest.mark.parametrize(
    "content", ["{broken", "[]", '{"id": null}', '{"id": {"pid": NaN}}']
)
def test_malformed_browser_inventory_has_no_json_stdout(tmp_path, content):
    # Arrange
    state = tmp_path / ".scitex/browser"
    state.mkdir(parents=True)
    (state / "sessions.json").write_text(content)
    # Act
    observed = _invoke(tmp_path, ["browser", ["list", "--json"]])
    # Assert
    assert (
        observed["exit"],
        observed["stdout"],
        "Cannot read browser" in observed["stderr"],
    ) == (1, "", True)


@pytest.mark.parametrize("installed", [False, True])
def test_completion_status_reads_owned_shell_rc_without_effects(tmp_path, installed):
    # Arrange
    (tmp_path / ".bashrc").write_text("# scitex tab completion\n" if installed else "")
    # Act
    observed = _invoke(tmp_path, ["completion", ["status", "--json"]])
    # Assert
    assert (
        observed["exit"],
        json.loads(observed["stdout"])["installed"],
        observed["stderr"],
    ) == (0, installed, "")


def test_completion_status_refuses_unreadable_rc_without_stdout(tmp_path):
    # Arrange
    (tmp_path / ".bashrc").mkdir()
    # Act
    observed = _invoke(tmp_path, ["completion", ["status", "--json"]])
    # Assert
    assert (
        observed["exit"],
        observed["stdout"],
        "Cannot read shell completion" in observed["stderr"],
    ) == (1, "", True)


def test_config_show_json_reports_owned_configured_path(tmp_path):
    # Arrange
    operation = ["config", ["show", "base", "--json"]]
    # Act
    observed = _invoke(tmp_path, operation)
    # Assert
    assert (observed["exit"], json.loads(observed["stdout"]), observed["stderr"]) == (
        0,
        {"name": "base", "path": str(tmp_path / "state")},
        "",
    )


def test_unknown_config_has_only_stderr(tmp_path):
    # Arrange
    operation = ["config", ["show", "no-such-config", "--json"]]
    # Act
    observed = _invoke(tmp_path, operation)
    # Assert
    assert (
        observed["exit"],
        observed["stdout"],
        "Unknown path" in observed["stderr"],
    ) == (1, "", True)


@pytest.mark.parametrize(
    "arguments",
    [["status", "--json"], [".", "status", "--json"], ["--json", "status", "--json"]],
)
def test_audit_status_is_real_availability_without_tool_execution(tmp_path, arguments):
    # Arrange
    operation = ["audit", arguments]
    # Act
    observed = _invoke(tmp_path, operation)
    tools = json.loads(observed["stdout"])["tools"]
    # Assert
    assert (
        observed["exit"],
        set(tools),
        all(v["installed"] == (v["path"] is not None) for v in tools.values()),
        observed["stderr"],
    ) == (0, {"bandit", "shellcheck", "pip-audit", "gh"}, True, "")


def test_missing_distribution_has_explicit_unavailable_metadata(tmp_path):
    # Arrange
    operation = "missing-metadata"
    # Act
    observed = _invoke(tmp_path, operation)
    # Assert
    assert (
        observed["version"],
        observed["summary"],
        "version unresolved" in observed["header"],
    ) == (None, "Summary unavailable: no installed Summary", True)


@pytest.mark.parametrize(
    "arguments,expected",
    [([], "."), (["./status"], "./status"), (["--json", "./status"], "./status")],
)
def test_audit_parser_preserves_default_and_explicit_command_named_paths(
    tmp_path, arguments, expected
):
    # Arrange
    (tmp_path / "status").mkdir()
    # Act
    observed = _invoke(tmp_path, ["audit", ["__parse__", *arguments]])
    # Assert
    assert observed["parsed"]["path"] == expected


def test_audit_unknown_path_refuses_before_tools_or_scan(tmp_path):
    # Arrange
    operation = ["audit", ["no-such-owned-path", "--json"]]
    # Act
    observed = _invoke(tmp_path, operation)
    # Assert
    assert (
        observed["exit"],
        observed["stdout"],
        "does not exist" in observed["stderr"],
    ) == (2, "", True)
