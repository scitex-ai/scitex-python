#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__customize.py
"""Tests for scitex.template._project._customize."""

import pytest

from scitex.template._project._customize import (
    customize_minimal_template,
    customize_template,
)


@pytest.fixture
def project_dir(tmp_path):
    """Create a fake project directory with template files."""
    (tmp_path / "README.md").write_text(
        "# SciTeX Example Research Project\nThis is an example research project"
    )
    paper = tmp_path / "paper" / "manuscript" / "src"
    paper.mkdir(parents=True)
    (paper / "title.tex").write_text("\\title{Template Title}")
    (paper / "authors.tex").write_text("\\author{Template Author}")
    return str(tmp_path)


@pytest.fixture
def minimal_dir(tmp_path):
    """Create a fake minimal template directory."""
    shared = tmp_path / "scitex" / "writer" / "00_shared"
    shared.mkdir(parents=True)
    (shared / "title.tex").write_text("\\title{Placeholder}")
    (shared / "authors.tex").write_text("\\author{Placeholder}")
    return str(tmp_path)


@pytest.fixture
def metadata():
    return {
        "name": "My Research",
        "description": "A test project",
        "owner": "jdoe",
        "owner_full_name": "Jane Doe",
    }


class TestCustomizeTemplate:
    def test_updates_readme(self, project_dir, metadata):
        customize_template(project_dir, metadata)
        import pathlib

        readme = (pathlib.Path(project_dir) / "README.md").read_text()
        assert "# My Research" in readme
        assert "A test project" in readme

    def test_updates_title_tex(self, project_dir, metadata):
        customize_template(project_dir, metadata)
        import pathlib

        title = (
            pathlib.Path(project_dir) / "paper" / "manuscript" / "src" / "title.tex"
        ).read_text()
        assert "My Research" in title

    def test_updates_authors_tex(self, project_dir, metadata):
        customize_template(project_dir, metadata)
        import pathlib

        authors = (
            pathlib.Path(project_dir) / "paper" / "manuscript" / "src" / "authors.tex"
        ).read_text()
        assert "Jane Doe" in authors

    def test_missing_files_no_error(self, tmp_path, metadata):
        customize_template(str(tmp_path), metadata)


class TestCustomizeMinimalTemplate:
    def test_updates_title(self, minimal_dir, metadata):
        customize_minimal_template(minimal_dir, metadata)
        import pathlib

        title = (
            pathlib.Path(minimal_dir) / "scitex" / "writer" / "00_shared" / "title.tex"
        ).read_text()
        assert "My Research" in title

    def test_updates_author(self, minimal_dir, metadata):
        customize_minimal_template(minimal_dir, metadata)
        import pathlib

        authors = (
            pathlib.Path(minimal_dir)
            / "scitex"
            / "writer"
            / "00_shared"
            / "authors.tex"
        ).read_text()
        assert "Jane Doe" in authors

    def test_uses_username_fallback(self, minimal_dir):
        customize_minimal_template(minimal_dir, {"name": "Test", "owner": "jdoe"})
        import pathlib

        authors = (
            pathlib.Path(minimal_dir)
            / "scitex"
            / "writer"
            / "00_shared"
            / "authors.tex"
        ).read_text()
        assert "jdoe" in authors


# EOF
