"""CLI metadata accounting shares Dev's vendor-neutral measurement contract."""

from types import SimpleNamespace

from scitex.cli.mcp import _get_mcp_summary


def test_context_summary_keeps_unknown_token_counts_unknown():
    # Arrange
    server = SimpleNamespace(name="owned", instructions="fixture")
    tool = SimpleNamespace(name="owned", description="fixture", parameters={})
    # Act
    summary = _get_mcp_summary(server, {"owned": tool})
    # Assert
    assert all(
        summary[key] is None
        for key in (
            "instructions_tokens",
            "descriptions_tokens",
            "schemas_tokens",
            "total_context_tokens",
        )
    )


def test_context_summary_distinguishes_unicode_characters_from_utf8_bytes():
    # Arrange
    server = SimpleNamespace(name="owned", instructions="計測")
    # Act
    summary = _get_mcp_summary(server, {})
    # Assert
    assert summary["context_measurement"]["instructions_raw"] == {
        "characters": 2,
        "utf8_bytes": 6,
    }


def test_context_summary_does_not_infer_ownership_from_name_prefixes():
    # Arrange
    server = SimpleNamespace(name="owned", instructions="")
    tools = {
        name: SimpleNamespace(name=name, description="", parameters={})
        for name in ["stats_owned", "dev_owned"]
    }
    # Act
    report = _get_mcp_summary(server, tools)["context_measurement"]
    # Assert
    assert (
        set(report["packages"]),
        report["packages"]["unattributed"]["mcp_tools"],
        report["client_total_context"],
    ) == ({"unattributed"}, 2, "not_observed")


def test_context_summary_preserves_protocol_schema_metadata_without_calls():
    # Arrange
    from scitex_dev.context import measure_context

    server = SimpleNamespace(name="owned", instructions="fixture")
    schema = {"type": "object", "properties": {"value": {"type": "string"}}}
    output = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    tool = SimpleNamespace(
        name="owned", description="fixture", inputSchema=schema, outputSchema=output
    )
    expected = measure_context(
        tools=[
            {
                "name": "owned",
                "description": "fixture",
                "inputSchema": schema,
                "outputSchema": output,
            }
        ],
        instructions="fixture",
    )
    # Act
    actual = _get_mcp_summary(server, {"owned": tool})["context_measurement"]
    # Assert
    assert actual == expected
