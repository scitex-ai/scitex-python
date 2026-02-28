#!/usr/bin/env python3
# Timestamp: 2026-02-23
# File: tests/container/test_build.py

"""Tests for scitex.container._build module."""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestBuild:
    """Tests for build function."""

    def test_build_creates_sif(self, tmp_path):
        """Test build runs apptainer build and returns sif path."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch(
                    "scitex.container._build.subprocess.run", return_value=mock_result
                ) as mock_run:
                    result = build(def_name="test-image")

        assert result == containers_dir / "test-image.sif"
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "apptainer" in call_args
        assert "build" in call_args

    def test_build_writes_hash_file(self, tmp_path):
        """Test build writes .def-hash after successful build."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch(
                    "scitex.container._build.subprocess.run", return_value=mock_result
                ):
                    build(def_name="test-image")

        hash_file = containers_dir / ".def-hash"
        assert hash_file.exists()
        expected_hash = hashlib.sha256(def_file.read_bytes()).hexdigest()
        assert hash_file.read_text().strip() == expected_hash

    def test_build_skips_when_hash_matches(self, tmp_path):
        """Test build skips rebuild when .def hash matches stored hash."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        # Pre-create the sif file and hash file
        sif_file = containers_dir / "test-image.sif"
        sif_file.write_text("fake sif content")
        current_hash = hashlib.sha256(def_file.read_bytes()).hexdigest()
        hash_file = containers_dir / ".def-hash"
        hash_file.write_text(current_hash + "\n")

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch("scitex.container._build.subprocess.run") as mock_run:
                    result = build(def_name="test-image")

        # subprocess.run should NOT have been called
        mock_run.assert_not_called()
        assert result == sif_file

    def test_build_rebuilds_when_hash_differs(self, tmp_path):
        """Test build rebuilds when .def content has changed."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        # Pre-create sif and hash with old hash
        sif_file = containers_dir / "test-image.sif"
        sif_file.write_text("fake sif content")
        hash_file = containers_dir / ".def-hash"
        hash_file.write_text("old_stale_hash\n")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch(
                    "scitex.container._build.subprocess.run", return_value=mock_result
                ) as mock_run:
                    result = build(def_name="test-image")

        mock_run.assert_called_once()
        assert result == sif_file

    def test_build_force_ignores_hash(self, tmp_path):
        """Test build with force=True rebuilds even when hash matches."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        # Pre-create sif and matching hash
        sif_file = containers_dir / "test-image.sif"
        sif_file.write_text("fake sif content")
        current_hash = hashlib.sha256(def_file.read_bytes()).hexdigest()
        hash_file = containers_dir / ".def-hash"
        hash_file.write_text(current_hash + "\n")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch(
                    "scitex.container._build.subprocess.run", return_value=mock_result
                ) as mock_run:
                    result = build(def_name="test-image", force=True)

        mock_run.assert_called_once()
        assert result == sif_file

    def test_build_raises_on_missing_def(self, tmp_path):
        """Test build raises FileNotFoundError if .def file is missing."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with pytest.raises(
                    FileNotFoundError, match="Definition file not found"
                ):
                    build(def_name="nonexistent")

    def test_build_raises_on_nonzero_exit(self, tmp_path):
        """Test build raises RuntimeError when subprocess returns non-zero."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch(
                    "scitex.container._build.subprocess.run", return_value=mock_result
                ):
                    with pytest.raises(
                        RuntimeError, match="Build failed with exit code 1"
                    ):
                        build(def_name="test-image")

    def test_build_custom_output_dir(self, tmp_path):
        """Test build places sif in custom output directory."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch(
                    "scitex.container._build.subprocess.run", return_value=mock_result
                ):
                    result = build(def_name="test-image", output_dir=output_dir)

        assert result == output_dir / "test-image.sif"

    def test_build_uses_sudo(self, tmp_path):
        """Test build command includes sudo prefix."""
        from scitex.container._build import build

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        def_file = containers_dir / "test-image.def"
        def_file.write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "scitex.container._build.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._build.find_containers_dir",
                return_value=containers_dir,
            ):
                with patch(
                    "scitex.container._build.subprocess.run", return_value=mock_result
                ) as mock_run:
                    build(def_name="test-image")

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "sudo"
        assert call_args[1] == "apptainer"
        assert call_args[2] == "build"
        assert call_args[3] == "--force"


class TestHashFile:
    """Tests for _hash_file helper."""

    def test_hash_file_returns_sha256(self, tmp_path):
        """Test _hash_file computes correct SHA256 digest."""
        from scitex.container._build import _hash_file

        test_file = tmp_path / "test.txt"
        content = b"hello world"
        test_file.write_bytes(content)

        result = _hash_file(test_file)
        expected = hashlib.sha256(content).hexdigest()
        assert result == expected

    def test_hash_file_different_content_different_hash(self, tmp_path):
        """Test different file contents produce different hashes."""
        from scitex.container._build import _hash_file

        file_a = tmp_path / "a.txt"
        file_a.write_bytes(b"content A")

        file_b = tmp_path / "b.txt"
        file_b.write_bytes(b"content B")

        assert _hash_file(file_a) != _hash_file(file_b)

    def test_hash_file_same_content_same_hash(self, tmp_path):
        """Test identical content produces identical hash."""
        from scitex.container._build import _hash_file

        file_a = tmp_path / "a.txt"
        file_a.write_bytes(b"identical content")

        file_b = tmp_path / "b.txt"
        file_b.write_bytes(b"identical content")

        assert _hash_file(file_a) == _hash_file(file_b)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
