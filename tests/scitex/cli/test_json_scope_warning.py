"""Regression test for scitex-python#211 — top-level --json warning."""

from __future__ import annotations

import subprocess


class TestTopLevelJsonScope:
    def test_bare_json_emits_structured_output(self):
        """`scitex --json` (no subcommand) still emits the JSON command listing."""
        r = subprocess.run(
            ["scitex", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0
        # Must be parseable JSON starting with the Result envelope
        assert '"success"' in r.stdout
        assert '"commands"' in r.stdout

    def test_json_with_subcommand_emits_stderr_warning(self):
        """`scitex --json config list` → subcommand runs, stderr has warning."""
        r = subprocess.run(
            ["scitex", "--json", "config", "list"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # stderr contains the scope-hint warning
        assert "top-level --json does not propagate" in r.stderr
        # stdout is plain text (not JSON), as documented
        assert "SciTeX Configuration" in r.stdout

    def test_subcommand_json_works(self):
        """`scitex config list --json` emits JSON output correctly."""
        r = subprocess.run(
            ["scitex", "config", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0
        # No warning on stderr
        assert "top-level --json does not propagate" not in r.stderr
        # stdout starts with a JSON object
        assert r.stdout.lstrip().startswith("{")


# EOF
