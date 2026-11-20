"""Browser CLI reads and previews cannot launch processes or write outputs."""

import json

import pytest

from tests.integration.test_readonly_cli_json import _invoke


@pytest.mark.parametrize("suffix", [".other", ".PDF"])
@pytest.mark.parametrize("accept", [[], ["--yes"]])
def test_pdf_export_preview_does_not_launch_or_write(tmp_path, accept, suffix):
    # Arrange
    target = tmp_path / "not-created" / ("page" + suffix)
    expected = target if suffix == ".PDF" else target.with_suffix(".pdf")
    # Act: the existing child guard rejects network, processes and writes.
    observed = _invoke(
        tmp_path,
        [
            "browser",
            ["save-as-pdf", "example.invalid", str(target), "--dry-run", *accept],
        ],
    )
    # Assert
    assert (
        observed["exit"],
        str(expected) in observed["stdout"],
        target.parent.exists(),
    ) == (0, True, False)


def test_browser_visibility_guidance_json_does_not_claim_control(tmp_path):
    # Arrange
    arguments = ["browser", ["show", "owned-session", "--json"]]
    # Act
    observed = _invoke(tmp_path, arguments)
    data = json.loads(observed["stdout"])["data"] if observed["exit"] == 0 else {}
    # Assert
    assert (
        observed["exit"],
        data.get("browser_id"),
        data.get("control_available"),
        bool(data.get("instructions")),
    ) == (0, "owned-session", False, True)
