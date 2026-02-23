#!/usr/bin/env python3
# Timestamp: 2026-02-23
# File: tests/container/test_status.py

"""Tests for scitex.container._status module."""

import hashlib
import time
from pathlib import Path
from unittest.mock import patch

import pytest


class TestStatus:
    """Tests for status function."""

    def test_status_returns_list(self, tmp_path):
        """Test status returns a list of dicts."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        (containers_dir / "image-a.def").write_text("Bootstrap: docker\n")

        result = status(containers_dir=containers_dir)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_status_empty_dir(self, tmp_path):
        """Test status returns empty list when no .def files exist."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()

        result = status(containers_dir=containers_dir)

        assert result == []

    def test_status_multiple_defs(self, tmp_path):
        """Test status lists all .def files."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        (containers_dir / "image-a.def").write_text("Bootstrap: docker\n")
        (containers_dir / "image-b.def").write_text("Bootstrap: library\n")
        (containers_dir / "image-c.def").write_text("Bootstrap: shub\n")

        result = status(containers_dir=containers_dir)

        assert len(result) == 3
        names = {r["name"] for r in result}
        assert names == {"image-a", "image-b", "image-c"}

    def test_status_dict_keys(self, tmp_path):
        """Test each status entry has all expected keys."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        (containers_dir / "test.def").write_text("Bootstrap: docker\n")

        result = status(containers_dir=containers_dir)
        entry = result[0]

        expected_keys = {
            "name",
            "def_path",
            "sif_path",
            "sif_size",
            "sif_date",
            "hash_current",
            "hash_stored",
            "needs_rebuild",
        }
        assert set(entry.keys()) == expected_keys

    def test_status_without_sif(self, tmp_path):
        """Test status when no .sif file exists."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        (containers_dir / "test.def").write_text("Bootstrap: docker\n")

        result = status(containers_dir=containers_dir)
        entry = result[0]

        assert entry["name"] == "test"
        assert entry["sif_path"] is None
        assert entry["sif_size"] is None
        assert entry["sif_date"] is None
        assert entry["needs_rebuild"] is True

    def test_status_with_sif_and_matching_hash(self, tmp_path):
        """Test status when .sif exists and hash matches."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test.def"
        def_file.write_text("Bootstrap: docker\n")

        sif_file = containers_dir / "test.sif"
        sif_file.write_bytes(b"fake sif content")

        current_hash = hashlib.sha256(def_file.read_bytes()).hexdigest()
        hash_file = containers_dir / ".def-hash"
        hash_file.write_text(current_hash + "\n")

        result = status(containers_dir=containers_dir)
        entry = result[0]

        assert entry["sif_path"] == str(sif_file)
        assert entry["sif_size"] is not None
        assert entry["sif_date"] is not None
        assert entry["needs_rebuild"] is False

    def test_status_with_sif_and_mismatched_hash(self, tmp_path):
        """Test status when .sif exists but hash does not match."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test.def"
        def_file.write_text("Bootstrap: docker\n")

        sif_file = containers_dir / "test.sif"
        sif_file.write_bytes(b"fake sif content")

        hash_file = containers_dir / ".def-hash"
        hash_file.write_text("stale_old_hash\n")

        result = status(containers_dir=containers_dir)
        entry = result[0]

        assert entry["sif_path"] == str(sif_file)
        assert entry["needs_rebuild"] is True

    def test_status_with_sif_no_hash_file(self, tmp_path):
        """Test status when .sif exists but no hash file."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test.def"
        def_file.write_text("Bootstrap: docker\n")

        sif_file = containers_dir / "test.sif"
        sif_file.write_bytes(b"fake sif content")

        result = status(containers_dir=containers_dir)
        entry = result[0]

        assert entry["hash_stored"] is None
        assert entry["needs_rebuild"] is True

    def test_status_hash_current_is_sha256(self, tmp_path):
        """Test hash_current is a valid SHA256 hex digest."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test.def"
        content = "Bootstrap: docker\nFrom: ubuntu:22.04\n"
        def_file.write_text(content)

        result = status(containers_dir=containers_dir)
        entry = result[0]

        expected_hash = hashlib.sha256(content.encode()).hexdigest()
        assert entry["hash_current"] == expected_hash
        assert len(entry["hash_current"]) == 64

    def test_status_uses_find_containers_dir(self):
        """Test status calls find_containers_dir when no arg given."""
        from scitex.container._status import status

        with patch("scitex.container._status.find_containers_dir") as mock_find:
            mock_find.side_effect = FileNotFoundError("no dir")
            with pytest.raises(FileNotFoundError):
                status()
            mock_find.assert_called_once()

    def test_status_sorted_by_name(self, tmp_path):
        """Test status entries are sorted by .def filename."""
        from scitex.container._status import status

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        (containers_dir / "z-image.def").write_text("Bootstrap: docker\n")
        (containers_dir / "a-image.def").write_text("Bootstrap: docker\n")
        (containers_dir / "m-image.def").write_text("Bootstrap: docker\n")

        result = status(containers_dir=containers_dir)
        names = [r["name"] for r in result]

        assert names == sorted(names)


class TestHumanSize:
    """Tests for _human_size helper."""

    def test_bytes(self):
        """Test human-readable for small byte values."""
        from scitex.container._status import _human_size

        assert _human_size(100) == "100.0 B"

    def test_kilobytes(self):
        """Test human-readable for kilobyte values."""
        from scitex.container._status import _human_size

        assert _human_size(1024) == "1.0 KB"

    def test_megabytes(self):
        """Test human-readable for megabyte values."""
        from scitex.container._status import _human_size

        assert _human_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self):
        """Test human-readable for gigabyte values."""
        from scitex.container._status import _human_size

        assert _human_size(1024**3) == "1.0 GB"

    def test_terabytes(self):
        """Test human-readable for terabyte values."""
        from scitex.container._status import _human_size

        assert _human_size(1024**4) == "1.0 TB"

    def test_zero(self):
        """Test human-readable for zero bytes."""
        from scitex.container._status import _human_size

        assert _human_size(0) == "0.0 B"

    def test_fractional_kb(self):
        """Test human-readable for fractional kilobytes."""
        from scitex.container._status import _human_size

        result = _human_size(1536)  # 1.5 KB
        assert result == "1.5 KB"


class TestStatusHashFile:
    """Tests for _hash_file helper in status module."""

    def test_hash_matches_build_module(self, tmp_path):
        """Test _hash_file in status produces same result as manual SHA256."""
        from scitex.container._status import _hash_file

        test_file = tmp_path / "test.def"
        content = b"Bootstrap: docker\nFrom: ubuntu:22.04\n"
        test_file.write_bytes(content)

        result = _hash_file(test_file)
        expected = hashlib.sha256(content).hexdigest()
        assert result == expected


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
