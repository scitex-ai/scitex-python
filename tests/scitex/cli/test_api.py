"""`scitex api list`: the global listing over installed packages (scitex-sdk aggregate)."""

import json

import pytest
from click.testing import CliRunner

pytest.importorskip("scitex_sdk.app.api_inventory")

from scitex.cli.api import api  # noqa: E402


@pytest.fixture(scope="module")
def sdk_listing():
    result = CliRunner().invoke(
        api, ["list", "--package", "scitex-sdk", "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_the_listing_names_the_packages_it_composed(sdk_listing):
    # Arrange
    doc = sdk_listing
    # Act
    packages = doc["sources"]["packages"]
    # Assert
    assert packages == ["scitex-sdk"]


def test_the_listing_carries_declared_operations(sdk_listing):
    # Arrange
    entries = sdk_listing["entries"]
    # Act
    paths = {e["path"] for e in entries if e["kind"] == "operation"}
    # Assert
    assert "/api/v1/scitex-sdk/skills" in paths


def test_strict_exits_nonzero_on_a_violation():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(api, ["list", "--package", "scitex-sdk", "--strict"])
    # Assert
    assert result.exit_code == 1
