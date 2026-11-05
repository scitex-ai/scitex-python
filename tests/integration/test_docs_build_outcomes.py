"""The umbrella must propagate failure results returned by its docs provider."""

import json

import pytest
from click.testing import CliRunner

from scitex.cli.docs import docs


@pytest.mark.parametrize(
    "provider_result",
    [
        {"example": {"error": "No Sphinx source found"}},
        {"example": {"html": {"error": "Sphinx returned 2"}}},
    ],
)
@pytest.mark.parametrize("as_json", [False, True])
def test_docs_provider_failures_are_not_reported_as_success(
    monkeypatch, provider_result, as_json
):
    import scitex_dev as provider

    monkeypatch.setattr(provider, "build_docs", lambda **kwargs: provider_result)
    args = ["build", "--package", "example", "--yes"]
    if as_json:
        args.append("--json")
    result = CliRunner().invoke(docs, args)
    assert result.exit_code == 1, result.output
    if as_json:
        envelope = json.loads(result.stdout)
        assert envelope["success"] is False
        assert envelope["data"] == provider_result
        assert envelope["error"]
    else:
        assert "built" not in result.stdout
        assert "example" in result.stdout


def test_docs_build_preview_accepts_yes_without_calling_builder(monkeypatch):
    import scitex_dev as provider

    def forbidden_build(**kwargs):
        pytest.fail("preview invoked a real documentation build")

    monkeypatch.setattr(provider, "build_docs", forbidden_build)
    result = CliRunner().invoke(
        docs, ["build", "--package", "example", "--dry-run", "--yes", "--json"]
    )
    assert result.exit_code == 0, result.output
    envelope = json.loads(result.stdout)
    assert envelope["success"] is True
    assert envelope["data"]["packages"] == ["example"]
    assert envelope["data"]["action"] == "dry_run"


def test_unknown_docs_provider_returns_structured_failure():
    result = CliRunner().invoke(
        docs,
        ["build", "--package", "scitex-test-nonexistent-provider", "--yes", "--json"],
    )
    assert result.exit_code == 1, result.output
    envelope = json.loads(result.stdout)
    assert envelope["success"] is False
    assert "scitex-test-nonexistent-provider" in envelope["error"]


def test_successful_docs_provider_keeps_success_envelope(monkeypatch):
    import scitex_dev as provider

    outcome = {"example": {"html": "/owned/example/index.html"}}
    monkeypatch.setattr(provider, "build_docs", lambda **kwargs: outcome)
    result = CliRunner().invoke(docs, ["build", "--package", "example", "--json"])
    assert result.exit_code == 0, result.output
    envelope = json.loads(result.stdout)
    assert envelope["success"] is True
    assert envelope["data"] == outcome
