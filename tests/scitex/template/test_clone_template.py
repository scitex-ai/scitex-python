#!/usr/bin/env python3
# Timestamp: 2026-02-08
# File: tests/scitex/template/test_clone_template.py

"""Tests for the unified clone_template dispatcher."""

from unittest.mock import MagicMock, patch

import pytest

from scitex.template._project._clone_template import (
    ALIASES,
    TEMPLATES,
    clone_template,
    get_all_template_ids,
    get_template_ids,
)


class TestCloneTemplateDispatch:
    """Test that clone_template dispatches to correct functions."""

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_canonical_ids_dispatch(self, template_id):
        """Each canonical template ID dispatches to its function."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {template_id: mock_func}):
            result = clone_template(
                template_id=template_id,
                project_dir="/tmp/test-project",
            )
            assert result is True
            mock_func.assert_called_once_with(
                project_dir="/tmp/test-project",
                git_strategy="child",
                branch=None,
                tag=None,
            )

    @pytest.mark.parametrize(
        "alias,canonical",
        list(ALIASES.items()),
    )
    def test_aliases_resolve(self, alias, canonical):
        """Aliases resolve to canonical IDs."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {canonical: mock_func}):
            result = clone_template(
                template_id=alias,
                project_dir="/tmp/test-alias",
            )
            assert result is True
            mock_func.assert_called_once()

    def test_unknown_template_raises(self):
        """Unknown template ID raises ValueError."""
        with pytest.raises(ValueError, match="Unknown template"):
            clone_template(
                template_id="nonexistent",
                project_dir="/tmp/test",
            )

    def test_kwargs_forwarded(self):
        """git_strategy, branch, tag are forwarded."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {"research": mock_func}):
            clone_template(
                template_id="research",
                project_dir="/tmp/test",
                git_strategy="origin",
                branch="develop",
                tag=None,
            )
            mock_func.assert_called_once_with(
                project_dir="/tmp/test",
                git_strategy="origin",
                branch="develop",
                tag=None,
            )

    def test_git_strategy_none(self):
        """git_strategy=None is forwarded correctly."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {"research": mock_func}):
            clone_template(
                template_id="research",
                project_dir="/tmp/test",
                git_strategy=None,
            )
            mock_func.assert_called_once_with(
                project_dir="/tmp/test",
                git_strategy=None,
                branch=None,
                tag=None,
            )

    def test_return_false_propagated(self):
        """False return from clone function is propagated."""
        mock_func = MagicMock(return_value=False)
        with patch.dict(TEMPLATES, {"research": mock_func}):
            result = clone_template(
                template_id="research",
                project_dir="/tmp/test",
            )
            assert result is False


class TestTemplateIdHelpers:
    """Test helper functions for template IDs."""

    def test_get_template_ids(self):
        """get_template_ids returns canonical IDs only."""
        ids = get_template_ids()
        assert "research" in ids
        assert "research_minimal" in ids
        assert "pip_project" in ids
        assert "singularity" in ids
        assert "paper_directory" in ids
        assert "minimal" not in ids

    def test_get_all_template_ids(self):
        """get_all_template_ids includes aliases."""
        ids = get_all_template_ids()
        assert "research" in ids
        assert "minimal" in ids
        assert "pip-project" in ids
        assert "paper" in ids


class TestIncludeDirsForwarding:
    """Test include_dirs parameter forwarding."""

    def test_include_dirs_forwarded_to_minimal(self):
        """include_dirs kwarg is forwarded to clone function."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {"research_minimal": mock_func}):
            clone_template(
                template_id="research_minimal",
                project_dir="/tmp/test",
                include_dirs=["00_shared", "01_manuscript"],
            )
            mock_func.assert_called_once()
            _, kwargs = mock_func.call_args
            assert kwargs["include_dirs"] == ["00_shared", "01_manuscript"]

    def test_extra_kwargs_forwarded(self):
        """Extra kwargs are forwarded through dispatcher."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {"research": mock_func}):
            clone_template(
                template_id="research",
                project_dir="/tmp/test",
                use_cache=False,
            )
            mock_func.assert_called_once()
            _, kwargs = mock_func.call_args
            assert kwargs["use_cache"] is False


