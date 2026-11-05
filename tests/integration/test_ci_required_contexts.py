"""Required checks must relay the real full matrix without rerunning tests."""

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
VERSIONS = ["3.11", "3.12", "3.13"]


def workflow():
    return yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())


def test_required_context_names_and_full_matrix_are_preserved():
    jobs = workflow()["jobs"]
    matrix = jobs["pytest-matrix"]
    assert (
        matrix["uses"] == "scitex-ai/.github/.github/workflows/pytest-matrix.yml@main"
    )
    assert json.loads(matrix["with"]["full_python_versions"]) == VERSIONS
    assert matrix["with"]["ordinary_pr_python"] == ""
    relay = jobs["required-test-contexts"]
    versions = relay["strategy"]["matrix"]["python-version"]
    assert versions == VERSIONS
    assert {
        relay["name"].replace("${{ matrix.python-version }}", version)
        for version in versions
    } == {f"pytest-matrix-on-ubuntu-py{version}" for version in VERSIONS}
    assert relay["needs"] == ["pytest-matrix"]
    assert relay["if"] == "${{ always() }}"
    assert relay["permissions"] == {}
    assert relay["steps"][0]["env"] == {
        "FULL_MATRIX_RESULT": "${{ needs.pytest-matrix.result }}"
    }
    assert all("uses" not in step for step in relay["steps"])


@pytest.mark.parametrize(
    "result", ["success", "failure", "cancelled", "skipped", "", "unknown"]
)
def test_actual_required_context_script_fails_closed(tmp_path, result):
    script = workflow()["jobs"]["required-test-contexts"]["steps"][0]["run"]
    completed = subprocess.run(
        ["bash", "-c", script],
        cwd=tmp_path,
        env={"PATH": os.defpath, "FULL_MATRIX_RESULT": result},
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert (completed.returncode == 0) == (result == "success")


def test_duplicate_runners_no_longer_replace_failed_full_installs():
    for name in [
        "pytest-matrix-on-ubuntu-py3-11-3-12-3-13.yml",
        "import-smoke-on-ubuntu-py3-12.yml",
        "rtd-sphinx-build-on-ubuntu-latest.yml",
    ]:
        assert not (ROOT / ".github/workflows" / name).exists()


def test_shared_docs_workflow_keeps_generated_bundle_publication():
    """Replacing build-and-publish with build-only would freeze editable docs."""
    docs = workflow()["jobs"]["rtd-sphinx-build"]
    assert docs["uses"] == "scitex-ai/.github/.github/workflows/rtd-sphinx-build.yml@main"
    assert docs["with"]["bundle_dir"] == "src/scitex/_sphinx_html"
    assert docs["permissions"] == {"contents": "write", "pull-requests": "write"}
    legacy_url = ROOT / "docs/sphinx/source/installation.rst"
    assert legacy_url.read_text().strip() == ".. include:: ../installation.rst"
