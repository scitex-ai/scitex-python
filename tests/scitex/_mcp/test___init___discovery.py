"""Registry ownership and metadata discovery share the bounded coordinator."""

import sys
from time import monotonic

import pytest

from scitex import _mcp as umbrella


def test_registry_uses_sdk_app_owner():
    # Arrange
    peers = list(umbrella._iter_registry())
    # Act
    app = ("scitex-sdk", "scitex_sdk.app", "sdk")
    # Assert
    assert app in peers


def test_registry_uses_sdk_ui_owner():
    # Arrange
    peers = list(umbrella._iter_registry())
    # Act
    ui = ("scitex-sdk", "scitex_sdk.ui", "ui")
    # Assert
    assert ui in peers


def test_registry_omits_retired_app_ui():
    # Arrange
    peers = list(umbrella._iter_registry())
    # Act
    retired = {pip for pip, _, _ in peers} & {"scitex-app", "scitex-ui"}
    # Assert
    assert retired == set()


@pytest.fixture
def wedged_metadata(tmp_path_factory):
    from scitex._mcp._mount_plan import prepare_mount

    root = tmp_path_factory.mktemp("metadata_discovery")
    package = root / "metadatawedgedpeer"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "_mcp_server.py").write_text(
        """
import asyncio
from fastmcp import FastMCP
class Wedged(FastMCP):
    async def list_tools(self, *args, **kwargs):
        await asyncio.Event().wait()
    async def get_tools(self, *args, **kwargs):
        await asyncio.Event().wait()
mcp = Wedged("wedged-metadata")
""",
    )
    sys.path.insert(0, str(root))
    try:
        start = monotonic()
        peer, reason = umbrella._resolve_one_peer_bounded(
            "metadatawedgedpeer", "wedged", 0.1, prepare=prepare_mount
        )
        yield peer, reason, monotonic() - start
    finally:
        sys.path.remove(str(root))
        for name in list(sys.modules):
            if name == "metadatawedgedpeer" or name.startswith("metadatawedgedpeer."):
                del sys.modules[name]


def test_wedged_metadata_is_skipped(wedged_metadata):
    # Arrange
    peer, _, _ = wedged_metadata
    # Act
    resolved = peer
    # Assert
    assert resolved is None


def test_wedged_metadata_reports_timeout(wedged_metadata):
    # Arrange
    _, reason, _ = wedged_metadata
    # Act
    diagnostic = reason
    # Assert
    assert "timed out" in diagnostic


def test_wedged_metadata_returns_within_budget(wedged_metadata):
    # Arrange
    _, _, elapsed = wedged_metadata
    # Act
    duration = elapsed
    # Assert
    assert duration < 2
