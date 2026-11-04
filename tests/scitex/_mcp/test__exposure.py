"""Disabled provider modules must never enter umbrella discovery."""

import importlib
import sys

import pytest


@pytest.mark.parametrize(
    "enabled,environment,expected",
    [(False, "1", False), (False, "0", False), (True, "0", False), (True, "1", True)],
)
def test_package_switch_cannot_be_overridden_by_namespace_environment(
    monkeypatch, enabled, environment, expected
):
    # Arrange
    from scitex._mcp._exposure import is_exposed

    monkeypatch.setenv("SCITEX_MCP_USE_FIXTURE", environment)
    # Act
    observed = is_exposed("fixture-owner", "fixture", {"fixture-owner": enabled})
    # Assert
    assert observed is expected


def test_disabled_provider_is_not_imported_but_selected_provider_remains_callable(
    tmp_path, monkeypatch
):
    # Arrange
    from fastmcp import Client, FastMCP

    from scitex._mcp import register_all_tools

    marker = tmp_path / "disabled-imported"
    (tmp_path / "context_disabled_peer.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('imported')\n"
    )
    package = tmp_path / "context_selected_peer"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "_mcp_server.py").write_text(
        "from fastmcp import FastMCP\n"
        "mcp = FastMCP('selected-fixture')\n"
        "@mcp.tool()\ndef ping() -> str:\n    return 'fixture-pong'\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    policy = {
        "disabled-owner": False,
        "selected-owner": True,
        "figrecipe": False,
        "socialia": False,
        "scitex-dev": False,
        "scitex-cloud": False,
        "scitex": False,
    }
    probe = FastMCP("exposure-fixture")
    # Act
    register_all_tools(
        probe,
        package_policy=policy,
        iter_registry=lambda: [
            ("disabled-owner", "context_disabled_peer", "blocked"),
            ("selected-owner", "context_selected_peer", "selected"),
        ],
    )

    async def inspect():
        async with Client(probe) as client:
            tools = await client.list_tools()
            result = await client.call_tool("selected_ping", {})
            return tools, result

    import asyncio

    tools, result = asyncio.run(inspect())
    # Assert
    assert not marker.exists()
    assert "context_disabled_peer" not in sys.modules
    assert {tool.name for tool in tools} == {"selected_ping"}
    assert result.data == "fixture-pong"


def test_extras_do_not_import_disabled_provider_modules(monkeypatch):
    # Arrange
    from fastmcp import FastMCP

    from scitex._mcp._peer_extras import register_peer_extras

    before = set(sys.modules)
    disabled = dict.fromkeys(
        ["figrecipe", "socialia", "scitex-dev", "scitex-cloud"], False
    )
    # Act
    register_peer_extras(FastMCP("disabled-extras"), package_policy=disabled)
    # Assert
    assert set(sys.modules) == before


def test_existing_dev_knob_is_read_by_umbrella_policy(tmp_path, monkeypatch):
    # Arrange
    from scitex_dev._core.config import set_package_knob

    from scitex._mcp._exposure import load_package_policy

    state = tmp_path / "knobs.json"
    set_package_knob("scitex-io", "mcp", False, path=state)
    monkeypatch.setenv("SCITEX_DEV_KNOB_STATE", str(state))
    # Act
    disabled = load_package_policy()["scitex-io"]
    set_package_knob("scitex-io", "mcp", True, path=state)
    enabled = load_package_policy()["scitex-io"]
    # Assert
    assert disabled is False
    assert enabled is True


def test_search_uses_upstream_discovery_or_explicitly_refuses_missing_dev_capability(
    monkeypatch,
):
    # Arrange
    import asyncio
    import importlib.util

    from fastmcp import Client, FastMCP

    from scitex._mcp._exposure import configure_discovery

    probe = FastMCP("search-policy-fixture")

    @probe.tool()
    def selected_fixture() -> str:
        raise AssertionError("Discovery must not execute the fixture")

    monkeypatch.setenv("SCITEX_MCP_DISCOVERY", "search")
    monkeypatch.setenv("SCITEX_MCP_SEARCH_LIMIT", "1")
    # Act / Assert
    if importlib.util.find_spec("scitex_dev.context") is None:
        with pytest.raises(ModuleNotFoundError, match="scitex_dev.context"):
            configure_discovery(probe)
    else:
        configure_discovery(probe)

        async def inspect():
            async with Client(probe) as client:
                tools = await client.list_tools()
                result = await client.call_tool(
                    "search_tools", {"pattern": "selected_fixture"}
                )
                return tools, result

        tools, result = asyncio.run(inspect())
        assert {tool.name for tool in tools} == {"search_tools", "call_tool"}
        assert "selected_fixture" in str(result.data)


@pytest.mark.parametrize("mode", ["", "invalid", "SEARCH"])
def test_invalid_discovery_mode_is_not_silently_treated_as_full(monkeypatch, mode):
    # Arrange
    from scitex._mcp._exposure import configure_discovery

    monkeypatch.setenv("SCITEX_MCP_DISCOVERY", mode)
    # Act / Assert
    with pytest.raises(ValueError, match="SCITEX_MCP_DISCOVERY"):
        configure_discovery(object())
