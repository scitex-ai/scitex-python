#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: tests/scitex/_dev/test__rename.py

"""Tests for scitex._dev._rename bulk rename utility."""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

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
from scitex._dev._rename._safety import has_uncommitted_changes

# ---------------------------------------------------------------------------
# RenameConfig defaults
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


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

    def test_matches_include_extensions(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert matches_include_extensions(Path("file.py"), config) is True
        assert matches_include_extensions(Path("file.txt"), config) is True
        assert matches_include_extensions(Path("file.jpg"), config) is False

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
        """db_table lines must remain protected."""
        assert (
            is_django_protected_line("    db_table = 'old_table'", "old_table") is True
        )

    def test_is_src_excluded(self):
        config = RenameConfig(pattern="x", replacement="y")
        assert is_src_excluded("db_table='test'", config) is True
        assert is_src_excluded("normal code here", config) is False


# ---------------------------------------------------------------------------
# Preview rename (dry run)
# ---------------------------------------------------------------------------


class TestPreviewRename:
    def test_preview_file_contents(self, tmp_path):
        (tmp_path / "test.py").write_text("old_name = 1\nold_name = 2\n")
        result = preview_rename("old_name", "new_name", directory=str(tmp_path))

        assert result.dry_run is True
        assert len(result.contents) == 1
        assert result.contents[0]["matches"] == 2
        # File should be unchanged
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
        # File should still exist with old name
        assert (tmp_path / "old_module.py").exists()

    def test_preview_directory_names(self, tmp_path):
        (tmp_path / "old_pkg").mkdir()
        (tmp_path / "old_pkg" / "__init__.py").write_text("")
        result = preview_rename("old_pkg", "new_pkg", directory=str(tmp_path))

        assert len(result.dir_names) == 1
        # Directory should still exist with old name
        assert (tmp_path / "old_pkg").exists()


# ---------------------------------------------------------------------------
# Execute rename (live)
# ---------------------------------------------------------------------------


class TestExecuteRename:
    def test_execute_file_contents(self, tmp_path):
        (tmp_path / "test.py").write_text("old_name = 1\n")
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                result = execute_rename("old_name", "new_name", directory=str(tmp_path))

        assert result.dry_run is False
        assert "new_name" in (tmp_path / "test.py").read_text()

    def test_execute_file_names(self, tmp_path):
        (tmp_path / "old_mod.py").write_text("pass\n")
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                execute_rename("old_mod", "new_mod", directory=str(tmp_path))

        assert not (tmp_path / "old_mod.py").exists()
        assert (tmp_path / "new_mod.py").exists()

    def test_execute_directory_names(self, tmp_path):
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "file.py").write_text("pass\n")
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                execute_rename("old_dir", "new_dir", directory=str(tmp_path))

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
        # File should be unchanged
        assert "old" in (tmp_path / "test.py").read_text()

    def test_execute_deepest_dir_first(self, tmp_path):
        (tmp_path / "old_a").mkdir()
        (tmp_path / "old_a" / "old_b").mkdir()
        (tmp_path / "old_a" / "old_b" / "file.py").write_text("pass\n")
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                result = execute_rename("old_", "new_", directory=str(tmp_path))

        assert (tmp_path / "new_a" / "new_b" / "file.py").exists()
        assert len(result.dir_names) == 2


# ---------------------------------------------------------------------------
# Django-safe mode
# ---------------------------------------------------------------------------


class TestDjangoSafe:
    def test_protects_db_table(self, tmp_path):
        content = "class Meta:\n    db_table = 'old_table'\nold_table_var = 1\n"
        (tmp_path / "models.py").write_text(content)
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                execute_rename("old_table", "new_table", directory=str(tmp_path))

        text = (tmp_path / "models.py").read_text()
        assert "db_table = 'old_table'" in text  # Protected (django-safe)
        assert "new_table_var = 1" in text  # Replaced (normal code)

    def test_no_django_safe(self, tmp_path):
        content = "db_table = 'old_table'\n"
        (tmp_path / "models.py").write_text(content)
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                execute_rename(
                    "old_table",
                    "new_table",
                    directory=str(tmp_path),
                    django_safe=False,
                )

        text = (tmp_path / "models.py").read_text()
        assert "new_table" in text  # Not protected


# ---------------------------------------------------------------------------
# Symlinks
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


