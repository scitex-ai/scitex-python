"""Real introspection remains usable through canonical and migration routes."""

import json

import pytest
from click.testing import CliRunner

from scitex.cli.introspect import introspect

CASES = [
    ("show-signature", "q", ["json.dumps"]),
    ("show-source", "qq", ["json.dumps", "--max-lines", "5"]),
    ("list-members", "dir", ["json", "--kind", "functions"]),
    ("list-apis", "api", ["json", "--root-only", "--max-depth", "1"]),
    ("show-docstring", "docstring", ["json.dumps", "--format", "summary"]),
    ("list-exports", "exports", ["json"]),
    ("list-examples", "examples", ["json.dumps", "--max-results", "1"]),
    ("show-hierarchy", "hierarchy", ["json.JSONEncoder", "--max-depth", "1"]),
    ("show-type-hints", "hints", ["json.dumps"]),
    ("list-imports", "imports", ["json"]),
    ("list-dependencies", "deps", ["json"]),
    ("list-calls", "calls", ["json.dumps"]),
]


@pytest.mark.parametrize("canonical,legacy,arguments", CASES)
def test_canonical_and_legacy_routes_use_the_same_real_provider(
    canonical, legacy, arguments, tmp_path
):
    runner = CliRunner()
    args = list(arguments)
    if canonical == "list-examples":
        args += ["--search-paths", str(tmp_path)]
    current = runner.invoke(introspect, [canonical, *args, "--json"])
    previous = runner.invoke(introspect, [legacy, *args, "--json"])
    assert current.exit_code == previous.exit_code == 0, (
        current.output,
        previous.output,
    )
    assert json.loads(current.stdout)["data"] == json.loads(previous.stdout)["data"]
    assert json.loads(current.stdout)["success"] is True


def test_json_discovery_advertises_only_the_full_verb_names():
    result = CliRunner().invoke(introspect, ["--json"])
    assert result.exit_code == 0, result.output
    assert set(json.loads(result.stdout)["data"]["commands"]) == {
        canonical for canonical, _, _ in CASES
    }


def test_recursive_help_does_not_advertise_hidden_migration_commands():
    result = CliRunner().invoke(introspect, ["--help-recursive"])
    assert result.exit_code == 0, result.output
    headings = [line for line in result.stdout.splitlines() if line.startswith("━━━")]
    assert len(headings) == len(CASES) + 1
    assert all(
        any(canonical in heading for canonical, _, _ in CASES)
        for heading in headings[1:]
    )


@pytest.mark.parametrize("command", ["show-signature", "q"])
def test_missing_object_returns_only_structured_error_on_stdout(command):
    result = CliRunner().invoke(
        introspect, [command, "json.__owned_missing_object__", "--json"]
    )
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["success"] is False and payload["error"]


def test_recursive_help_keeps_the_actual_developer_namespace():
    from scitex.cli.main import cli

    result = CliRunner().invoke(
        cli, ["dev", "introspect", "--help-recursive"], prog_name="scitex"
    )
    assert result.exit_code == 0, result.output
    headings = [line for line in result.stdout.splitlines() if line.startswith("━━━")]
    assert len(headings) == len(CASES) + 1
    assert all(line.startswith("━━━ scitex dev introspect") for line in headings)
