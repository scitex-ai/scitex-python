"""Construction reports describe selection on a real FastMCP parent."""

import pytest
from fastmcp import FastMCP

from scitex._mcp._mount_report import begin_report


@pytest.fixture
def selection():
    parent = FastMCP("report-fixture")
    peers, report = begin_report(
        parent,
        [
            ("enabled-owner", "enabled_module", "enabled"),
            ("disabled-owner", "disabled_module", "disabled"),
        ],
        lambda namespace: namespace == "enabled",
    )
    return parent, peers, report


def test_disabled_peer_is_not_resolved(selection):
    # Arrange
    _, peers, _ = selection
    # Act
    selected = peers
    # Assert
    assert selected == [("enabled_module", "enabled")]


def test_disabled_namespace_has_explicit_state(selection):
    # Arrange
    _, _, report = selection
    # Act
    state = report["disabled"]
    # Assert
    assert state == {"state": "disabled"}


def test_unresolved_namespace_is_not_reported_mounted(selection):
    # Arrange
    _, _, report = selection
    # Act
    state = report["enabled"]["state"]
    # Assert
    assert state == "unavailable"


def test_report_is_attached_to_owning_server(selection):
    # Arrange
    parent, _, report = selection
    # Act
    attached = parent._scitex_peer_mount_report
    # Assert
    assert attached is report
