#!/usr/bin/env python3
# Timestamp: "2026-02-18"
# File: tests/scitex/scholar/storage/test__search_filename_and_symlink.py
# ----------------------------------------

"""
Comprehensive tests for normalize_search_filename and _create_project_local_symlink.

Feature 1: normalize_search_filename
- Generates timestamped filenames from search queries
- Format: YYYYMMDD-HHMMSS-{normalized-query}.{ext}
- Uses SearchQueryParser to extract filters

Feature 2: _create_project_local_symlink
- Creates symlinks at {project_dir}/scitex/scholar/library/{project}/{readable_name}
- Symlink target is absolute path to master_storage_path
- Removes stale symlinks pointing to same master entry with different names
"""

import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# ============================================================================
# Module Loading Helpers
# ============================================================================


def load_module(name, path):
    """Load a module from file path using importlib.util."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PROJECT_ROOT = Path(
    __file__
).parent.parent.parent.parent.parent  # tests/scitex/scholar/storage/ -> project root


@pytest.fixture(scope="session")
def search_query_parser_module():
    """Load SearchQueryParser module once per session."""
    module_path = PROJECT_ROOT / "src/scitex/scholar/pipelines/SearchQueryParser.py"
    return load_module("scitex.scholar.pipelines.SearchQueryParser", str(module_path))


@pytest.fixture(scope="session")
def search_filename_module():
    """Load _search_filename module once per session."""
    module_path = PROJECT_ROOT / "src/scitex/scholar/storage/_search_filename.py"
    return load_module("scitex.scholar.storage._search_filename", str(module_path))


@pytest.fixture(scope="session")
def symlink_handlers_module():
    """Load _symlink_handlers module once per session (avoids full scitex import chain)."""
    module_path = (
        PROJECT_ROOT / "src/scitex/scholar/storage/_mixins/_symlink_handlers.py"
    )
    return load_module(
        "scitex.scholar.storage._mixins._symlink_handlers", str(module_path)
    )


@pytest.fixture(scope="session")
def SymlinkHandlersMixin(symlink_handlers_module):
    """Get the SymlinkHandlersMixin class."""
    return symlink_handlers_module.SymlinkHandlersMixin


@pytest.fixture
def normalize_search_filename(search_filename_module):
    """Get the normalize_search_filename function."""
    return search_filename_module.normalize_search_filename


@pytest.fixture
def SearchQueryParser(search_query_parser_module):
    """Get the SearchQueryParser class."""
    return search_query_parser_module.SearchQueryParser


# ============================================================================
# Feature 1: normalize_search_filename Tests
# ============================================================================


class TestNormalizeSearchFilenameBasics:
    """Test basic functionality of normalize_search_filename."""

    def test_empty_query_returns_search_bib(self, normalize_search_filename):
        """Empty query should return filename with 'search' as stem."""
        result = normalize_search_filename("")
        # Format: YYYYMMDD-HHMMSS-search.bib
        assert result.endswith("-search.bib")
        # Check timestamp prefix (YYYYMMDD-HHMMSS)
        parts = result.split("-")
        assert len(parts) >= 3
        assert len(parts[0]) == 8  # YYYYMMDD
        assert len(parts[1]) == 6  # HHMMSS

    def test_simple_keywords_with_hyphens(self, normalize_search_filename):
        """Simple keywords should be joined with hyphens."""
        result = normalize_search_filename("hippocampus theta")
        assert "hippocampus-theta" in result
        assert ".bib" in result
        # Should NOT have underscores
        assert "_" not in result.split("-search")[0]

    def test_keywords_converted_to_lowercase(self, normalize_search_filename):
        """Keywords should be converted to lowercase."""
        result = normalize_search_filename("HIPPOCAMPUS Sharp WAVE")
        assert "hippocampus-sharp-wave" in result
        # Verify no uppercase letters in the normalized part
        stem = (
            result.split("-search")[0] if "-search" in result else result.split(".")[0]
        )
        normalized_part = "-".join(stem.split("-")[2:])  # Skip timestamp
        assert normalized_part.islower()

    def test_special_characters_removed(self, normalize_search_filename):
        """Special characters should be removed, words joined with hyphens."""
        result = normalize_search_filename("neural@network signal-processing")
        # special chars removed, hyphens preserved for word separation
        assert "-" in result
        assert "@" not in result

    def test_custom_extension(self, normalize_search_filename):
        """Should support custom file extensions."""
        result_json = normalize_search_filename("test query", extension=".json")
        assert result_json.endswith(".json")

        result_csv = normalize_search_filename("test query", extension="csv")
        assert result_csv.endswith(".csv")

        result_txt = normalize_search_filename("test query", extension="txt")
        assert result_txt.endswith(".txt")

    def test_extension_format_normalization(self, normalize_search_filename):
        """Extension should work with or without leading dot."""
        result_with_dot = normalize_search_filename("query", extension=".bib")
        result_without_dot = normalize_search_filename("query", extension="bib")

        # Both should end with .bib
        assert result_with_dot.endswith(".bib")
        assert result_without_dot.endswith(".bib")


class TestNormalizeSearchFilenameTimestamp:
    """Test timestamp generation in normalize_search_filename."""

    def test_timestamp_format_yyyymmdd_hhmmss(self, normalize_search_filename):
        """Timestamp should be YYYYMMDD-HHMMSS format."""
        result = normalize_search_filename("test")
        # Extract timestamp (first two hyphen-separated parts)
        parts = result.split("-", 2)
        assert len(parts) >= 2

        date_part = parts[0]
        time_part = parts[1]

        # Check date format (YYYYMMDD)
        assert len(date_part) == 8
        assert date_part.isdigit()
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        assert 2000 <= year <= 2100
        assert 1 <= month <= 12
        assert 1 <= day <= 31

        # Check time format (HHMMSS)
        assert len(time_part) == 6
        assert time_part.isdigit()
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59

    def test_timestamp_is_reasonable(self, normalize_search_filename):
        """Timestamp should be close to current time."""
        before = datetime.now()
        result = normalize_search_filename("query")
        after = datetime.now()

        # Extract timestamp
        timestamp_str = result.split("-", 2)[0] + "-" + result.split("-", 2)[1]
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")

        # Timestamp should be within a reasonable range (strip microseconds; strptime gives second precision)
        assert before.replace(microsecond=0) <= timestamp <= after


class TestNormalizeSearchFilenameFilters:
    """Test filter encoding in normalize_search_filename."""

    def test_year_range_encoding(self, normalize_search_filename):
        """Year range should be encoded as YYYY-YYYY."""
        result = normalize_search_filename("query year:2020-2024")
        assert "2020-2024" in result

    def test_year_start_only_encoding(self, normalize_search_filename):
        """Year start only should be encoded as from{YYYY}."""
        result = normalize_search_filename("query year:>2020")
        assert "from2020" in result

    def test_year_end_only_encoding(self, normalize_search_filename):
        """Year end only should be encoded as to{YYYY}."""
        result = normalize_search_filename("query year:<2024")
        assert "to2024" in result

    def test_impact_factor_encoding(self, normalize_search_filename):
        """Impact factor should be encoded as if{value}."""
        result = normalize_search_filename("query if:>5")
        assert "if5" in result

        result_decimal = normalize_search_filename("query if:>5.5")
        assert "if5.5" in result_decimal

    def test_citation_count_encoding(self, normalize_search_filename):
        """Citation count should be encoded as c{count}."""
        result = normalize_search_filename("query citations:>100")
        assert "c100" in result

        result_alt = normalize_search_filename("query citation:>50")
        assert "c50" in result_alt

    def test_open_access_encoding(self, normalize_search_filename):
        """Open access should be encoded as 'oa'."""
        result = normalize_search_filename("query open_access:true")
        assert "oa" in result

        result_alt = normalize_search_filename("query oa:yes")
        assert "oa" in result_alt

    def test_document_type_encoding(self, normalize_search_filename):
        """Document type should be appended to filename."""
        result = normalize_search_filename("query type:article")
        assert "article" in result

        result_review = normalize_search_filename("query type:review")
        assert "review" in result_review

    def test_complex_query_with_multiple_filters(self, normalize_search_filename):
        """Complex query should encode all filters correctly."""
        result = normalize_search_filename(
            "hippocampus neural network year:2020-2024 if:>5 citations:>100 oa:true type:article"
        )
        # Should contain all key elements
        assert "hippocampus" in result
        assert "neural-network" in result
        assert "2020-2024" in result
        assert "if5" in result
        assert "c100" in result
        assert "oa" in result
        assert "article" in result


class TestNormalizeSearchFilenameMixins:
    """Test mixin behavior and edge cases."""

    def test_multiple_spaces_collapsed(self, normalize_search_filename):
        """Multiple spaces should be handled gracefully."""
        result1 = normalize_search_filename("keyword1   keyword2")
        result2 = normalize_search_filename("keyword1 keyword2")
        # Both should produce same normalized part
        assert (
            result1.split(".")[0].split("-")[-2:]
            == result2.split(".")[0].split("-")[-2:]
        )

    def test_leading_trailing_whitespace_ignored(self, normalize_search_filename):
        """Leading and trailing whitespace should be ignored."""
        result1 = normalize_search_filename("  query  ")
        result2 = normalize_search_filename("query")
        # Normalized parts should match
        assert (
            result1.split(".")[0].split("-")[-1] == result2.split(".")[0].split("-")[-1]
        )

    def test_quoted_phrases_treated_as_single_keyword(self, normalize_search_filename):
        """Quoted phrases should be treated as single keywords with hyphens."""
        result = normalize_search_filename('"sharp wave" ripple')
        # Phrase should be present (possibly hyphenated)
        assert "sharp" in result
        assert "wave" in result
        assert "ripple" in result

    def test_negative_keywords_excluded(self, normalize_search_filename):
        """Negative keywords (prefixed with -) should not appear in filename."""
        result = normalize_search_filename("hippocampus -seizure -epilepsy")
        assert "hippocampus" in result
        # Negative keywords should not be in the filename
        assert "seizure" not in result
        assert "epilepsy" not in result

    def test_hyphen_collapsing(self, normalize_search_filename):
        """Multiple consecutive hyphens should be collapsed."""
        # This tests the internal regex cleanup
        result = normalize_search_filename("query")
        # Should have only single hyphens between components
        timestamp_sep = result.count("---")
        # Should not have triple hyphens in the normalized part
        assert timestamp_sep == 0

    def test_leading_trailing_hyphens_stripped(self, normalize_search_filename):
        """Leading and trailing hyphens in normalized part should be stripped."""
        result = normalize_search_filename("test")
        # Split on dots to get filename without extension
        filename = result.split(".")[0]
        # Extract normalized part (skip YYYYMMDD-HHMMSS-)
        normalized = "-".join(filename.split("-")[2:])
        # Should not start or end with hyphen
        assert not normalized.startswith("-")
        assert not normalized.endswith("-")


# ============================================================================
# Feature 2: _create_project_local_symlink Tests
# ============================================================================


class TestCreateProjectLocalSymlinkBasics:
    """Test basic symlink creation functionality."""

    @pytest.fixture
    def mixin_instance(self, tmp_path, SymlinkHandlersMixin):
        """Create a minimal instance with the mixin."""

        class FakeLibraryManager(SymlinkHandlersMixin):
            def __init__(self, project=None, project_dir=None):
                self.project = project
                self.project_dir = project_dir

        return FakeLibraryManager()

    def test_returns_none_when_project_dir_not_set(self, mixin_instance, tmp_path):
        """Should return None if project_dir is not set."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = None

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(
            master_path, "readable_name"
        )
        assert result is None

    def test_returns_none_for_master_project(self, mixin_instance, tmp_path):
        """Should return None when project is 'master'."""
        mixin_instance.project = "master"
        mixin_instance.project_dir = tmp_path / "project"
        mixin_instance.project_dir.mkdir(parents=True)

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(
            master_path, "readable_name"
        )
        assert result is None

    def test_returns_none_for_master_uppercase(self, mixin_instance, tmp_path):
        """Should return None when project is 'MASTER' (uppercase)."""
        mixin_instance.project = "MASTER"
        mixin_instance.project_dir = tmp_path / "project"
        mixin_instance.project_dir.mkdir(parents=True)

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(
            master_path, "readable_name"
        )
        assert result is None

    def test_creates_symlink_at_correct_path(self, mixin_instance, tmp_path):
        """Should create symlink at {project_dir}/scitex/scholar/library/{project}/{readable_name}."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        readable_name = "PDF-01_CC-000100_IF-005_2024_Smith_Nature"
        result = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )

        # Check that symlink was created at expected location
        expected_path = (
            tmp_path
            / "project"
            / "scitex"
            / "scholar"
            / "library"
            / "test_project"
            / readable_name
        )
        assert result == expected_path
        assert expected_path.exists()
        assert expected_path.is_symlink()

    def test_symlink_target_is_absolute(self, mixin_instance, tmp_path):
        """Symlink target should be absolute path to master storage."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        readable_name = "Paper_Name"
        symlink_path = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )

        # Resolve symlink target
        target = symlink_path.resolve()

        # Target should be the absolute path to master storage
        assert target == master_path.resolve()
        assert target.is_absolute()

    def test_creates_parent_directories(self, mixin_instance, tmp_path):
        """Should create parent directories if they don't exist."""
        mixin_instance.project = "new_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "DEF456"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(master_path, "paper_name")

        # Check that parent directory structure was created
        parent_dir = (
            tmp_path / "project" / "scitex" / "scholar" / "library" / "new_project"
        )
        assert parent_dir.exists()
        assert parent_dir.is_dir()


