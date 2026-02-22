#!/usr/bin/env python3
# Timestamp: 2026-02-19
# File: tests/scitex/project/_mcp/test_handlers.py
"""Tests for project file operation MCP handlers."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


# Point ALLOWED_DATA_ROOT to a temp dir for all tests
@pytest.fixture(autouse=True)
def allow_tmp_root(tmp_path, monkeypatch):
    """Allow handlers to operate under tmp_path."""
    monkeypatch.setenv("SCITEX_PROJECT_DATA_ROOT", str(tmp_path))
    # Reload module so the env var is picked up
    import importlib

    import scitex.project._mcp.handlers as h

    importlib.reload(h)
    return tmp_path


@pytest.fixture()
def project_root(tmp_path):
    """Create a minimal fake project directory structure."""
    root = tmp_path / "test-user" / "proj" / "my-project"
    root.mkdir(parents=True)
    (root / "README.md").write_text("# My Project\nHello world.")
    (root / "scripts").mkdir()
    (root / "scripts" / "analysis.py").write_text("import scitex as stx\nprint('hi')")
    (root / "data").mkdir()
    (root / "data" / "results.csv").write_text("col1,col2\n1,2\n3,4")
    return root


class TestResolvePathSecurity:
    """Security: path traversal must be rejected."""

    def test_path_traversal_rejected(self, project_root):
        import scitex.project._mcp.handlers as h

        with pytest.raises(ValueError, match="traversal"):
            h._resolve_safe(str(project_root), "../other-project/secret.txt")

    def test_root_outside_allowed_rejected(self, tmp_path):
        import scitex.project._mcp.handlers as h

        with pytest.raises(ValueError, match="allowed data root"):
            h._resolve_safe("/etc", "passwd")

    def test_valid_path_resolves(self, project_root):
        import scitex.project._mcp.handlers as h

        target = h._resolve_safe(str(project_root), "scripts/analysis.py")
        assert target.exists()
        assert target.name == "analysis.py"

    def test_root_itself_resolves(self, project_root):
        import scitex.project._mcp.handlers as h

        target = h._resolve_safe(str(project_root), ".")
        assert target == project_root.resolve()


class TestListFilesHandler:
    @pytest.mark.asyncio
    async def test_lists_project_root(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.list_files_handler(str(project_root))
        assert result["success"] is True
        names = [e["name"] for e in result["tree"]]
        assert "README.md" in names
        assert "scripts" in names
        assert "data" in names

    @pytest.mark.asyncio
    async def test_lists_subdirectory(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.list_files_handler(str(project_root), "scripts")
        assert result["success"] is True
        names = [e["name"] for e in result["tree"]]
        assert "analysis.py" in names

    @pytest.mark.asyncio
    async def test_nonexistent_path_fails(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.list_files_handler(str(project_root), "nonexistent")
        assert result["success"] is False
        assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_file_path_fails(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.list_files_handler(str(project_root), "README.md")
        assert result["success"] is False
        assert "Not a directory" in result["error"]

    @pytest.mark.asyncio
    async def test_hidden_files_excluded(self, project_root):
        import scitex.project._mcp.handlers as h

        (project_root / ".hidden").write_text("secret")
        result = await h.list_files_handler(str(project_root))
        names = [e["name"] for e in result["tree"]]
        assert ".hidden" not in names

    @pytest.mark.asyncio
    async def test_max_depth_respected(self, project_root):
        import scitex.project._mcp.handlers as h

        # With depth=1, scripts/ children should not appear
        result = await h.list_files_handler(str(project_root), max_depth=1)
        assert result["success"] is True
        scripts_entry = next(e for e in result["tree"] if e["name"] == "scripts")
        assert scripts_entry["children"] == []


class TestReadFileHandler:
    @pytest.mark.asyncio
    async def test_reads_existing_file(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.read_file_handler(str(project_root), "README.md")
        assert result["success"] is True
        assert "Hello world" in result["content"]
        assert result["truncated"] is False

    @pytest.mark.asyncio
    async def test_reads_nested_file(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.read_file_handler(str(project_root), "scripts/analysis.py")
        assert result["success"] is True
        assert "import scitex" in result["content"]

    @pytest.mark.asyncio
    async def test_missing_file_fails(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.read_file_handler(str(project_root), "does_not_exist.py")
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_large_file_truncated(self, project_root):
        import scitex.project._mcp.handlers as h

        big = project_root / "big.txt"
        big.write_text("x" * 100_000)
        result = await h.read_file_handler(str(project_root), "big.txt")
        assert result["success"] is True
        assert result["truncated"] is True
        assert len(result["content"]) <= 65536

    @pytest.mark.asyncio
    async def test_path_traversal_rejected(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.read_file_handler(str(project_root), "../other/secret")
        assert result["success"] is False


class TestWriteFileHandler:
    @pytest.mark.asyncio
    async def test_creates_new_file(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.write_file_handler(
            str(project_root), "new_script.py", "print('hello')"
        )
        assert result["success"] is True
        assert (project_root / "new_script.py").read_text() == "print('hello')"

    @pytest.mark.asyncio
    async def test_overwrites_existing_file(self, project_root):
        import scitex.project._mcp.handlers as h

        await h.write_file_handler(str(project_root), "README.md", "Updated content")
        result = await h.read_file_handler(str(project_root), "README.md")
        assert "Updated content" in result["content"]

    @pytest.mark.asyncio
    async def test_creates_parent_dirs(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.write_file_handler(
            str(project_root), "nested/deep/file.txt", "content"
        )
        assert result["success"] is True
        assert (project_root / "nested" / "deep" / "file.txt").exists()

    @pytest.mark.asyncio
    async def test_path_traversal_rejected(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.write_file_handler(str(project_root), "../escape.txt", "bad")
        assert result["success"] is False


class TestSearchFilesHandler:
    @pytest.mark.asyncio
    async def test_search_by_name_glob(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.search_files_handler(str(project_root), name_pattern="*.py")
        assert result["success"] is True
        assert result["count"] >= 1
        assert all(m["path"].endswith(".py") for m in result["matches"])

    @pytest.mark.asyncio
    async def test_search_by_content(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.search_files_handler(
            str(project_root), content_pattern="Hello world"
        )
        assert result["success"] is True
        assert result["count"] >= 1
        paths = [m["path"] for m in result["matches"]]
        assert any("README" in p for p in paths)

    @pytest.mark.asyncio
    async def test_search_by_name_and_content(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.search_files_handler(
            str(project_root), name_pattern="*.py", content_pattern="import scitex"
        )
        assert result["success"] is True
        assert result["count"] >= 1

    @pytest.mark.asyncio
    async def test_no_pattern_fails(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.search_files_handler(str(project_root))
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_no_match_returns_empty(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.search_files_handler(
            str(project_root), content_pattern="xyzzy_not_present"
        )
        assert result["success"] is True
        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_content_match_includes_line_preview(self, project_root):
        import scitex.project._mcp.handlers as h

        result = await h.search_files_handler(
            str(project_root), content_pattern="import scitex"
        )
        assert result["success"] is True
        match = result["matches"][0]
        assert "line" in match
        assert "preview" in match
        assert match["line"] > 0

    @pytest.mark.asyncio
    async def test_hidden_files_excluded(self, project_root):
        import scitex.project._mcp.handlers as h

        (project_root / ".secret.py").write_text("password = 'hunter2'")
        result = await h.search_files_handler(
            str(project_root), content_pattern="hunter2"
        )
        assert result["count"] == 0


# EOF
