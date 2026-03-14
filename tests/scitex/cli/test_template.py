#!/usr/bin/env python3
"""Tests for scitex.cli.template - Project template scaffolding CLI commands."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.template import template


class TestTemplateGroup:
    """Tests for the template command group."""

    def test_template_help(self):
        """Test that template help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(template, ["--help"])
        assert result.exit_code == 0
        assert "Project template scaffolding" in result.output

    def test_template_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(template, ["--help"])
        expected_commands = ["list", "clone", "info"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in template help"


class TestTemplateList:
    """Tests for the template list command."""

    def test_list_default(self):
        """Test list command with default options."""
        runner = CliRunner()
        with patch("scitex.template.get_available_templates_info") as mock_info:
            mock_info.return_value = [
                {
                    "id": "research",
                    "name": "Research Project",
                    "description": "Scientific research template",
                    "use_case": "Research workflows",
                    "github_url": "https://github.com/example/research",
                    "features": ["scripts", "data", "docs"],
                },
                {
                    "id": "pip-project",
                    "name": "Pip Package",
                    "description": "Python package template",
                    "use_case": "Python packages",
                    "github_url": "https://github.com/example/pip",
                    "features": ["src", "tests"],
                },
            ]
            result = runner.invoke(template, ["list"])
            assert result.exit_code == 0
            assert "Available" in result.output or "Template" in result.output

    def test_list_json(self):
        """Test list command with --json flag."""
        runner = CliRunner()
        with patch("scitex.template.get_available_templates_info") as mock_info:
            mock_info.return_value = [
                {"id": "research", "name": "Research Project"},
            ]
            result = runner.invoke(template, ["list", "--json"])
            assert result.exit_code == 0
            output = json.loads(result.output)
            data = output.get("data", output)
            assert isinstance(data, list)
            assert len(data) > 0

    def test_list_empty(self):
        """Test list command when no templates available."""
        runner = CliRunner()
        with patch("scitex.template.get_available_templates_info") as mock_info:
            mock_info.return_value = []
            result = runner.invoke(template, ["list"])
            assert result.exit_code == 0


class TestTemplateClone:
    """Tests for the template clone command."""

    def test_clone_research(self):
        """Test clone command with research template."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "my_project")
            with patch("scitex.template.clone_research") as mock_clone:
                mock_clone.return_value = Path(output_path)
                result = runner.invoke(template, ["clone", "research", output_path])
                assert result.exit_code == 0
                assert (
                    "Successfully cloned" in result.output
                    or "cloned" in result.output.lower()
                )
                mock_clone.assert_called_once()

    def test_clone_pip_project(self):
        """Test clone command with pip-project template."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "my_package")
            with patch("scitex.template.clone_pip_project") as mock_clone:
                mock_clone.return_value = Path(output_path)
                result = runner.invoke(template, ["clone", "pip-project", output_path])
                assert result.exit_code == 0
                mock_clone.assert_called_once()

    def test_clone_with_git_strategy(self):
        """Test clone command with git strategy."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "custom_name")
            with patch("scitex.template.clone_research") as mock_clone:
                mock_clone.return_value = Path(output_path)
                result = runner.invoke(
                    template,
                    [
                        "clone",
                        "research",
                        output_path,
                        "--git-strategy",
                        "parent",
                    ],
                )
                assert result.exit_code == 0

    def test_clone_invalid_template(self):
        """Test clone command with invalid template type."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(template, ["clone", "invalid_type", tmpdir])
            assert result.exit_code != 0

    def test_clone_error_handling(self):
        """Test clone command handles errors."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "project")
            with patch("scitex.template.clone_research") as mock_clone:
                mock_clone.side_effect = Exception("Clone failed")
                result = runner.invoke(template, ["clone", "research", output_path])
                assert result.exit_code == 1
                assert "Error" in result.output


class TestTemplateInfo:
    """Tests for the template info command."""

    def test_info_research(self):
        """Test info command for research template."""
        runner = CliRunner()
        with patch("scitex.template.get_available_templates_info") as mock_info:
            mock_info.return_value = [
                {
                    "id": "research",
                    "name": "Research Project",
                    "description": "Scientific research template",
                    "use_case": "Research workflows",
                    "github_url": "https://github.com/example/research",
                    "features": ["src/", "tests/", "docs/"],
                },
            ]
            result = runner.invoke(template, ["info", "research"])
            assert result.exit_code == 0
            assert "Research" in result.output or "research" in result.output

    def test_info_invalid_template(self):
        """Test info command with invalid template."""
        runner = CliRunner()
        with patch("scitex.template.get_available_templates_info") as mock_info:
            mock_info.return_value = [
                {"id": "research", "name": "Research"},
                {"id": "pip-project", "name": "Pip"},
            ]
            result = runner.invoke(template, ["info", "nonexistent"])
            assert result.exit_code == 1
            assert "not found" in result.output.lower()


class TestTemplateGet:
    """Tests for the template get command."""

    def test_get_session(self):
        """Test get command for session template."""
        runner = CliRunner()
        result = runner.invoke(template, ["get", "session"])
        assert result.exit_code == 0
        assert "@stx.session" in result.output

    def test_get_io(self):
        """Test get command for io template."""
        runner = CliRunner()
        result = runner.invoke(template, ["get", "io"])
        assert result.exit_code == 0
        assert "stx.io" in result.output

    def test_get_all(self):
        """Test get command for all templates combined."""
        runner = CliRunner()
        result = runner.invoke(template, ["get", "all"])
        assert result.exit_code == 0
        assert "SCITEX CODE TEMPLATES" in result.output

    def test_get_module_usage_templates(self):
        """Test get command for module usage templates."""
        runner = CliRunner()
        for template_id in [
            "plt",
            "stats",
            "scholar",
            "audio",
            "capture",
            "diagram",
            "canvas",
            "writer",
        ]:
            result = runner.invoke(template, ["get", template_id])
            assert result.exit_code == 0, f"Failed for template: {template_id}"

    def test_get_with_output_file(self):
        """Test get command with output file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "script.py")
            result = runner.invoke(template, ["get", "session", "-o", output_path])
            assert result.exit_code == 0
            assert os.path.exists(output_path)
            with open(output_path) as f:
                content = f.read()
            assert "@stx.session" in content

    def test_get_with_docstring(self):
        """Test get command with custom docstring."""
        runner = CliRunner()
        result = runner.invoke(template, ["get", "session", "-d", "Custom description"])
        assert result.exit_code == 0
        assert "Custom description" in result.output

    def test_get_invalid_template(self):
        """Test get command with invalid template."""
        runner = CliRunner()
        result = runner.invoke(template, ["get", "nonexistent"])
        assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