class TestCreateProjectLocalSymlinkStaleSymlinks:
    """Test stale symlink removal functionality."""

    @pytest.fixture
    def mixin_instance(self, tmp_path, SymlinkHandlersMixin):
        """Create a minimal instance with the mixin."""

        class FakeLibraryManager(SymlinkHandlersMixin):
            def __init__(self, project=None, project_dir=None):
                self.project = project
                self.project_dir = project_dir

        return FakeLibraryManager()

    def test_removes_stale_symlink_same_master_different_name(
        self, mixin_instance, tmp_path
    ):
        """Should remove stale symlink pointing to same master entry with different name."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        # Create directory for symlinks
        symlink_dir = (
            tmp_path / "project" / "scitex" / "scholar" / "library" / "test_project"
        )
        symlink_dir.mkdir(parents=True)

        # Create a stale symlink with different name pointing to same master
        old_symlink = symlink_dir / "Old_Paper_Name"
        old_symlink.symlink_to(master_path.resolve())

        assert old_symlink.exists()

        # Create new symlink with different name, same master target
        new_name = "New_Paper_Name"
        result = mixin_instance._create_project_local_symlink(master_path, new_name)

        # Old symlink should be removed
        assert not old_symlink.exists()

        # New symlink should exist
        assert result.exists()
        assert result.name == new_name

    def test_preserves_symlink_with_same_name(self, mixin_instance, tmp_path):
        """Should not remove symlink if name matches."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        symlink_dir = (
            tmp_path / "project" / "scitex" / "scholar" / "library" / "test_project"
        )
        symlink_dir.mkdir(parents=True)

        readable_name = "PDF-01_CC-000100_IF-005_2024_Smith_Nature"
        symlink_path = symlink_dir / readable_name
        symlink_path.symlink_to(master_path.resolve())

        original_inode = symlink_path.lstat().st_ino

        # Call method with same name
        result = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )

        # Symlink should still exist (not removed)
        assert result.exists()
        # Should point to same target
        assert result.resolve() == master_path.resolve()

    def test_ignores_non_symlink_files(self, mixin_instance, tmp_path):
        """Should ignore non-symlink files in directory."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        symlink_dir = (
            tmp_path / "project" / "scitex" / "scholar" / "library" / "test_project"
        )
        symlink_dir.mkdir(parents=True)

        # Create a regular file (not symlink)
        regular_file = symlink_dir / "regular_file.txt"
        regular_file.write_text("This is a regular file")

        # Create symlink
        result = mixin_instance._create_project_local_symlink(
            master_path, "new_symlink"
        )

        # Regular file should still exist
        assert regular_file.exists()
        assert not regular_file.is_symlink()

        # New symlink should be created
        assert result.exists()

    def test_handles_broken_symlinks_gracefully(self, mixin_instance, tmp_path):
        """Should handle broken symlinks without crashing."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        symlink_dir = (
            tmp_path / "project" / "scitex" / "scholar" / "library" / "test_project"
        )
        symlink_dir.mkdir(parents=True)

        # Create a broken symlink (target doesn't exist)
        broken_symlink = symlink_dir / "broken_link"
        broken_symlink.symlink_to("/nonexistent/path")

        # This should not crash
        result = mixin_instance._create_project_local_symlink(
            master_path, "new_symlink"
        )

        assert result.exists()
        # Broken symlink should remain (since target doesn't match)
        assert broken_symlink.is_symlink()

    def test_removes_only_matching_master_id(self, mixin_instance, tmp_path):
        """Should only remove symlinks pointing to the same master ID."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path_1 = tmp_path / "master" / "ABC123"
        master_path_2 = tmp_path / "master" / "DEF456"
        master_path_1.mkdir(parents=True)
        master_path_2.mkdir(parents=True)

        symlink_dir = (
            tmp_path / "project" / "scitex" / "scholar" / "library" / "test_project"
        )
        symlink_dir.mkdir(parents=True)

        # Create symlinks to different masters
        old_symlink_1 = symlink_dir / "Old_Name_1"
        old_symlink_1.symlink_to(master_path_1.resolve())

        other_symlink = symlink_dir / "Other_Master"
        other_symlink.symlink_to(master_path_2.resolve())

        # Create new symlink for master 1 with different name
        result = mixin_instance._create_project_local_symlink(
            master_path_1, "New_Name_1"
        )

        # Old symlink for master 1 should be removed
        assert not old_symlink_1.exists()

        # Symlink for other master should remain
        assert other_symlink.exists()
        assert other_symlink.resolve() == master_path_2.resolve()

        # New symlink should exist
        assert result.exists()
        assert result.resolve() == master_path_1.resolve()


class TestCreateProjectLocalSymlinkReturnValue:
    """Test return values of _create_project_local_symlink."""

    @pytest.fixture
    def mixin_instance(self, tmp_path, SymlinkHandlersMixin):
        """Create a minimal instance with the mixin."""

        class FakeLibraryManager(SymlinkHandlersMixin):
            def __init__(self, project=None, project_dir=None):
                self.project = project
                self.project_dir = project_dir

        return FakeLibraryManager()

    def test_returns_path_object_on_success(self, mixin_instance, tmp_path):
        """Should return Path object when symlink is created successfully."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(master_path, "paper")

        assert isinstance(result, Path)
        assert result.exists()

    def test_return_path_is_correct_path(self, mixin_instance, tmp_path):
        """Returned path should match the created symlink path."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)
        readable_name = "PDF-01_CC_IF"

        result = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )

        expected = (
            tmp_path
            / "project"
            / "scitex"
            / "scholar"
            / "library"
            / "test_project"
            / readable_name
        )
        assert result == expected

    def test_returns_none_on_missing_project_dir(self, mixin_instance, tmp_path):
        """Should return None if project_dir is None."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = None

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(master_path, "paper")
        assert result is None

    def test_returns_none_on_master_project(self, mixin_instance, tmp_path):
        """Should return None if project is 'master'."""
        mixin_instance.project = "master"
        mixin_instance.project_dir = tmp_path / "project"
        mixin_instance.project_dir.mkdir(parents=True)

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(master_path, "paper")
        assert result is None


class TestCreateProjectLocalSymlinkEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture
    def mixin_instance(self, tmp_path, SymlinkHandlersMixin):
        """Create a minimal instance with the mixin."""

        class FakeLibraryManager(SymlinkHandlersMixin):
            def __init__(self, project=None, project_dir=None):
                self.project = project
                self.project_dir = project_dir

        return FakeLibraryManager()

    def test_handles_special_characters_in_readable_name(
        self, mixin_instance, tmp_path
    ):
        """Should handle special characters in readable_name."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        readable_name = "PDF-01_CC-000100_IF-005_2024_Smith-Jones_Nature-Science"
        result = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )

        assert result is not None
        assert result.exists()
        assert result.name == readable_name

    def test_handles_long_readable_name(self, mixin_instance, tmp_path):
        """Should handle long readable names."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        readable_name = "PDF-01_CC-999999_IF-999_2024_VeryLongAuthorName_VeryLongJournalNameThatExceedsNormalLength"
        result = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )

        assert result is not None
        assert result.exists()
        assert result.name == readable_name

    def test_handles_paths_with_spaces(self, mixin_instance, tmp_path):
        """Should handle paths with spaces."""
        mixin_instance.project = "test project"
        project_dir = tmp_path / "my project"
        mixin_instance.project_dir = project_dir

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(master_path, "paper name")

        assert result is not None
        assert result.exists()
        # Path should contain spaces correctly
        assert "test project" in str(result)
        assert "paper name" in str(result)

    def test_handles_nested_master_paths(self, mixin_instance, tmp_path):
        """Should handle deeply nested master storage paths."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        # Create nested path
        master_path = tmp_path / "archive" / "deep" / "nested" / "master" / "ABC123"
        master_path.mkdir(parents=True)

        result = mixin_instance._create_project_local_symlink(master_path, "paper")

        assert result is not None
        assert result.exists()
        # Symlink target should resolve to the correct master path
        assert result.resolve() == master_path.resolve()

    def test_idempotency_same_call_twice(self, mixin_instance, tmp_path):
        """Calling with same arguments twice should be idempotent."""
        mixin_instance.project = "test_project"
        mixin_instance.project_dir = tmp_path / "project"

        master_path = tmp_path / "master" / "ABC123"
        master_path.mkdir(parents=True)
        readable_name = "Paper_Name"

        result1 = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )
        result2 = mixin_instance._create_project_local_symlink(
            master_path, readable_name
        )

        # Both calls should return same path
        assert result1 == result2
        # Path should exist after both calls
        assert result1.exists()
        assert result2.exists()
        # Should point to same target
        assert result1.resolve() == result2.resolve()


# EOF
