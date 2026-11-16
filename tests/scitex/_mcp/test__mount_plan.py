"""Real protocol coverage for the shared mount boundary, without peer imports."""

import asyncio
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
from fastmcp import Client, FastMCP
from fastmcp.server.middleware import Middleware


@pytest.fixture
def boundary():
    # Load only the boundary: importing the umbrella discovers every installed
    # peer and is intentionally a separate integration scope.
    name = "_scitex_mount_contract"
    package = ModuleType(name)
    package.__path__ = [str(Path(__file__).parents[3] / "src/scitex/_mcp")]
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


@pytest.fixture(
    params=[
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
def protocol_outcome(boundary, request):
    namespace, raw, expected = request.param
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
            schema = getattr(tools[0], "input_schema", None)
            if schema is None:
                schema = tools[0].inputSchema
            result = await client.call_tool(expected, {"value": "ok"})
            prompts = await client.list_prompts()
            resources = await client.list_resources()
            resource_text = (await client.read_resource(resources[0].uri))[0].text
        async with Client(leaf) as client:
            original_names = [tool.name for tool in await client.list_tools()]
        return {
            "expected": expected,
            "namespace": namespace,
            "raw": raw,
            "names": [tool.name for tool in tools],
            "schema": schema,
            "call_error": result.is_error,
            "content": result.content[0].text,
            "prompts": [prompt.name for prompt in prompts],
            "resource_uri": str(resources[0].uri),
            "resource_text": resource_text,
            "original_names": original_names,
            "middleware": calls,
        }

    return asyncio.run(exercise())


def test_public_tool_name(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["names"]
    # Assert
    assert observed == [outcome["expected"]]


def test_input_schema_retained(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["schema"]["properties"]["value"]["type"]
    # Assert
    assert observed == "string"


def test_mounted_call_succeeds(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["call_error"]
    # Assert
    assert observed is False


def test_callback_result_retained(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["content"]
    # Assert
    assert observed == "ok"


def test_prompt_namespace_retained(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["prompts"]
    # Assert
    assert observed == [outcome["namespace"] + "_help_me"]


def test_resource_namespace_retained(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["resource_uri"]
    # Assert
    assert observed == "fixture://" + outcome["namespace"] + "/text"


def test_resource_read_retained(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["resource_text"]
    # Assert
    assert observed == "resource retained"


def test_leaf_names_unchanged(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["original_names"]
    # Assert
    assert observed == [outcome["raw"]]


def test_leaf_middleware_retained(protocol_outcome):
    # Arrange
    outcome = protocol_outcome
    # Act
    observed = outcome["middleware"]
    # Assert
    assert observed == [outcome["raw"]]


def test_collisions_rejected_before_mount(boundary):
    # Arrange
    _, planner = boundary
    leaf = FastMCP("ambiguous")
    leaf.tool(name="io_load")(lambda: "first")
    leaf.tool(name="load")(lambda: "second")
    # Act
    # Assert
    with pytest.raises(ValueError, match="collision"):
        planner.prepare_mount(leaf, "io")
