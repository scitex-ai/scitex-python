"""The events extra must supply the real provider behind advertised workflows."""

import json

import pytest
from click.testing import CliRunner

from scitex.cli.main import cli


@pytest.fixture
def owned_event(tmp_path, monkeypatch):
    import scitex as stx

    monkeypatch.setenv("SCITEX_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("SCITEX_API_KEY", "")
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    return stx.events.emit(
        "test_complete", project="owned-fixture", payload={"rows": 3}
    )


def test_python_event_facade_reaches_installed_provider(owned_event):
    # Arrange
    import scitex as stx

    # Act
    latest = stx.events.latest("test_complete")
    # Assert
    assert latest == owned_event.to_dict()


@pytest.mark.parametrize(
    "command,key",
    [("get-latest", "event"), ("list-history", "events"), ("list-types", "types")],
)
def test_event_read_commands_return_machine_readable_results(owned_event, command, key):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["event", command, "--json"])
    data = json.loads(result.stdout)
    # Assert
    assert (result.exit_code, data["success"], bool(data["data"][key])) == (
        0,
        True,
        True,
    )


@pytest.mark.parametrize(
    "old,new,args",
    [
        ("latest", "get-latest", ["--type", "test_complete"]),
        ("history", "list-history", ["--limit", "1"]),
        ("types", "list-types", []),
    ],
)
def test_legacy_event_read_routes_preserve_output_and_status(
    owned_event, old, new, args
):
    # Arrange
    runner = CliRunner()
    # Act
    canonical = runner.invoke(cli, ["event", new, *args])
    legacy = runner.invoke(cli, ["event", old, *args])
    # Assert
    assert (canonical.exit_code, legacy.exit_code, legacy.stdout) == (
        0,
        0,
        canonical.stdout,
    )
