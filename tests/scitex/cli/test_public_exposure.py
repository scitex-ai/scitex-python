"""Black-box namespace contracts using real metadata and real Click commands.

Children use the current source with the actual installed peer distributions.
No real business callbacks, network calls or unapproved processes are allowed.
Synthetic console invocation is explicit; incidental writes stay in owned home.
Umbrella bootstrap is separate from peer module execution during discovery.
"""

import importlib.util
import json
from pathlib import Path

import pytest

_HELPER_SPEC = importlib.util.spec_from_file_location(
    "_scitex_cli_public_exposure_helpers",
    Path(__file__).with_name("_public_exposure_helpers.py"),
)
_HELPERS = importlib.util.module_from_spec(_HELPER_SPEC)
_HELPER_SPEC.loader.exec_module(_HELPERS)
_probe = _HELPERS._probe
installed_parser = _HELPERS.installed_parser

_MOVED = {
    "completion",
    "introspect",
    "linter",
    "list-python-apis",
    "pkg",
    "skills",
    "audit",
}
_HIDDEN = {
    "app",
    "ui",
    "orochi",
    "notify",
    "todo",
    "verify",
    "tunnel",
    "events",
    "socialia",
}
_PYTHON_ONLY = {"compat", "decorators", "dict", "types", "dsp", "nn", "linalg", "math"}
_PEERS = (
    "scitex_cards",
    "scitex_clew",
    "scitex_sdk",
    "scitex_ssh",
    "scitex_scholar",
    "scitex_writer",
    "figrecipe",
    "socialia",
)

_DEV_PEERS = set("capture security newb resource template git benchmark".split())


def _command_rows(text):
    """Parse command rows, excluding examples and narrative text."""
    import re

    return set(re.findall(r"^  ([a-z][a-z0-9-]*)\s{2,}\S", text, re.MULTILINE))


@pytest.mark.parametrize("mode", ["help", "json", "completion"])
def test_normal_discovery_executes_no_peer_code_after_bootstrap(tmp_path, mode):
    # Arrange
    request = {"args": ["--json"] if mode == "json" else ["--help"], "peers": _PEERS}
    if mode == "completion":
        request = {"args": [], "complete": "scitex ", "peers": _PEERS}
    # Act
    result = _probe(tmp_path, "invoke", request)
    # Assert
    assert (result["code"], result["peer_imports"]) == (0, [])


@pytest.mark.parametrize("mode", ["help", "json", "completion"])
def test_normal_root_discovery_has_only_public_names(tmp_path, mode):
    # Arrange
    request = {"args": ["--json"] if mode == "json" else ["--help"]}
    if mode == "completion":
        request = {"args": [], "complete": "scitex "}
    # Act
    result = _probe(tmp_path, "invoke", request)
    if mode == "json":
        names = set(json.loads(result["stdout"])["data"]["commands"])
    elif mode == "completion":
        names = {
            line.split(",", 1)[1]
            for line in result["stdout"].splitlines()
            if line.startswith("plain,")
        }
    else:
        names = _command_rows(result["stdout"])
    # Assert
    assert (
        {"sdk", "cards", "clew", "ssh", "dev"} <= names,
        names & (_HIDDEN | _MOVED | _PYTHON_ONLY | _DEV_PEERS),
    ) == (True, set())


