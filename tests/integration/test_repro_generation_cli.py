"""Generated identifiers retain randomness and predictable CLI discovery."""

import json
from datetime import datetime

import pytest
from click.testing import CliRunner

from scitex.cli.repro import repro


@pytest.mark.parametrize("command", ["generate-id", "gen-id"])
def test_custom_length_retains_timestamp_and_random_suffix(command):
    result = CliRunner().invoke(
        repro, [command, "--length", "12", "--count", "3", "--prefix", "exp_", "--json"]
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    ids = payload["data"]["ids"]
    assert payload["success"] is True
    assert len(ids) == len(set(ids)) == 3
    for identifier in ids:
        timestamp, suffix = identifier.removeprefix("exp_").rsplit("_", 1)
        datetime.strptime(timestamp, "%YY-%mM-%dD-%Hh%Mm%Ss")
        assert len(suffix) == 12 and suffix.isalnum()
        assert identifier.startswith("exp_")


@pytest.mark.parametrize("command", ["generate-timestamp", "gen-timestamp"])
def test_utc_timestamp_is_machine_readable_with_timezone(command):
    result = CliRunner().invoke(repro, [command, "--utc", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert payload["success"] is True
    assert data["format"] == "iso" and data["utc"] is True
    assert datetime.fromisoformat(data["timestamp"]).utcoffset().total_seconds() == 0


@pytest.mark.parametrize("option", ["--length", "--count"])
@pytest.mark.parametrize("value", ["0", "-1"])
def test_invalid_generation_bounds_fail_before_producing_ids(option, value):
    result = CliRunner().invoke(repro, ["generate-id", option, value])
    assert result.exit_code == 2
    assert not result.stdout


@pytest.mark.parametrize("arguments", [["--help"], ["--help-recursive"], ["--json"]])
def test_discovery_shows_full_names_and_omits_legacy_abbreviations(arguments):
    result = CliRunner().invoke(repro, arguments)
    assert result.exit_code == 0, result.output
    assert "generate-id" in result.stdout and "generate-timestamp" in result.stdout
    assert "gen-id" not in result.stdout and "gen-timestamp" not in result.stdout


def test_plain_text_generation_remains_one_identifier_per_line():
    result = CliRunner().invoke(repro, ["gen-id", "--count", "2"])
    assert result.exit_code == 0, result.output
    assert len(result.stdout.splitlines()) == 2
    assert all(len(line.rsplit("_", 1)[1]) == 8 for line in result.stdout.splitlines())


@pytest.mark.parametrize(
    "command", ["generate-id", "generate-timestamp", "gen-id", "gen-timestamp"]
)
def test_dry_run_takes_priority_over_yes_without_generated_values(command):
    result = CliRunner().invoke(repro, [command, "--dry-run", "--yes", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["data"]["dry_run"] is True
    assert "ids" not in payload["data"] and "timestamp" not in payload["data"]
