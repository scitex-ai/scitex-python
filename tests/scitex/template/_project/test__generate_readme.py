#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__generate_readme.py
"""Tests for scitex.template._project._generate_readme."""

import pytest

from scitex.template._project._generate_readme import (
    create_minimal_readme,
    create_project_readme,
)


@pytest.fixture
def metadata():
    return {
        "name": "My Research",
        "created_at": "2026-01-15",
        "owner": "jdoe",
        "owner_full_name": "Jane Doe",
        "description": "A test project",
        "hypotheses": "H1: X > Y",
        "progress": 75,
        "id": 42,
        "updated_at": "2026-02-01",
    }


class TestCreateMinimalReadme:
    def test_creates_file(self, tmp_path, metadata):
        out = create_minimal_readme(str(tmp_path), metadata)
        assert out.exists()
        assert out.name == "README.md"

    def test_contains_project_name(self, tmp_path, metadata):
        out = create_minimal_readme(str(tmp_path), metadata)
        content = out.read_text()
        assert "# My Research" in content

    def test_contains_owner(self, tmp_path, metadata):
        out = create_minimal_readme(str(tmp_path), metadata)
        content = out.read_text()
        assert "Jane Doe" in content


class TestCreateProjectReadme:
    def test_creates_file(self, tmp_path, metadata):
        out = create_project_readme(str(tmp_path), metadata)
        assert out.exists()

    def test_contains_hypotheses(self, tmp_path, metadata):
        out = create_project_readme(str(tmp_path), metadata)
        content = out.read_text()
        assert "H1: X > Y" in content

    def test_contains_progress(self, tmp_path, metadata):
        out = create_project_readme(str(tmp_path), metadata)
        content = out.read_text()
        assert "75%" in content

    def test_contains_project_id(self, tmp_path, metadata):
        out = create_project_readme(str(tmp_path), metadata)
        content = out.read_text()
        assert "42" in content


# EOF
