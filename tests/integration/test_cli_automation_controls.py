"""Automation flags preserve preview and explicit local-write behavior."""

from click.testing import CliRunner

from scitex.cli.completion import completion
from scitex.cli.config import config


def test_config_preview_and_explicit_creation_accept_yes(tmp_path, monkeypatch):
    target = tmp_path / "scitex"
    monkeypatch.setenv("SCITEX_DIR", str(target))
    runner = CliRunner()
    preview = runner.invoke(config, ["init", "--dry-run", "--yes"])
    assert preview.exit_code == 0, preview.output
    assert "Would create" in preview.output
    assert not target.exists()
    created = runner.invoke(config, ["init", "--yes"])
    assert created.exit_code == 0, created.output
    assert (target / "logs").is_dir()
    assert (target / "scholar" / "library").is_dir()


def test_completion_preview_and_idempotent_install_accept_yes(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    rc = tmp_path / ".bashrc"
    original = "# Existing user settings\n"
    rc.write_text(original)
    args = ["install", "--shell", "bash", "--yes"]
    preview = runner.invoke(completion, [*args, "--dry-run"])
    assert preview.exit_code == 0, preview.output
    assert "_SCITEX_COMPLETE=bash_source" in preview.output
    assert rc.read_text() == original
    installed = runner.invoke(completion, args)
    assert installed.exit_code == 0, installed.output
    contents = rc.read_text()
    assert contents.startswith(original)
    assert "_SCITEX_COMPLETE=bash_source" in contents
    repeated = runner.invoke(completion, args)
    assert repeated.exit_code == 0, repeated.output
    assert rc.read_text() == contents