class TestUtils:
    def test_has_uncommitted_changes_not_git(self, tmp_path):
        assert has_uncommitted_changes(str(tmp_path)) is False

    def test_find_matching_files_respects_excludes(self, tmp_path):
        (tmp_path / "good.py").write_text("pattern\n")
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "bad.py").write_text("pattern\n")

        config = RenameConfig(pattern="pattern", replacement="new")
        files = find_matching_files(str(tmp_path), config, need_content_match=True)

        file_names = [f.name for f in files]
        assert "good.py" in file_names
        assert "bad.py" not in file_names


# ---------------------------------------------------------------------------
# Collision detection
# ---------------------------------------------------------------------------


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

    def test_execute_blocks_on_collision(self, tmp_path):
        (tmp_path / "old_mod.py").write_text("pass\n")
        (tmp_path / "new_mod.py").write_text("existing\n")

        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                result = execute_rename("old_mod", "new_mod", directory=str(tmp_path))

        assert result.error is not None
        assert "Collision" in result.error
        # Files should be unchanged
        assert (tmp_path / "old_mod.py").exists()
        assert "existing" in (tmp_path / "new_mod.py").read_text()

    def test_collision_summary_count(self, tmp_path):
        (tmp_path / "old_a.py").write_text("pass\n")
        (tmp_path / "new_a.py").write_text("existing\n")
        (tmp_path / "old_b.py").write_text("pass\n")
        (tmp_path / "new_b.py").write_text("existing\n")

        result = preview_rename("old_", "new_", directory=str(tmp_path))

        assert result.summary["collisions"] == 2


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Skip IDs
# ---------------------------------------------------------------------------


class TestSkipIds:
    def test_skip_file_level(self, tmp_path):
        """Skip all changes in a specific file by file-level ID."""
        (tmp_path / "a.py").write_text("old = 1\n")
        (tmp_path / "b.py").write_text("old = 2\n")
        # Preview to get IDs
        preview = preview_rename("old", "new", directory=str(tmp_path))
        # Find ID for a.py
        a_id = [c["id"] for c in preview.contents if "a.py" in c["file"]][0]
        # Execute with skip
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                execute_rename("old", "new", directory=str(tmp_path), skip_ids=[a_id])
        assert "old" in (tmp_path / "a.py").read_text()  # Skipped
        assert "new" in (tmp_path / "b.py").read_text()  # Changed

    def test_skip_line_level(self, tmp_path):
        """Skip a specific line by line-level ID."""
        (tmp_path / "test.py").write_text("old_a = 1\nkeep = 2\nold_b = 3\n")
        preview = preview_rename("old", "new", directory=str(tmp_path))
        # Get line-level ID for line 1
        file_result = preview.contents[0]
        line_id = [l["id"] for l in file_result["lines"] if l["line_num"] == 1][0]
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                execute_rename(
                    "old", "new", directory=str(tmp_path), skip_ids=[line_id]
                )
        text = (tmp_path / "test.py").read_text()
        assert "old_a" in text  # Line 1 skipped
        assert "new_b" in text  # Line 3 changed

    def test_skip_dir_rename(self, tmp_path):
        """Skip a directory rename by ID."""
        (tmp_path / "old_dir").mkdir()
        (tmp_path / "old_dir" / "file.py").write_text("pass\n")
        preview = preview_rename("old_dir", "new_dir", directory=str(tmp_path))
        dir_id = preview.dir_names[0]["id"]
        with patch(
            "scitex._dev._rename._core.has_uncommitted_changes", return_value=False
        ):
            with patch(
                "scitex._dev._rename._core.check_directory_safety", return_value=None
            ):
                execute_rename(
                    "old_dir",
                    "new_dir",
                    directory=str(tmp_path),
                    skip_ids=[dir_id],
                )
        assert (tmp_path / "old_dir").exists()  # Not renamed

    def test_ids_in_preview(self, tmp_path):
        """Preview output includes IDs."""
        (tmp_path / "test.py").write_text("old = 1\n")
        result = preview_rename("old", "new", directory=str(tmp_path))
        assert "id" in result.contents[0]
        assert result.contents[0]["id"].startswith("c-")
        assert "id" in result.contents[0]["lines"][0]
        assert "-L" in result.contents[0]["lines"][0]["id"]


# EOF
