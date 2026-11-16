"""Canonical developer inspection routes retain real behavior and policy."""

import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "_introspection_namespace_probes",
    Path(__file__).with_name("_public_exposure_helpers.py"),
)
_HELPERS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_HELPERS)
_probe = _HELPERS._probe
installed_parser = _HELPERS.installed_parser


def test_canonical_introspection_is_visible_and_old_verb_is_hidden(tmp_path):
    # Arrange
    request = {"args": ["dev", "--json"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    names = json.loads(result["stdout"])["data"]["commands"]
    # Assert
    assert (result["code"], "introspection" in names, "introspect" in names) == (
        0, True, False,
    )


def test_developer_completion_prefers_the_canonical_noun(tmp_path):
    # Arrange
    request = {"args": [], "complete": "scitex dev "}
    # Act
    result = _probe(tmp_path, "invoke", request)
    names = {line.partition(",")[2] for line in result["stdout"].splitlines()
             if line.startswith("plain,")}
    # Assert
    assert (result["code"], "introspection" in names, "introspect" in names) == (
        0, True, False,
    )


@pytest.mark.parametrize("prefix", [["dev", "introspect"], ["introspect"]])
def test_old_routes_warn_without_polluting_json_output(tmp_path, prefix):
    # Arrange
    request = {"args": [*prefix, "show-signature", "json.dumps", "--json"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    response = json.loads(result["stdout"])
    # Assert
    assert (result["code"], response["success"], "introspection" in result["stderr"]) == (
        0, True, True,
    )


@pytest.mark.parametrize("prefix", [
    ["dev", "introspection"], ["dev", "introspect"], ["introspect"],
])
def test_real_signature_operation_survives_canonical_and_legacy_routes(tmp_path, prefix):
    # Arrange
    request = {"args": [*prefix, "show-signature", "json.dumps", "--json"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    response = json.loads(result["stdout"])
    # Assert
    assert (result["code"], response["success"], "obj" in response["data"]["signature"]) == (
        0, True, True,
    )


@pytest.mark.parametrize("declined", ["introspect", "introspection"])
@pytest.mark.parametrize("prefix", [
    ["dev", "introspection"], ["dev", "introspect"], ["introspect"],
    ["dev", "dev", "introspect"],
])
def test_decline_covers_canonical_and_legacy_developer_routes(
    tmp_path, installed_parser, declined, prefix,
):
    # Arrange
    site, imported, called = installed_parser
    (site / "scitex_owned_parser-1.0.dist-info" / "entry_points.txt").write_text(
        f"[scitex.cli]\n{declined} = none\n"
    )
    # Act
    result = _probe(tmp_path, "invoke", {
        "args": [*prefix, "show-signature", "json.dumps", "--json"],
        "fixture_site": str(site),
    })
    # Assert
    assert (result["code"] != 0, imported.exists(), called.exists()) == (True, False, False)
