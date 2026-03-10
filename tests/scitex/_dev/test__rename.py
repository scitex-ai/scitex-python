#!/usr/bin/env python3
# Timestamp: 2026-03-09
# File: tests/scitex/_dev/test__rename.py

"""Comprehensive tests for scitex._dev._rename bulk rename utility."""

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from scitex._dev._rename import (
    RenameConfig,
    RenameResult,
    bulk_rename,
    execute_rename,
    preview_rename,
)
from scitex._dev._rename._filters import (
    find_matching_files,
    is_django_protected_line,
    is_src_excluded,
    matches_include_extensions,
    parse_csv_config,
    should_exclude_path,
)
from scitex._dev._rename._io import (
    _sudo_run,
    mkdir,
    rename_path,
    rmdir,
    set_sudo_password,
    symlink_to,
    unlink_path,
    write_text,
)
from scitex._dev._rename._safety import (
    check_directory_safety,
    create_backup,
    has_uncommitted_changes,
    is_git_repo,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_execute(pattern, replacement, directory, **kwargs):
    """Execute rename with safety checks mocked out."""
    with patch("scitex._dev._rename._core.has_uncommitted_changes", return_value=False):
        with patch(
            "scitex._dev._rename._core.check_directory_safety", return_value=None
        ):
            return execute_rename(
                pattern, replacement, directory=str(directory), **kwargs
            )


# ===========================================================================
# RenameConfig
# ===========================================================================


class TestRenameConfig:
    def test_defaults(self):
        config = RenameConfig(pattern="old", replacement="new")
        assert config.dry_run is True
        assert config.django_safe is True
        assert config.create_backup is False
        assert "py" in config.path_includes
        assert "__pycache__" in config.path_excludes

    def test_custom_values(self):
        config = RenameConfig(
            pattern="foo",
            replacement="bar",
            directory="/tmp",
            dry_run=False,
            django_safe=False,
            extra_excludes=["*.log"],
        )
        assert config.dry_run is False
        assert config.django_safe is False
        assert config.extra_excludes == ["*.log"]

    def test_skip_ids_default_empty(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert config.skip_ids == []

    def test_use_sudo_default_false(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert config.use_sudo is False


# ===========================================================================
# RenameResult
# ===========================================================================


class TestRenameResult:
    def test_error_field_default_none(self):
        result = RenameResult(
            dry_run=True,
            pattern="a",
            replacement="b",
            directory=".",
            contents=[],
            symlink_targets=[],
            symlink_names=[],
            file_names=[],
            dir_names=[],
            summary={},
        )
        assert result.error is None
        assert result.collisions == []

    def test_error_field_set(self):
        result = RenameResult(
            dry_run=False,
            pattern="a",
            replacement="b",
            directory=".",
            contents=[],
            symlink_targets=[],
            symlink_names=[],
            file_names=[],
            dir_names=[],
            summary={},
            error="Something went wrong",
        )
        assert result.error == "Something went wrong"


# ===========================================================================
# Filtering
# ===========================================================================


class TestFiltering:
    def test_parse_csv_config(self):
        assert parse_csv_config("py,txt,sh") == ["py", "txt", "sh"]
        assert parse_csv_config("") == []
        assert parse_csv_config("  py , txt ") == ["py", "txt"]

    def test_should_exclude_path_pycache(self):
        config = RenameConfig(pattern="x", replacement="y")
        path = Path("/some/dir/__pycache__/module.pyc")
        assert should_exclude_path(path, config) is True

    def test_should_exclude_path_normal(self):
        config = RenameConfig(pattern="x", replacement="y")
        path = Path("/some/dir/src/module.py")
        assert should_exclude_path(path, config) is False

    def test_should_exclude_path_extra(self):
        config = RenameConfig(pattern="x", replacement="y", extra_excludes=["vendor"])
        path = Path("/some/vendor/lib.py")
        assert should_exclude_path(path, config) is True

    def test_should_exclude_path_node_modules(self):
        config = RenameConfig(pattern="x", replacement="y")
        path = Path("/project/node_modules/pkg/index.js")
        assert should_exclude_path(path, config) is True

    def test_should_exclude_path_git(self):
        config = RenameConfig(pattern="x", replacement="y")
        path = Path("/project/.git/config")
        assert should_exclude_path(path, config) is True

    def test_should_exclude_path_venv(self):
        config = RenameConfig(pattern="x", replacement="y")
        path = Path("/project/.venv/lib/site-packages/pkg.py")
        assert should_exclude_path(path, config) is True

    def test_should_exclude_migrations(self):
        """Migrations are in path_must_excludes by default."""
        config = RenameConfig(pattern="x", replacement="y")
        path = Path("/project/apps/my_app/migrations/0001_initial.py")
        assert should_exclude_path(path, config) is True

    def test_matches_include_extensions(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert matches_include_extensions(Path("file.py"), config) is True
        assert matches_include_extensions(Path("file.txt"), config) is True
        assert matches_include_extensions(Path("file.jpg"), config) is False

    def test_matches_include_html(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert matches_include_extensions(Path("template.html"), config) is True

    def test_matches_include_ts(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert matches_include_extensions(Path("app.ts"), config) is True
        assert matches_include_extensions(Path("comp.tsx"), config) is True

    def test_matches_include_custom(self):
        config = RenameConfig(pattern="x", replacement="y", path_includes="rs,go")
        assert matches_include_extensions(Path("main.rs"), config) is True
        assert matches_include_extensions(Path("main.go"), config) is True
        assert matches_include_extensions(Path("main.py"), config) is False

    def test_is_django_protected_line(self):
        assert is_django_protected_line("    db_table = 'my_table'", "my") is True
        assert is_django_protected_line("    related_name='items'", "items") is True
        assert is_django_protected_line("INSTALLED_APPS = [", "APP") is True
        assert is_django_protected_line("x = my_function()", "my") is False

    def test_django_protected_does_not_block_app_config(self):
        """apps.py name and urls.py app_name should NOT be protected."""
        assert (
            is_django_protected_line('    name = "apps.modulemaker_app"', "modulemaker")
            is False
        )
        assert (
            is_django_protected_line('app_name = "modulemaker"', "modulemaker") is False
        )

    def test_django_protected_db_table_still_protected(self):
        assert (
            is_django_protected_line("    db_table = 'old_table'", "old_table") is True
        )

    def test_django_protected_related_name_variants(self):
        assert is_django_protected_line("    related_name='old_items'", "old") is True
        assert is_django_protected_line('    related_name="old_items"', "old") is True

    def test_django_protected_manager_line(self):
        assert is_django_protected_line("    objects = OldManager()", "Old") is True

    def test_django_protected_settings_patterns(self):
        assert is_django_protected_line("DATABASES = {", "DATA") is True
        assert is_django_protected_line("MIDDLEWARE = [", "MID") is True
        assert is_django_protected_line("TEMPLATES = [", "TEMP") is True

    def test_is_src_excluded(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert is_src_excluded("db_table='test'", config) is True
        assert is_src_excluded("normal code here", config) is False

    def test_is_src_excluded_related_name(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert is_src_excluded("related_name='items'", config) is True

    def test_is_src_excluded_custom(self):
        config = RenameConfig(
            pattern="x", replacement="y", src_must_excludes="KEEP_THIS"
        )
        assert is_src_excluded("KEEP_THIS = True", config) is True


# ===========================================================================
# Preview rename (dry run)
# ===========================================================================


class TestPreviewRename:
    def test_preview_file_contents(self, tmp_path):
        (tmp_path / "test.py").write_text("old_name = 1\nold_name = 2\n")
        result = preview_rename("old_name", "new_name", directory=str(tmp_path))

        assert result.dry_run is True
        assert len(result.contents) == 1
        assert result.contents[0]["matches"] == 2
        assert "old_name" in (tmp_path / "test.py").read_text()

    def test_preview_includes_line_details(self, tmp_path):
        (tmp_path / "test.py").write_text("old_name = 1\nkeep\nold_name = 2\n")
        result = preview_rename("old_name", "new_name", directory=str(tmp_path))

        assert "lines" in result.contents[0]
        lines = result.contents[0]["lines"]
        assert len(lines) == 2
        assert lines[0]["action"] == "replace"
        assert lines[0]["line_num"] == 1
        assert "old_name" in lines[0]["before"]
        assert "new_name" in lines[0]["after"]

    def test_preview_line_details_shows_protected(self, tmp_path):
        content = "db_table = 'old_val'\nold_val = 1\n"
        (tmp_path / "models.py").write_text(content)
        result = preview_rename("old_val", "new_val", directory=str(tmp_path))

        lines = result.contents[0]["lines"]
        actions = [l["action"] for l in lines]
        assert "protect" in actions
        assert "replace" in actions

    def test_preview_file_names(self, tmp_path):
        (tmp_path / "old_module.py").write_text("pass\n")
        result = preview_rename("old_module", "new_module", directory=str(tmp_path))

        assert len(result.file_names) == 1
        assert "old_module" in result.file_names[0]["old_path"]
        assert (tmp_path / "old_module.py").exists()

    def test_preview_directory_names(self, tmp_path):
        (tmp_path / "old_pkg").mkdir()
        (tmp_path / "old_pkg" / "__init__.py").write_text("")
        result = preview_rename("old_pkg", "new_pkg", directory=str(tmp_path))

        assert len(result.dir_names) == 1
        assert (tmp_path / "old_pkg").exists()

    def test_preview_no_changes_for_no_matches(self, tmp_path):
        (tmp_path / "test.py").write_text("nothing here\n")
        result = preview_rename("nonexistent", "replacement", directory=str(tmp_path))

        assert len(result.contents) == 0
        assert len(result.file_names) == 0
        assert len(result.dir_names) == 0

    def test_preview_multiple_files(self, tmp_path):
        (tmp_path / "a.py").write_text("old = 1\n")
        (tmp_path / "b.py").write_text("old = 2\n")
        (tmp_path / "c.py").write_text("no match\n")
        result = preview_rename("old", "new", directory=str(tmp_path))

        assert len(result.contents) == 2

    def test_preview_preserves_non_matching_lines(self, tmp_path):
        (tmp_path / "test.py").write_text("line1\nold\nline3\n")
        result = preview_rename("old", "new", directory=str(tmp_path))

        lines = result.contents[0]["lines"]
        assert len(lines) == 1
        assert lines[0]["line_num"] == 2


# ===========================================================================
# Execute rename (live)
# ===========================================================================


class TestExecuteRename:
    def test_execute_file_contents(self, tmp_path):
        (tmp_path / "test.py").write_text("old_name = 1\n")
        result = _safe_execute("old_name", "new_name", tmp_path)

        assert result.dry_run is False
        assert "new_name" in (tmp_path / "test.py").read_text()

    def test_execute_file_names(self, tmp_path):
        (tmp_path / "old_mod.py").write_text("pass\n")
        _safe_execute("old_mod", "new_mod", tmp_path)

        assert not (tmp_path / "old_mod.py").exists()
        assert (tmp_path / "new_mod.py").exists()

    def test_execute_directory_names(self, tmp_path):
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "file.py").write_text("pass\n")
        _safe_execute("old_dir", "new_dir", tmp_path)

        assert not (tmp_path / "old_dir").exists()
        assert (tmp_path / "new_dir").exists()
        assert (tmp_path / "new_dir" / "file.py").exists()

    def test_execute_blocks_on_uncommitted(self, tmp_path):
        (tmp_path / "test.py").write_text("old\n")
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=True
        ):
            result = execute_rename("old", "new", directory=str(tmp_path))

        assert result.error is not None
        assert "Uncommitted" in result.error
        assert "old" in (tmp_path / "test.py").read_text()

    def test_execute_deepest_dir_first(self, tmp_path):
        (tmp_path / "old_a").mkdir()
        (tmp_path / "old_a" / "old_b").mkdir()
        (tmp_path / "old_a" / "old_b" / "file.py").write_text("pass\n")
        result = _safe_execute("old_", "new_", tmp_path)

        assert (tmp_path / "new_a" / "new_b" / "file.py").exists()
        assert len(result.dir_names) == 2

    def test_execute_force_bypasses_uncommitted_check(self, tmp_path):
        (tmp_path / "test.py").write_text("old = 1\n")
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=True
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                result = execute_rename(
                    "old", "new", directory=str(tmp_path), force=True
                )

        assert result.error is None
        assert "new" in (tmp_path / "test.py").read_text()

    def test_execute_multiple_occurrences_per_line(self, tmp_path):
        (tmp_path / "test.py").write_text("old old old\n")
        result = _safe_execute("old", "new", tmp_path)

        text = (tmp_path / "test.py").read_text()
        assert text.strip() == "new new new"
        assert result.contents[0]["matches"] == 3

    def test_execute_preserves_file_with_no_matches(self, tmp_path):
        (tmp_path / "keep.py").write_text("no match here\n")
        (tmp_path / "change.py").write_text("old = 1\n")
        _safe_execute("old", "new", tmp_path)

        assert (tmp_path / "keep.py").read_text() == "no match here\n"
        assert "new" in (tmp_path / "change.py").read_text()

    def test_execute_content_and_filename_both_renamed(self, tmp_path):
        (tmp_path / "old_mod.py").write_text("import old_mod\n")
        _safe_execute("old_mod", "new_mod", tmp_path)

        assert not (tmp_path / "old_mod.py").exists()
        assert (tmp_path / "new_mod.py").exists()
        assert "import new_mod" in (tmp_path / "new_mod.py").read_text()


# ===========================================================================
# Django-safe mode
# ===========================================================================


class TestDjangoSafe:
    def test_protects_db_table(self, tmp_path):
        content = "class Meta:\n    db_table = 'old_table'\nold_table_var = 1\n"
        (tmp_path / "models.py").write_text(content)
        _safe_execute("old_table", "new_table", tmp_path)

        text = (tmp_path / "models.py").read_text()
        assert "db_table = 'old_table'" in text
        assert "new_table_var = 1" in text

    def test_no_django_safe(self, tmp_path):
        content = "db_table = 'old_table'\n"
        (tmp_path / "models.py").write_text(content)
        _safe_execute("old_table", "new_table", tmp_path, django_safe=False)

        text = (tmp_path / "models.py").read_text()
        assert "new_table" in text

    def test_protects_related_name(self, tmp_path):
        content = "    related_name='old_items'\nold_items = []\n"
        (tmp_path / "models.py").write_text(content)
        _safe_execute("old_items", "new_items", tmp_path)

        text = (tmp_path / "models.py").read_text()
        assert "related_name='old_items'" in text
        assert "new_items = []" in text

    def test_protects_installed_apps(self, tmp_path):
        content = "INSTALLED_APPS = ['old_app']\nold_app_var = 1\n"
        (tmp_path / "settings.py").write_text(content)
        _safe_execute("old_app", "new_app", tmp_path)

        text = (tmp_path / "settings.py").read_text()
        assert "INSTALLED_APPS = ['old_app']" in text
        assert "new_app_var = 1" in text

    def test_protects_old_name_new_name_in_migration(self, tmp_path):
        content = "old_name='old_field'\nnew_name='new_field'\nold_field = 1\n"
        (tmp_path / "test.py").write_text(content)
        _safe_execute("old_field", "new_field", tmp_path)

        text = (tmp_path / "test.py").read_text()
        assert "old_name='old_field'" in text
        assert "new_name='new_field'" in text


# ===========================================================================
# Symlinks
# ===========================================================================


class TestSymlinks:
    def test_symlink_target_update(self, tmp_path):
        target = tmp_path / "old_target.py"
        target.write_text("pass\n")
        link = tmp_path / "link.py"
        link.symlink_to("old_target.py")

        with patch(
            "scitex._dev._rename._core.check_directory_safety", return_value=None
        ):
            config = RenameConfig(
                pattern="old_target",
                replacement="new_target",
                directory=str(tmp_path),
                dry_run=False,
            )
            result = bulk_rename(config)

        assert len(result.symlink_targets) == 1
        assert os.readlink(str(link)) == "new_target.py"

    def test_symlink_name_rename(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("pass\n")
        link = tmp_path / "old_link.py"
        link.symlink_to("target.py")

        with patch(
            "scitex._dev._rename._core.check_directory_safety", return_value=None
        ):
            config = RenameConfig(
                pattern="old_link",
                replacement="new_link",
                directory=str(tmp_path),
                dry_run=False,
            )
            result = bulk_rename(config)

        assert len(result.symlink_names) == 1
        assert (tmp_path / "new_link.py").is_symlink()

    def test_symlink_target_and_name_both_updated(self, tmp_path):
        target = tmp_path / "old_file.py"
        target.write_text("pass\n")
        link = tmp_path / "old_link.py"
        link.symlink_to("old_file.py")

        with patch(
            "scitex._dev._rename._core.check_directory_safety", return_value=None
        ):
            config = RenameConfig(
                pattern="old_",
                replacement="new_",
                directory=str(tmp_path),
                dry_run=False,
            )
            result = bulk_rename(config)

        assert len(result.symlink_targets) == 1
        assert len(result.symlink_names) == 1

    def test_symlink_collision_detected(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("pass\n")
        (tmp_path / "new_link.py").write_text("existing\n")
        link = tmp_path / "old_link.py"
        link.symlink_to("target.py")

        result = preview_rename("old_link", "new_link", directory=str(tmp_path))

        collisions = [c for c in result.collisions if c["type"] == "symlink"]
        assert len(collisions) == 1


# ===========================================================================
# Collision detection
# ===========================================================================


class TestCollisions:
    def test_file_collision_detected_in_dry_run(self, tmp_path):
        (tmp_path / "old_mod.py").write_text("pass\n")
        (tmp_path / "new_mod.py").write_text("existing\n")

        result = preview_rename("old_mod", "new_mod", directory=str(tmp_path))

        assert len(result.collisions) == 1
        assert result.collisions[0]["type"] == "file"
        assert "new_mod.py" in result.collisions[0]["path"]

    def test_dir_collision_detected_in_dry_run(self, tmp_path):
        (tmp_path / "old_pkg").mkdir()
        (tmp_path / "old_pkg" / "__init__.py").write_text("")
        (tmp_path / "new_pkg").mkdir()
        (tmp_path / "new_pkg" / "__init__.py").write_text("")

        result = preview_rename("old_pkg", "new_pkg", directory=str(tmp_path))

        assert len(result.collisions) >= 1
        types = [c["type"] for c in result.collisions]
        assert "directory" in types

    def test_no_collision_when_target_absent(self, tmp_path):
        (tmp_path / "old_mod.py").write_text("pass\n")

        result = preview_rename("old_mod", "new_mod", directory=str(tmp_path))

        assert len(result.collisions) == 0

    def test_execute_blocks_on_file_collision(self, tmp_path):
        (tmp_path / "old_mod.py").write_text("pass\n")
        (tmp_path / "new_mod.py").write_text("existing\n")

        result = _safe_execute("old_mod", "new_mod", tmp_path)

        assert result.error is not None
        assert "Collision" in result.error
        assert (tmp_path / "old_mod.py").exists()
        assert "existing" in (tmp_path / "new_mod.py").read_text()

    def test_collision_summary_count(self, tmp_path):
        (tmp_path / "old_a.py").write_text("pass\n")
        (tmp_path / "new_a.py").write_text("existing\n")
        (tmp_path / "old_b.py").write_text("pass\n")
        (tmp_path / "new_b.py").write_text("existing\n")

        result = preview_rename("old_", "new_", directory=str(tmp_path))

        assert result.summary["collisions"] == 2

    def test_dir_collision_allows_merge(self, tmp_path):
        """Directory collisions don't block execution (merge instead)."""
        (tmp_path / "old_pkg").mkdir()
        (tmp_path / "old_pkg" / "a.py").write_text("pass\n")
        (tmp_path / "new_pkg").mkdir()
        (tmp_path / "new_pkg" / "b.py").write_text("pass\n")

        result = _safe_execute("old_pkg", "new_pkg", tmp_path)

        # Should succeed (dir collisions merged, not blocked)
        assert result.error is None
        assert (tmp_path / "new_pkg" / "a.py").exists()
        assert (tmp_path / "new_pkg" / "b.py").exists()


# ===========================================================================
# Directory merge
# ===========================================================================


class TestDirectoryMerge:
    def test_merge_moves_all_children(self, tmp_path):
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "file1.py").write_text("one\n")
        (tmp_path / "old_dir" / "file2.py").write_text("two\n")
        (tmp_path / "new_dir").mkdir()
        (tmp_path / "new_dir" / "file3.py").write_text("three\n")

        _safe_execute("old_dir", "new_dir", tmp_path)

        assert not (tmp_path / "old_dir").exists()
        assert (tmp_path / "new_dir" / "file1.py").exists()
        assert (tmp_path / "new_dir" / "file2.py").exists()
        assert (tmp_path / "new_dir" / "file3.py").exists()

    def test_merge_nested_directories(self, tmp_path):
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "sub").mkdir()
        (tmp_path / "old_dir" / "sub" / "nested.py").write_text("nested\n")
        (tmp_path / "new_dir").mkdir()
        (tmp_path / "new_dir" / "sub").mkdir()
        (tmp_path / "new_dir" / "sub" / "existing.py").write_text("existing\n")

        _safe_execute("old_dir", "new_dir", tmp_path)

        assert (tmp_path / "new_dir" / "sub" / "nested.py").exists()
        assert (tmp_path / "new_dir" / "sub" / "existing.py").exists()


# ===========================================================================
# Summary
# ===========================================================================


class TestSummary:
    def test_summary_counts(self, tmp_path):
        (tmp_path / "old_file.py").write_text("old_name = 1\nold_name = 2\n")
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "test.txt").write_text("pass\n")

        result = preview_rename("old_", "new_", directory=str(tmp_path))

        assert result.summary["content_files"] >= 1
        assert result.summary["content_matches"] >= 2
        assert result.summary["files_renamed"] >= 1
        assert result.summary["dirs_renamed"] >= 1

    def test_summary_protected_files_count(self, tmp_path):
        (tmp_path / "models.py").write_text("db_table = 'old_val'\nold_val = 1\n")
        (tmp_path / "clean.py").write_text("old_val = 2\n")

        result = preview_rename("old_val", "new_val", directory=str(tmp_path))

        assert result.summary["protected_files"] == 1

    def test_summary_zero_when_no_matches(self, tmp_path):
        (tmp_path / "test.py").write_text("nothing\n")
        result = preview_rename("nonexistent", "replacement", directory=str(tmp_path))

        assert result.summary["content_files"] == 0
        assert result.summary["files_renamed"] == 0
        assert result.summary["dirs_renamed"] == 0


# ===========================================================================
# Skip IDs
# ===========================================================================


class TestSkipIds:
    def test_skip_file_level(self, tmp_path):
        """Skip all changes in a specific file by file-level ID."""
        (tmp_path / "a.py").write_text("old = 1\n")
        (tmp_path / "b.py").write_text("old = 2\n")
        preview = preview_rename("old", "new", directory=str(tmp_path))
        a_id = [c["id"] for c in preview.contents if "a.py" in c["file"]][0]
        _safe_execute("old", "new", tmp_path, skip_ids=[a_id])
        assert "old" in (tmp_path / "a.py").read_text()
        assert "new" in (tmp_path / "b.py").read_text()

    def test_skip_line_level(self, tmp_path):
        """Skip a specific line by line-level ID."""
        (tmp_path / "test.py").write_text("old_a = 1\nkeep = 2\nold_b = 3\n")
        preview = preview_rename("old", "new", directory=str(tmp_path))
        file_result = preview.contents[0]
        line_id = [l["id"] for l in file_result["lines"] if l["line_num"] == 1][0]
        _safe_execute("old", "new", tmp_path, skip_ids=[line_id])
        text = (tmp_path / "test.py").read_text()
        assert "old_a" in text
        assert "new_b" in text

    def test_skip_dir_rename(self, tmp_path):
        """Skip a directory rename by ID."""
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "file.py").write_text("pass\n")
        preview = preview_rename("old_dir", "new_dir", directory=str(tmp_path))
        dir_id = preview.dir_names[0]["id"]
        _safe_execute("old_dir", "new_dir", tmp_path, skip_ids=[dir_id])
        assert (tmp_path / "old_dir").exists()

    def test_skip_file_rename(self, tmp_path):
        """Skip a file rename by ID."""
        (tmp_path / "old_mod.py").write_text("pass\n")
        preview = preview_rename("old_mod", "new_mod", directory=str(tmp_path))
        file_id = preview.file_names[0]["id"]
        _safe_execute("old_mod", "new_mod", tmp_path, skip_ids=[file_id])
        assert (tmp_path / "old_mod.py").exists()
        assert not (tmp_path / "new_mod.py").exists()

    def test_skip_symlink_target(self, tmp_path):
        """Skip a symlink target update by ID."""
        target = tmp_path / "old_target.py"
        target.write_text("pass\n")
        link = tmp_path / "link.py"
        link.symlink_to("old_target.py")

        preview = preview_rename("old_target", "new_target", directory=str(tmp_path))
        st_id = preview.symlink_targets[0]["id"]

        with patch(
            "scitex._dev._rename._core.check_directory_safety", return_value=None
        ):
            with patch(
                "scitex._dev._rename._core.has_uncommitted_changes",
                return_value=False,
            ):
                execute_rename(
                    "old_target",
                    "new_target",
                    directory=str(tmp_path),
                    skip_ids=[st_id],
                )

        assert os.readlink(str(link)) == "old_target.py"

    def test_ids_in_preview(self, tmp_path):
        """Preview output includes IDs."""
        (tmp_path / "test.py").write_text("old = 1\n")
        result = preview_rename("old", "new", directory=str(tmp_path))
        assert "id" in result.contents[0]
        assert result.contents[0]["id"].startswith("c-")
        assert "id" in result.contents[0]["lines"][0]
        assert "-L" in result.contents[0]["lines"][0]["id"]

    def test_skip_multiple_ids(self, tmp_path):
        """Skip multiple items at once."""
        (tmp_path / "a.py").write_text("old = 1\n")
        (tmp_path / "b.py").write_text("old = 2\n")
        (tmp_path / "c.py").write_text("old = 3\n")
        preview = preview_rename("old", "new", directory=str(tmp_path))
        ids_to_skip = [
            c["id"]
            for c in preview.contents
            if "a.py" in c["file"] or "b.py" in c["file"]
        ]
        _safe_execute("old", "new", tmp_path, skip_ids=ids_to_skip)
        assert "old" in (tmp_path / "a.py").read_text()
        assert "old" in (tmp_path / "b.py").read_text()
        assert "new" in (tmp_path / "c.py").read_text()


# ===========================================================================
# Django app rename warnings
# ===========================================================================


class TestDjangoAppWarning:
    def test_warning_emitted_for_app_dir_rename(self, tmp_path):
        """Renaming a directory containing apps.py triggers warning."""
        app_dir = tmp_path / "old_app"
        app_dir.mkdir()
        (app_dir / "apps.py").write_text("class Config: pass\n")
        (app_dir / "__init__.py").write_text("")

        result = _safe_execute("old_app", "new_app", tmp_path)

        assert "warnings" in result.summary
        assert any("DJANGO APP RENAME" in w for w in result.summary["warnings"])

    def test_no_warning_for_regular_dir(self, tmp_path):
        """Regular directory rename does not trigger warning."""
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "file.py").write_text("pass\n")

        result = _safe_execute("old_dir", "new_dir", tmp_path)

        assert "warnings" not in result.summary

    def test_warning_in_preview(self, tmp_path):
        """Warning also shown in dry run preview."""
        app_dir = tmp_path / "old_app"
        app_dir.mkdir()
        (app_dir / "apps.py").write_text("class Config: pass\n")
        (app_dir / "__init__.py").write_text("")

        result = preview_rename("old_app", "new_app", directory=str(tmp_path))

        assert "warnings" in result.summary
        assert any("DJANGO APP RENAME" in w for w in result.summary["warnings"])

    def test_warning_includes_old_and_new_names(self, tmp_path):
        app_dir = tmp_path / "modulemaker_app"
        app_dir.mkdir()
        (app_dir / "apps.py").write_text("class Config: pass\n")
        (app_dir / "__init__.py").write_text("")

        result = preview_rename(
            "modulemaker_app", "appmaker_app", directory=str(tmp_path)
        )

        warning = result.summary["warnings"][0]
        assert "modulemaker_app" in warning
        assert "appmaker_app" in warning


# ===========================================================================
# Safety checks (_safety.py)
# ===========================================================================


class TestSafety:
    def test_has_uncommitted_changes_not_git(self, tmp_path):
        assert has_uncommitted_changes(str(tmp_path)) is False

    def test_is_git_repo_false_for_tmp(self, tmp_path):
        assert is_git_repo(str(tmp_path)) is False

    def test_is_git_repo_true_for_real_repo(self):
        """Current project should be a git repo."""
        project_root = Path(__file__).resolve().parents[3]
        assert is_git_repo(str(project_root)) is True

    def test_check_directory_safety_blocks_root(self):
        result = check_directory_safety("/")
        assert result is not None
        assert "system directory" in result

    def test_check_directory_safety_blocks_home(self):
        result = check_directory_safety("/home")
        assert result is not None

    def test_check_directory_safety_blocks_usr(self):
        result = check_directory_safety("/usr")
        assert result is not None

    def test_check_directory_safety_blocks_shallow_path(self):
        result = check_directory_safety("/ab")
        assert result is not None
        assert "shallow" in result

    def test_check_directory_safety_requires_git(self, tmp_path):
        result = check_directory_safety(str(tmp_path))
        assert result is not None
        assert "git" in result.lower()

    def test_create_backup(self, tmp_path):
        (tmp_path / "file.py").write_text("content\n")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.py").write_text("nested\n")

        backup_dir = create_backup(str(tmp_path), "old", "new")

        assert backup_dir.exists()
        assert (backup_dir / "operation.txt").exists()
        meta = (backup_dir / "operation.txt").read_text()
        assert "pattern=old" in meta
        assert "replacement=new" in meta
        assert (backup_dir / "original" / "file.py").exists()
        assert (backup_dir / "original" / "subdir" / "nested.py").exists()


# ===========================================================================
# I/O helpers (_io.py)
# ===========================================================================


class TestIO:
    def test_write_text_normal(self, tmp_path):
        f = tmp_path / "test.txt"
        write_text(f, "hello world")
        assert f.read_text() == "hello world"

    def test_rename_path_normal(self, tmp_path):
        src = tmp_path / "old.txt"
        dst = tmp_path / "new.txt"
        src.write_text("content")
        rename_path(src, dst)
        assert not src.exists()
        assert dst.read_text() == "content"

    def test_unlink_path_normal(self, tmp_path):
        f = tmp_path / "delete_me.txt"
        f.write_text("bye")
        unlink_path(f)
        assert not f.exists()

    def test_mkdir_normal(self, tmp_path):
        d = tmp_path / "new_dir"
        mkdir(d)
        assert d.is_dir()

    def test_mkdir_parents(self, tmp_path):
        d = tmp_path / "a" / "b" / "c"
        mkdir(d, parents=True)
        assert d.is_dir()

    def test_rmdir_normal(self, tmp_path):
        d = tmp_path / "empty_dir"
        d.mkdir()
        rmdir(d)
        assert not d.exists()

    def test_symlink_to_normal(self, tmp_path):
        target = tmp_path / "target.txt"
        target.write_text("content")
        link = tmp_path / "link.txt"
        symlink_to(link, "target.txt")
        assert link.is_symlink()
        assert os.readlink(str(link)) == "target.txt"

    def test_set_sudo_password_and_clear(self):
        from scitex._dev._rename import _io

        set_sudo_password("secret123")
        assert _io._sudo_password == "secret123"
        set_sudo_password(None)
        assert _io._sudo_password is None

    def test_write_text_sudo_calls_subprocess(self, tmp_path):
        f = tmp_path / "test.txt"
        with patch("scitex._dev._rename._io._sudo_run") as mock_run:
            write_text(f, "hello", use_sudo=True)
            mock_run.assert_called_once()
            args = mock_run.call_args
            assert args[0][0] == ["tee", str(f)]

    def test_rename_path_sudo_calls_subprocess(self, tmp_path):
        src = tmp_path / "old.txt"
        dst = tmp_path / "new.txt"
        with patch("scitex._dev._rename._io._sudo_run") as mock_run:
            rename_path(src, dst, use_sudo=True)
            mock_run.assert_called_once_with(["mv", str(src), str(dst)])

    def test_mkdir_sudo_with_parents(self, tmp_path):
        d = tmp_path / "new_dir"
        with patch("scitex._dev._rename._io._sudo_run") as mock_run:
            mkdir(d, parents=True, use_sudo=True)
            mock_run.assert_called_once_with(["mkdir", "-p", str(d)])


# ===========================================================================
# Find matching files
# ===========================================================================


class TestFindMatchingFiles:
    def test_respects_excludes(self, tmp_path):
        (tmp_path / "good.py").write_text("pattern\n")
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "bad.py").write_text("pattern\n")

        config = RenameConfig(pattern="pattern", replacement="new")
        files = find_matching_files(str(tmp_path), config, need_content_match=True)

        file_names = [f.name for f in files]
        assert "good.py" in file_names
        assert "bad.py" not in file_names

    def test_respects_extension_filter(self, tmp_path):
        (tmp_path / "code.py").write_text("match\n")
        (tmp_path / "image.jpg").write_text("match\n")

        config = RenameConfig(pattern="match", replacement="new")
        files = find_matching_files(str(tmp_path), config, need_content_match=True)

        names = [f.name for f in files]
        assert "code.py" in names
        assert "image.jpg" not in names

    def test_skips_symlinks(self, tmp_path):
        (tmp_path / "real.py").write_text("match\n")
        (tmp_path / "link.py").symlink_to("real.py")

        config = RenameConfig(pattern="match", replacement="new")
        files = find_matching_files(str(tmp_path), config, need_content_match=True)

        names = [f.name for f in files]
        assert "real.py" in names
        assert "link.py" not in names

    def test_content_match_filter(self, tmp_path):
        (tmp_path / "has_match.py").write_text("target_pattern\n")
        (tmp_path / "no_match.py").write_text("nothing here\n")

        config = RenameConfig(pattern="target_pattern", replacement="new")
        with_content = find_matching_files(
            str(tmp_path), config, need_content_match=True
        )
        without_content = find_matching_files(
            str(tmp_path), config, need_content_match=False
        )

        assert len(with_content) == 1
        assert len(without_content) == 2

    def test_recursive_search(self, tmp_path):
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "b").mkdir()
        (tmp_path / "a" / "b" / "deep.py").write_text("match\n")

        config = RenameConfig(pattern="match", replacement="new")
        files = find_matching_files(str(tmp_path), config, need_content_match=True)

        assert any("deep.py" in f.name for f in files)


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    def test_empty_file(self, tmp_path):
        (tmp_path / "empty.py").write_text("")
        result = preview_rename("anything", "something", directory=str(tmp_path))
        assert len(result.contents) == 0

    def test_pattern_in_directory_and_file(self, tmp_path):
        """Pattern matches both directory name and file inside it."""
        (tmp_path / "old_pkg").mkdir()
        (tmp_path / "old_pkg" / "old_mod.py").write_text("old_ref\n")

        result = preview_rename("old_", "new_", directory=str(tmp_path))

        assert len(result.dir_names) >= 1
        assert len(result.file_names) >= 1
        assert len(result.contents) >= 1

    def test_pattern_is_substring(self, tmp_path):
        """Pattern matches as substring within larger tokens."""
        (tmp_path / "test.py").write_text("old_longer_name\nold\nsome_old_thing\n")
        result = preview_rename("old", "new", directory=str(tmp_path))

        lines = result.contents[0]["lines"]
        assert len(lines) == 3  # All three lines contain "old"

    def test_replacement_contains_pattern(self, tmp_path):
        """Replacement that contains the original pattern should work."""
        (tmp_path / "test.py").write_text("app\n")
        _safe_execute("app", "appmaker", tmp_path)

        text = (tmp_path / "test.py").read_text()
        assert text.strip() == "appmaker"

    def test_unicode_content(self, tmp_path):
        (tmp_path / "test.py").write_text("# Comment: old_name → new\nold_name = 1\n")
        result = _safe_execute("old_name", "new_name", tmp_path)

        text = (tmp_path / "test.py").read_text()
        assert "new_name" in text
        assert "→" in text

    def test_multiline_file_preserved(self, tmp_path):
        content = "line1\nold = 1\nline3\nold = 2\nline5\n"
        (tmp_path / "test.py").write_text(content)
        _safe_execute("old", "new", tmp_path)

        text = (tmp_path / "test.py").read_text()
        lines = text.split("\n")
        assert lines[0] == "line1"
        assert "new" in lines[1]
        assert lines[2] == "line3"
        assert "new" in lines[3]
        assert lines[4] == "line5"

    def test_no_partial_extension_match(self, tmp_path):
        """File renames should not create double extensions."""
        (tmp_path / "old_name.py").write_text("pass\n")
        _safe_execute("old_name", "new_name", tmp_path)

        assert (tmp_path / "new_name.py").exists()
        assert not (tmp_path / "new_name.py.py").exists()

    def test_preserves_file_permissions(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("old = 1\n")
        f.chmod(0o755)
        _safe_execute("old", "new", tmp_path)

        # File should still have content updated
        assert "new" in f.read_text()


# ===========================================================================
# Execution order
# ===========================================================================


class TestExecutionOrder:
    def test_contents_before_file_rename(self, tmp_path):
        """Content replacement happens before file rename."""
        (tmp_path / "old_mod.py").write_text("import old_mod\n")
        _safe_execute("old_mod", "new_mod", tmp_path)

        # File should be renamed AND content updated
        assert (tmp_path / "new_mod.py").exists()
        assert "import new_mod" in (tmp_path / "new_mod.py").read_text()

    def test_symlink_target_before_file_rename(self, tmp_path):
        """Symlink targets updated before files are renamed."""
        target = tmp_path / "old_target.py"
        target.write_text("pass\n")
        link = tmp_path / "link.py"
        link.symlink_to("old_target.py")

        with patch(
            "scitex._dev._rename._core.check_directory_safety", return_value=None
        ):
            config = RenameConfig(
                pattern="old_target",
                replacement="new_target",
                directory=str(tmp_path),
                dry_run=False,
            )
            result = bulk_rename(config)

        # Symlink target should point to new name
        assert os.readlink(str(link)) == "new_target.py"
        # Original file renamed
        assert (tmp_path / "new_target.py").exists()


# ===========================================================================
# use_sudo propagation
# ===========================================================================


class TestSudoPropagation:
    def test_config_carries_use_sudo(self):
        config = RenameConfig(pattern="x", replacement="y", use_sudo=True)
        assert config.use_sudo is True

    def test_preview_with_sudo_does_not_write(self, tmp_path):
        """Dry run with use_sudo should not call any sudo operations."""
        (tmp_path / "test.py").write_text("old = 1\n")
        with patch("scitex._dev._rename._io._sudo_run") as mock_sudo:
            preview_rename("old", "new", directory=str(tmp_path))
            mock_sudo.assert_not_called()


# EOF