class TestFilterToIncludeDirs:
    """Test the _filter_to_include_dirs helper."""

    def test_removes_unlisted_dirs(self, tmp_path):
        """Directories not in include_dirs are removed."""
        from scitex.template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        (tmp_path / "README.md").write_text("test")

        _filter_to_include_dirs(tmp_path, ["00_shared", "01_manuscript"])

        assert (tmp_path / "00_shared").exists()
        assert (tmp_path / "01_manuscript").exists()
        assert not (tmp_path / "02_supplementary").exists()
        assert not (tmp_path / "03_revision").exists()

    def test_preserves_readme_and_license(self, tmp_path):
        """README.md and LICENSE are always preserved."""
        from scitex.template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "README.md").write_text("readme")
        (tmp_path / "LICENSE").write_text("license")
        (tmp_path / "extra").mkdir()

        _filter_to_include_dirs(tmp_path, ["00_shared"])

        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "LICENSE").exists()
        assert not (tmp_path / "extra").exists()

    def test_preserves_dotfiles(self, tmp_path):
        """Dotfiles like .gitignore are always preserved."""
        from scitex.template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc")
        (tmp_path / ".git").mkdir()
        (tmp_path / "extra_dir").mkdir()
        (tmp_path / "extra_file.txt").write_text("x")

        _filter_to_include_dirs(tmp_path, ["00_shared"])

        assert (tmp_path / ".gitignore").exists()
        assert (tmp_path / ".git").exists()
        assert not (tmp_path / "extra_dir").exists()
        assert not (tmp_path / "extra_file.txt").exists()

    def test_removes_unlisted_files(self, tmp_path):
        """Files not in include_dirs are also removed."""
        from scitex.template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "compile.sh").write_text("#!/bin/bash")
        (tmp_path / "pyproject.toml").write_text("[project]")

        _filter_to_include_dirs(tmp_path, ["00_shared", "compile.sh"])

        assert (tmp_path / "compile.sh").exists()
        assert not (tmp_path / "pyproject.toml").exists()


class TestMinimalIncludeDirs:
    """Test MINIMAL_INCLUDE_DIRS constant."""

    def test_minimal_dirs_defined(self):
        """MINIMAL_INCLUDE_DIRS is exported and contains expected dirs."""
        from scitex.template import MINIMAL_INCLUDE_DIRS

        assert "00_shared" in MINIMAL_INCLUDE_DIRS
        assert "01_manuscript" in MINIMAL_INCLUDE_DIRS
        assert "scripts" in MINIMAL_INCLUDE_DIRS
        assert "compile.sh" in MINIMAL_INCLUDE_DIRS
        assert "Makefile" in MINIMAL_INCLUDE_DIRS
        assert "config" in MINIMAL_INCLUDE_DIRS

    def test_minimal_does_not_include_supplementary(self):
        """Minimal template excludes non-essential directories."""
        from scitex.template import MINIMAL_INCLUDE_DIRS

        assert "02_supplementary" not in MINIMAL_INCLUDE_DIRS
        assert "03_revision" not in MINIMAL_INCLUDE_DIRS
        assert "src" not in MINIMAL_INCLUDE_DIRS
        assert "tests" not in MINIMAL_INCLUDE_DIRS

    def test_clone_research_minimal_uses_include_dirs(self):
        """clone_research_minimal passes include_dirs to clone_project."""
        with patch(
            "scitex.template._project.clone_research_minimal.clone_project"
        ) as mock:
            mock.return_value = True
            from scitex.template._project.clone_research_minimal import (
                MINIMAL_INCLUDE_DIRS,
                clone_research_minimal,
            )

            clone_research_minimal("/tmp/test-minimal")
            mock.assert_called_once()
            _, kwargs = mock.call_args
            assert kwargs["include_dirs"] == MINIMAL_INCLUDE_DIRS


class TestCustomizeMinimalPaths:
    """Test that customize_minimal_template finds files in direct clone layout."""

    def test_direct_clone_layout(self, tmp_path):
        """customize_minimal_template works with direct 00_shared/ layout."""
        from scitex.template._project._customize import customize_minimal_template

        shared = tmp_path / "00_shared"
        shared.mkdir()
        (shared / "title.tex").write_text("\\title{Old Title}")
        (shared / "authors.tex").write_text("\\author{Old Author}")

        customize_minimal_template(
            str(tmp_path),
            {"name": "My Project", "owner": "testuser", "owner_full_name": "Test User"},
        )

        title = (shared / "title.tex").read_text()
        assert "My Project" in title
        authors = (shared / "authors.tex").read_text()
        assert "Test User" in authors

    def test_nested_layout_still_works(self, tmp_path):
        """customize_minimal_template also works with scitex/writer/ layout."""
        from scitex.template._project._customize import customize_minimal_template

        nested = tmp_path / "scitex" / "writer" / "00_shared"
        nested.mkdir(parents=True)
        (nested / "title.tex").write_text("\\title{Old}")

        customize_minimal_template(
            str(tmp_path),
            {"name": "Nested Project"},
        )

        title = (nested / "title.tex").read_text()
        assert "Nested Project" in title


class TestImportFromPackage:
    """Test that clone_template is importable from scitex.template."""

    def test_import_from_template(self):
        """clone_template is importable from scitex.template."""
        from scitex.template import clone_template as ct

        assert callable(ct)

    def test_in_all(self):
        """clone_template is in __all__."""
        import scitex.template

        assert "clone_template" in scitex.template.__all__

    def test_minimal_include_dirs_in_all(self):
        """MINIMAL_INCLUDE_DIRS is in __all__."""
        import scitex.template

        assert "MINIMAL_INCLUDE_DIRS" in scitex.template.__all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF
