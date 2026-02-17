#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__generate_configs.py
"""Tests for scitex.template._project._generate_configs."""

import json

import pytest

from scitex.template._project._generate_configs import (
    create_env_template,
    create_paths_config,
    create_project_config,
    create_requirements_file,
)


@pytest.fixture
def metadata():
    return {
        "name": "Test Project",
        "id": 42,
        "description": "Testing configs",
        "created_at": "2026-01-01",
        "owner": "jdoe",
        "progress": 50,
        "hypotheses": "H1: X causes Y",
    }


class TestCreateProjectConfig:
    def test_creates_config_file(self, tmp_path, metadata):
        out = create_project_config(str(tmp_path), metadata)
        assert out.exists()
        assert out.parent.name == "config"

    def test_json_fallback(self, tmp_path, metadata):
        out = create_project_config(str(tmp_path), metadata)
        if out.suffix == ".json":
            data = json.loads(out.read_text())
            assert data["project"]["name"] == "Test Project"

    def test_creates_config_dir(self, tmp_path, metadata):
        create_project_config(str(tmp_path), metadata)
        assert (tmp_path / "config").is_dir()


class TestCreatePathsConfig:
    def test_creates_paths_json(self, tmp_path):
        out = create_paths_config(str(tmp_path))
        assert out.name == "paths.json"
        data = json.loads(out.read_text())
        assert "data" in data
        assert "scripts" in data

    def test_uses_absolute_paths(self, tmp_path):
        out = create_paths_config(str(tmp_path))
        data = json.loads(out.read_text())
        assert str(tmp_path) in data["scripts"]


class TestCreateEnvTemplate:
    def test_creates_env_template(self, tmp_path, metadata):
        out = create_env_template(str(tmp_path), metadata)
        assert out.name == ".env.template"
        content = out.read_text()
        assert "Test Project" in content
        assert "42" in content


class TestCreateRequirementsFile:
    def test_creates_requirements(self, tmp_path):
        out = create_requirements_file(str(tmp_path))
        assert out.name == "requirements.txt"
        content = out.read_text()
        assert "numpy" in content
        assert "pandas" in content


# EOF
