"""The umbrella owns its audit noun without weakening action requirements."""

from importlib.resources import files

import click
import yaml

from scitex_dev._cli.audit._summary._audit import (
    _check_universal_flags,
    _classify,
)
from scitex_dev._cli.audit._summary._dict_root import use_owner_dict


def test_packaged_audit_vocabulary_classifies_the_facility_as_a_noun():
    # Arrange
    resource = files("scitex").joinpath("_cli_audit_dict.yaml")
    # Act
    payload = resource.read_bytes()
    with use_owner_dict(resource, "scitex", "canonical source resource", payload):
        observed = _classify("audit")
    # Assert
    assert yaml.safe_load(payload) == {"nouns": ["audit"]}
    assert observed == {"noun"}


def test_audit_vocabulary_keeps_mutation_consent_and_preview_requirements():
    # Arrange
    resource = files("scitex").joinpath("_cli_audit_dict.yaml")
    command = click.Command("delete", callback=lambda: None)
    findings = []
    # Act
    with use_owner_dict(resource, "scitex", "canonical source resource",
                        resource.read_bytes()):
        _check_universal_flags(command, "scitex delete", False, findings)
    # Assert
    messages = [finding.message for finding in findings]
    assert any("--yes" in message for message in messages)
    assert any("--dry-run" in message for message in messages)


def test_umbrella_audit_noun_is_not_borrowed_by_a_foreign_owner():
    # Arrange
    resource = files("scitex").joinpath("_cli_audit_dict.yaml")
    # Act
    with use_owner_dict(resource, "scitex", "canonical source resource",
                        resource.read_bytes()):
        own_labels = _classify("audit")
        with use_owner_dict(None, "unrelated-owner", "no owned dictionary"):
            foreign_labels = _classify("audit")
    # Assert
    assert own_labels == {"noun"}
    assert "noun" not in foreign_labels
