#!/usr/bin/env python3
# Timestamp: 2026-02-23
# File: tests/container/test_freeze.py

"""Tests for scitex.container._freeze module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestFreeze:
    """Tests for freeze function."""

    def test_freeze_returns_all_lock_files(self, tmp_path):
        """Test freeze returns pip, dpkg, and node lock file paths."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            if "pip" in cmd:
                result.stdout = "numpy==1.24.0\npandas==2.0.0\n"
            elif "dpkg-query" in cmd:
                result.stdout = "python3=3.10.12\nbash=5.1\n"
            elif "npm" in cmd:
                result.stdout = '{"dependencies": {}}\n'
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                result = freeze(sif_path)

        assert "pip" in result
        assert "dpkg" in result
        assert "node" in result
        assert len(result) == 3

    def test_freeze_pip_lock_content(self, tmp_path):
        """Test freeze writes correct pip freeze output."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")
        pip_content = "numpy==1.24.0\npandas==2.0.0\n"

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            if "pip" in cmd:
                result.stdout = pip_content
            else:
                result.stdout = ""
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                result = freeze(sif_path)

        assert result["pip"].read_text() == pip_content

    def test_freeze_dpkg_lock_content(self, tmp_path):
        """Test freeze writes correct dpkg lock output."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")
        dpkg_content = "python3=3.10.12\nbash=5.1\n"

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            if "dpkg-query" in cmd:
                result.stdout = dpkg_content
            else:
                result.stdout = ""
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                result = freeze(sif_path)

        assert result["dpkg"].read_text() == dpkg_content

    def test_freeze_node_lock_content(self, tmp_path):
        """Test freeze writes correct npm lock output."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")
        node_content = '{"dependencies": {"npm": "9.0.0"}}\n'

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            if "npm" in cmd:
                result.stdout = node_content
            else:
                result.stdout = ""
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                result = freeze(sif_path)

        assert result["node"].read_text() == node_content

    def test_freeze_skips_failed_commands(self, tmp_path):
        """Test freeze omits lock file keys for commands that fail."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if "pip" in cmd:
                result.returncode = 0
                result.stdout = "numpy==1.24.0\n"
            else:
                result.returncode = 1
                result.stdout = ""
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                result = freeze(sif_path)

        assert "pip" in result
        assert "dpkg" not in result
        assert "node" not in result
        assert len(result) == 1

    def test_freeze_empty_when_all_fail(self, tmp_path):
        """Test freeze returns empty dict when all commands fail."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch(
                "scitex.container._freeze.subprocess.run", return_value=mock_result
            ):
                result = freeze(sif_path)

        assert result == {}

    def test_freeze_raises_on_missing_sif(self, tmp_path):
        """Test freeze raises FileNotFoundError for missing .sif file."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "nonexistent.sif"

        with pytest.raises(FileNotFoundError, match="SIF not found"):
            freeze(sif_path)

    def test_freeze_custom_output_dir(self, tmp_path):
        """Test freeze writes lock files to custom output directory."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")
        output_dir = tmp_path / "locks"

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "output\n"
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                result = freeze(sif_path, output_dir=output_dir)

        for path in result.values():
            assert path.parent == output_dir

    def test_freeze_creates_output_dir(self, tmp_path):
        """Test freeze creates the output directory if it does not exist."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")
        output_dir = tmp_path / "nested" / "locks"

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "output\n"
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                freeze(sif_path, output_dir=output_dir)

        assert output_dir.exists()

    def test_freeze_uses_correct_exec_commands(self, tmp_path):
        """Test freeze calls container exec with correct arguments."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")

        calls = []

        def mock_run(cmd, **kwargs):
            calls.append(cmd)
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                freeze(sif_path)

        assert len(calls) == 3
        # pip freeze call
        assert calls[0] == ["apptainer", "exec", str(sif_path), "pip", "freeze"]
        # dpkg call
        assert calls[1][0:3] == ["apptainer", "exec", str(sif_path)]
        assert "dpkg-query" in calls[1]
        # npm call
        assert calls[2][0:3] == ["apptainer", "exec", str(sif_path)]
        assert "npm" in calls[2]

    def test_freeze_lock_file_names(self, tmp_path):
        """Test freeze uses expected lock file names."""
        from scitex.container._freeze import freeze

        sif_path = tmp_path / "test.sif"
        sif_path.write_text("fake sif")

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "content\n"
            return result

        with patch(
            "scitex.container._freeze.detect_container_cmd", return_value="apptainer"
        ):
            with patch("scitex.container._freeze.subprocess.run", side_effect=mock_run):
                result = freeze(sif_path)

        assert result["pip"].name == "requirements-lock.txt"
        assert result["dpkg"].name == "dpkg-lock.txt"
        assert result["node"].name == "node-lock.txt"


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