@pytest.mark.parametrize("name", sorted(_MOVED))
def test_moved_developer_paths_have_real_help(tmp_path, name):
    # Arrange
    request = {"args": ["dev", name, "--help"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    # Assert
    assert (result["code"], "Usage:" in result["stdout"]) == (0, True), result


def test_developer_help_lists_moved_workflows(tmp_path):
    # Arrange
    request = {"args": ["dev", "--help"], "developer_metadata": True}
    # Act
    result = _probe(tmp_path, "invoke", request)
    # Assert
    assert (_MOVED | set(result["declared_dev_peers"])) <= _command_rows(
        result["stdout"]
    ), result


def test_canonical_groups_are_actual_owner_objects_without_owner_mutation(tmp_path):
    # Arrange
    operation = "owners"
    # Act
    result = _probe(tmp_path, operation)
    # Assert
    assert (
        all(result["same"].values()),
        result["owner_unchanged"],
        result["retired_imports"],
    ) == (True, True, [])


@pytest.mark.parametrize("component", ["app", "ui"])
def test_sdk_component_help_uses_canonical_path(tmp_path, component):
    # Arrange
    request = {"args": ["sdk", component, "--help"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    # Assert
    assert (result["code"], "Usage:" in result["stdout"]) == (0, True), result


def test_ssh_tunnel_is_a_real_subgroup(tmp_path):
    # Arrange
    request = {"args": ["ssh", "tunnel", "--help"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    # Assert
    assert (
        result["code"],
        {"setup", "remove", "check-status"} <= _command_rows(result["stdout"]),
    ) == (0, True), result


def test_tuple_alias_preserves_arguments_output_and_exit_status(tmp_path):
    # Arrange
    operation = "tuple-alias"
    # Act
    result = _probe(tmp_path, operation)
    # Assert
    assert (
        result["code"],
        json.loads(result["stdout"]),
        result["hidden"],
        "canonical echo-value" in result["stderr"],
    ) == (7, {"value": "owned value", "label": "owned label"}, True, True)


def test_python_only_utilities_remain_public(tmp_path, record_property):
    # Arrange
    operation = "python"
    # Act
    result = _probe(tmp_path, operation)
    record_property("missing_optional_python_owners", result["missing_owners"])
    # Assert
    assert result["public"] == {
        "dict": True,
        "compat": True,
        "types": True,
        "decorators": True,
    }


@pytest.mark.parametrize("component", ["app", "ui"])
def test_hidden_sdk_alias_help_preserves_the_component_tree(tmp_path, component):
    # Arrange
    canonical_home = tmp_path / "canonical"
    canonical_home.mkdir()
    legacy_home = tmp_path / "legacy"
    legacy_home.mkdir()
    canonical = _probe(canonical_home, "invoke", {"args": ["sdk", component, "--help"]})
    # Act
    alias = _probe(legacy_home, "invoke", {"args": [component, "--help"]})
    # Assert
    assert (canonical["code"], alias["code"], _command_rows(alias["stdout"])) == (
        0,
        0,
        _command_rows(canonical["stdout"]),
    ), alias


@pytest.mark.parametrize("args", [["--help"], ["--json"]])
def test_declared_console_discovery_does_not_import_or_call_launcher(
    tmp_path, installed_parser, args
):
    # Arrange
    site, imported, called = installed_parser
    # Act
    result = _probe(tmp_path, "invoke", {"args": args, "fixture_site": str(site)})
    # Assert
    assert (
        result["code"],
        imported.exists(),
        called.exists(),
        "owned-parser" in result["stdout"],
    ) == (0, False, False, True)


def test_explicit_declared_parser_help_runs_only_on_invocation(
    tmp_path, installed_parser
):
    # Arrange
    site, imported, called = installed_parser
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {
            "args": ["owned-parser", "--help"],
            "fixture_site": str(site),
            "allow_owned_console": True,
        },
    )
    # Assert
    assert (
        result["code"],
        imported.exists(),
        called.exists(),
        "Owned parser fixture" in result["stdout"],
    ) == (0, True, True, True), result


def test_explicit_declared_parser_preserves_output_and_exit(tmp_path, installed_parser):
    # Arrange
    site, _imported, called = installed_parser
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {
            "args": ["owned-parser", "--value", "owned argument", "--exit-code", "7"],
            "fixture_site": str(site),
            "allow_owned_console": True,
        },
    )
    # Assert
    assert (result["code"], json.loads(result["stdout"]), called.exists()) == (
        7,
        {"value": "owned argument"},
        True,
    )


def test_explicit_leaf_decline_blocks_an_existing_umbrella_wrapper(
    tmp_path, installed_parser
):
    # Arrange
    site, imported, called = installed_parser
    entries = site / "scitex_owned_parser-1.0.dist-info" / "entry_points.txt"
    entries.write_text(
        "[console_scripts]\nscitex-owned-parser = owned_parser:main\n"
        "[scitex.cli]\nevent = none\n"
    )
    # Act
    result = _probe(tmp_path, "invoke", {"args": ["--json"], "fixture_site": str(site)})
    names = set(json.loads(result["stdout"])["data"]["commands"])
    # Assert
    assert (
        "event" in names,
        "owned-parser" in names,
        imported.exists(),
        called.exists(),
    ) == (False, False, False, False)


def test_declared_dotted_click_target_help_never_calls_business_callback(
    tmp_path, installed_parser
):
    # Arrange
    site, _imported, called = installed_parser
    (site / "owned_parser.py").write_text(
        "import click\nfrom pathlib import Path\n"
        "class Holder:\n    pass\n"
        "@click.group(help='Owned dotted command')\n"
        "def command():\n"
        f"    Path({str(called)!r}).touch()\n"
        "    raise AssertionError('business callback must not execute')\n"
        "Holder.command=command\n"
    )
    (site / "scitex_owned_parser-1.0.dist-info" / "entry_points.txt").write_text(
        "[console_scripts]\nscitex-owned-parser = owned_parser:Holder.command\n"
        "[scitex.cli]\nowned-parser = owned_parser:Holder.command\n"
    )
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {"args": ["owned-parser", "--help"], "fixture_site": str(site)},
    )
    # Assert
    assert (
        result["code"],
        "Owned dotted command" in result["stdout"],
        called.exists(),
    ) == (0, True, False), result


@pytest.mark.parametrize("name", ["skills", "linter"])
@pytest.mark.parametrize("prefix", [["dev"], [], ["dev", "dev"]])
def test_explicit_decline_cannot_be_bypassed_by_developer_aliases(
    tmp_path, installed_parser, name, prefix
):
    # Arrange
    site, imported, called = installed_parser
    (site / "scitex_owned_parser-1.0.dist-info" / "entry_points.txt").write_text(
        f"[scitex.cli]\n{name} = none\n"
    )
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {"args": [*prefix, name, "--help"], "fixture_site": str(site)},
    )
    # Assert
    assert (result["code"] != 0, imported.exists(), called.exists()) == (
        True,
        False,
        False,
    ), result


def test_explicit_ui_decline_blocks_old_alias_but_preserves_sdk_mount(
    tmp_path, installed_parser
):
    # Arrange
    site, imported, called = installed_parser
    (site / "scitex_owned_parser-1.0.dist-info" / "entry_points.txt").write_text(
        "[scitex.cli]\nui = none\n"
    )
    old = _probe(
        tmp_path, "invoke", {"args": ["ui", "--help"], "fixture_site": str(site)}
    )
    # Act
    canonical = _probe(
        tmp_path, "invoke", {"args": ["sdk", "ui", "--help"], "fixture_site": str(site)}
    )
    # Assert
    assert (
        old["code"] != 0,
        canonical["code"],
        imported.exists(),
        called.exists(),
    ) == (True, 0, False, False), (old, canonical)


@pytest.mark.parametrize("name", ["install-shell-completion", "install-tab-completion"])
def test_declined_completion_cannot_use_captured_owner_alias(
    tmp_path, installed_parser, name
):
    # Arrange
    site, imported, called = installed_parser
    (site / "scitex_owned_parser-1.0.dist-info" / "entry_points.txt").write_text(
        "[scitex.cli]\ninstall-shell-completion = none\n"
    )
    # Act
    result = _probe(
        tmp_path, "invoke", {"args": ["dev", name, "--help"], "fixture_site": str(site)}
    )
    # Assert
    assert (result["code"] != 0, imported.exists(), called.exists()) == (
        True,
        False,
        False,
    ), result


def test_legacy_double_dev_skills_still_resolves_effective_view(tmp_path):
    # Arrange
    request = {"args": ["dev", "dev", "skills", "--help"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    # Assert
    assert (result["code"], "Usage:" in result["stdout"]) == (0, True), result
