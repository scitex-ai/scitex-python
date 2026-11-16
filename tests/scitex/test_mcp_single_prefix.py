"""Real protocol coverage for the shared mount boundary, without peer imports."""

import asyncio
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
from fastmcp import Client, FastMCP
from fastmcp.server.middleware import Middleware


@pytest.fixture(scope="module")
def boundary():
    # Load only the boundary: importing the umbrella discovers every installed
    # peer and is intentionally a separate integration scope.
    name = "_scitex_mount_contract"
    package = ModuleType(name)
    package.__path__ = [str(Path(__file__).parents[2] / "src/scitex/_mcp")]
    sys.modules[name] = package
    modules = []
    try:
        for leaf in ("_compat", "_mount_plan"):
            spec = importlib.util.spec_from_file_location(
                name + "." + leaf, Path(package.__path__[0]) / (leaf + ".py")
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            modules.append(module)
        yield modules
    finally:
        for key in list(sys.modules):
            if key == name or key.startswith(name + "."):
                del sys.modules[key]


@pytest.mark.parametrize(
    "namespace,raw,expected",
    [
        ("ui", "ui_get_component", "ui_get_component"),
        ("scholar", "scholar_search", "scholar_search"),
        ("notebook", "notebook_check", "notebook_check"),
        ("io", "io_load", "io_load"),
        ("dev", "dev_config_show", "dev_config_show"),
        ("clew", "clew_clew_status", "clew_status"),
        ("audio", "audio_speak", "audio_speak"),
        ("sdk", "app_read_file", "sdk_read_file"),
        ("hub", "cloud_sdk_data_get", "hub_sdk_data_get"),
        ("hub", "hub_skills_get", "hub_skills_get"),
        ("hub", "api_scholar_search", "hub_api_scholar_search"),
        ("dev", "linter_check_source", "dev_linter_check_source"),
    ],
)
def test_protocol_name_and_safe_fixture_call(boundary, namespace, raw, expected):
    compat, planner = boundary
    calls = []

    class RecordCalls(Middleware):
        async def on_call_tool(self, context, call_next):
            calls.append(context.message.name)
            return await call_next(context)

    leaf = FastMCP("fixture", middleware=[RecordCalls()])

    @leaf.tool(name=raw)
    def echo(value: str) -> str:
        """A local fixture, never a live service or filesystem operation."""
        return value

    @leaf.resource("fixture://text")
    def text() -> str:
        return "resource retained"

    @leaf.prompt()
    def help_me() -> str:
        return "prompt retained"

    parent = FastMCP("parent")
    plan = planner.prepare_mount(leaf, namespace)
    compat.safe_mount(
        parent, plan.server, namespace=namespace, tool_names=plan.tool_names
    )

    async def exercise():
        async with Client(parent) as client:
            tools = await client.list_tools()
            assert [t.name for t in tools] == [expected]
            assert "value" in tools[0].inputSchema["properties"]
            result = await client.call_tool(expected, {"value": "ok"})
            assert not result.is_error
            assert result.content[0].text == "ok"
            assert [p.name for p in await client.list_prompts()] == [
                namespace + "_help_me"
            ]
            resources = await client.list_resources()
            assert str(resources[0].uri) == "fixture://" + namespace + "/text"
            assert (await client.read_resource(resources[0].uri))[
                0
            ].text == "resource retained"
        async with Client(leaf) as client:
            assert [t.name for t in await client.list_tools()] == [raw]

    asyncio.run(exercise())
    assert calls == [raw]


def test_collisions_rejected_before_mount(boundary):
    _, planner = boundary
    leaf = FastMCP("ambiguous")
    leaf.tool(name="io_load")(lambda: "first")
    leaf.tool(name="load")(lambda: "second")
    with pytest.raises(ValueError, match="collision"):
        planner.prepare_mount(leaf, "io")
