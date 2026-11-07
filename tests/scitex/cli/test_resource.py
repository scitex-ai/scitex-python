"""CLI resource readings must preserve the actual provider's tabular units."""

import csv
import json

import pytest

from click.testing import CliRunner

from scitex.cli.resource import resource

COLUMNS = ["Timestamp", "CPU [%]", "RAM [GiB]", "GPU [%]", "VRAM [GiB]"]


def test_usage_displays_provider_units_instead_of_missing_dictionary_values():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(resource, ["usage"])
    # Assert
    assert result.exit_code == 0 and all(c in result.output for c in COLUMNS)


def test_usage_json_contains_a_structured_sample_not_a_dataframe_string():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(resource, ["usage", "--json"])
    payload = json.loads(result.output)
    # Assert
    assert result.exit_code == 0 and isinstance(payload, dict)
    assert payload["success"] is True
    sample = payload["data"]["samples"][0]
    assert list(sample) == COLUMNS
    assert isinstance(sample["Timestamp"], str)
    assert all(isinstance(sample[c], (int, float)) for c in COLUMNS[1:])
    assert sample["RAM [GiB]"] > 0


def test_monitor_logs_real_ram_in_gib_instead_of_zero_memory_percent(tmp_path):
    # Arrange
    log = tmp_path / "measurements.csv"
    runner = CliRunner()
    # Act
    result = runner.invoke(
        resource, ["monitor", "--count", "2", "--interval", "0.01", "--log", str(log)]
    )
    with log.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    # Assert
    assert result.exit_code == 0 and len(rows) == 2
    assert list(rows[0]) == COLUMNS
    assert all(float(row["RAM [GiB]"]) > 0 for row in rows)
    assert "RAM:" in result.output and "GiB" in result.output


@pytest.mark.parametrize(
    "option,value",
    [("--count", "0"), ("--count", "-1"), ("--interval", "0"), ("--interval", "-1")],
)
def test_invalid_monitor_limits_are_refused_before_opening_a_log(
    tmp_path, option, value
):
    # Arrange
    log = tmp_path / "must-not-exist.csv"
    # Act
    result = CliRunner().invoke(resource, ["monitor", option, value, "--log", str(log)])
    # Assert
    assert result.exit_code == 2 and not log.exists()
