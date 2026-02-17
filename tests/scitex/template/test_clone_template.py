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
        assert "scitex_minimal" in ids
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

    def test_minimal_alias_resolves_to_scitex_minimal(self):
        """The 'minimal' alias resolves to scitex_minimal."""
        assert ALIASES["minimal"] == "scitex_minimal"


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

    def test_minimal_includes_supplementary_and_revision(self):
        """Minimal template includes supplementary and revision."""
        from scitex.template import MINIMAL_INCLUDE_DIRS

        assert "02_supplementary" in MINIMAL_INCLUDE_DIRS
        assert "03_revision" in MINIMAL_INCLUDE_DIRS

    def test_minimal_excludes_dev_dirs(self):
        """Minimal template excludes dev-only directories."""
        from scitex.template import MINIMAL_INCLUDE_DIRS

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

    def test_clone_scitex_minimal_in_all(self):
        """clone_scitex_minimal is in __all__."""
        import scitex.template

        assert "clone_scitex_minimal" in scitex.template.__all__


class TestScitexMinimalDispatch:
    """Test scitex_minimal template dispatching."""

    def test_scitex_minimal_in_templates(self):
        """scitex_minimal is registered in TEMPLATES."""
        assert "scitex_minimal" in TEMPLATES

    def test_scitex_minimal_dispatches(self):
        """scitex_minimal dispatches to its clone function."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {"scitex_minimal": mock_func}):
            result = clone_template(
                template_id="scitex_minimal",
                project_dir="/tmp/test-scitex-minimal",
            )
            assert result is True
            mock_func.assert_called_once()

    def test_minimal_alias_dispatches_to_scitex_minimal(self):
        """'minimal' alias dispatches to scitex_minimal function."""
        mock_func = MagicMock(return_value=True)
        with patch.dict(TEMPLATES, {"scitex_minimal": mock_func}):
            result = clone_template(
                template_id="minimal",
                project_dir="/tmp/test-minimal-alias",
            )
            assert result is True
            mock_func.assert_called_once()


class TestScitexMinimalComposition:
    """Test clone_scitex_minimal composes ensure calls."""

    @patch("scitex.template._project._scholar_writer_integration.ensure_integration")
    @patch("scitex.scholar.ensure")
    @patch("scitex.writer.ensure")
    def test_calls_writer_ensure(self, mock_writer, mock_scholar, mock_int, tmp_path):
        """clone_scitex_minimal calls writer.ensure."""
        from scitex.template._project.clone_scitex_minimal import clone_scitex_minimal

        clone_scitex_minimal(str(tmp_path / "proj"))
        mock_writer.assert_called_once()

    @patch("scitex.template._project._scholar_writer_integration.ensure_integration")
    @patch("scitex.scholar.ensure")
    @patch("scitex.writer.ensure")
    def test_calls_scholar_ensure(self, mock_writer, mock_scholar, mock_int, tmp_path):
        """clone_scitex_minimal calls scholar.ensure."""
        from scitex.template._project.clone_scitex_minimal import clone_scitex_minimal

        clone_scitex_minimal(str(tmp_path / "proj"))
        mock_scholar.assert_called_once()

    @patch("scitex.template._project._scholar_writer_integration.ensure_integration")
    @patch("scitex.scholar.ensure")
    @patch("scitex.writer.ensure")
    def test_calls_ensure_integration(
        self, mock_writer, mock_scholar, mock_int, tmp_path
    ):
        """clone_scitex_minimal sets up integration."""
        from scitex.template._project.clone_scitex_minimal import clone_scitex_minimal

        clone_scitex_minimal(str(tmp_path / "proj"))
        mock_int.assert_called_once()

    @patch("scitex.template._project._scholar_writer_integration.ensure_integration")
    @patch("scitex.scholar.ensure")
    @patch("scitex.writer.ensure")
    def test_forwards_git_strategy(self, mock_writer, mock_scholar, mock_int, tmp_path):
        """git_strategy is forwarded to writer.ensure."""
        from scitex.template._project.clone_scitex_minimal import clone_scitex_minimal

        clone_scitex_minimal(str(tmp_path / "proj"), git_strategy="origin")
        _, kwargs = mock_writer.call_args
        assert kwargs["git_strategy"] == "origin"

    @patch("scitex.template._project._scholar_writer_integration.ensure_integration")
    @patch("scitex.scholar.ensure")
    @patch("scitex.writer.ensure")
    def test_returns_true_on_success(
        self, mock_writer, mock_scholar, mock_int, tmp_path
    ):
        """Returns True on successful creation."""
        from scitex.template._project.clone_scitex_minimal import clone_scitex_minimal

        result = clone_scitex_minimal(str(tmp_path / "proj"))
        assert result is True


class TestScholarEnsure:
    """Test scitex.scholar.ensure creates workspace scaffold."""

    def test_creates_scaffold(self, tmp_path):
        """ensure creates bib_files, library, prompts."""
        from scitex.scholar.ensure import ensure

        result = ensure(str(tmp_path))
        assert result == tmp_path / "scitex" / "scholar"
        assert (tmp_path / "scitex" / "scholar" / "bib_files").is_dir()
        assert (tmp_path / "scitex" / "scholar" / "library").is_dir()
        assert (tmp_path / "scitex" / "scholar" / "prompts").is_dir()

    def test_noop_if_exists(self, tmp_path):
        """ensure is a no-op if scholar directory already exists."""
        from scitex.scholar.ensure import ensure

        scholar_dir = tmp_path / "scitex" / "scholar"
        scholar_dir.mkdir(parents=True)
        (scholar_dir / "existing_file.txt").write_text("keep me")

        result = ensure(str(tmp_path))
        assert result == scholar_dir
        assert (scholar_dir / "existing_file.txt").exists()

    def test_importable_from_package(self):
        """ensure is importable from scitex.scholar."""
        from scitex.scholar import ensure

        assert callable(ensure)


class TestWriterEnsure:
    """Test scitex.writer.ensure function signature and behavior."""

    def test_noop_if_exists(self, tmp_path):
        """ensure returns existing path without calling Writer."""
        from scitex.writer import ensure

        writer_dir = tmp_path / "scitex" / "writer"
        writer_dir.mkdir(parents=True)

        result = ensure(str(tmp_path))
        assert result == writer_dir

    @patch("scitex.writer.Writer")
    def test_calls_writer_constructor(self, mock_writer_cls, tmp_path):
        """ensure calls Writer constructor for new workspace."""
        from scitex.writer import ensure

        result = ensure(str(tmp_path))
        expected_path = tmp_path / "scitex" / "writer"
        mock_writer_cls.assert_called_once_with(
            str(expected_path), git_strategy="child"
        )

    @patch("scitex.writer.Writer")
    def test_forwards_kwargs(self, mock_writer_cls, tmp_path):
        """ensure forwards git_strategy and other kwargs."""
        from scitex.writer import ensure

        ensure(str(tmp_path), git_strategy="origin", branch="develop")
        mock_writer_cls.assert_called_once_with(
            str(tmp_path / "scitex" / "writer"),
            git_strategy="origin",
            branch="develop",
        )

    def test_importable_from_package(self):
        """ensure is importable from scitex.writer."""
        from scitex.writer import ensure

        assert callable(ensure)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF
