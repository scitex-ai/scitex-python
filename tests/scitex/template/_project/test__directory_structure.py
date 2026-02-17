#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__directory_structure.py
"""Tests for scitex.template._project._directory_structure."""

import pytest

from scitex.template._project._directory_structure import (
    PROJECT_STRUCTURE,
    build_directory_tree,
)


class TestProjectStructure:
    def test_has_expected_dirs(self):
        expected = {"config", "data", "scripts", "docs", "results", "temp"}
        assert expected == set(PROJECT_STRUCTURE.keys())


class TestBuildDirectoryTree:
    def test_creates_top_level_dirs(self, tmp_path):
        build_directory_tree(str(tmp_path))
        for d in PROJECT_STRUCTURE:
            assert (tmp_path / d).is_dir()

    def test_custom_structure(self, tmp_path):
        custom = {"src": [], "tests": [], "docs": []}
        build_directory_tree(str(tmp_path), structure=custom)
        assert (tmp_path / "src").is_dir()
        assert (tmp_path / "tests").is_dir()

    def test_nested_structure(self, tmp_path):
        nested = {"data": {"raw": ["csv", "json"]}}
        build_directory_tree(str(tmp_path), structure=nested)
        assert (tmp_path / "data" / "raw" / "csv").is_dir()
        assert (tmp_path / "data" / "raw" / "json").is_dir()


# EOF
