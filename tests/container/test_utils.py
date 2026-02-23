#!/usr/bin/env python3
# Timestamp: 2026-02-23
# File: tests/container/test_utils.py

"""Tests for scitex.container._utils module."""

from pathlib import Path
from unittest.mock import patch

import pytest


class TestDetectContainerCmd:
    """Tests for detect_container_cmd function."""

    def test_returns_apptainer_when_available(self):
        """Test returns 'apptainer' when apptainer is on PATH."""
        from scitex.container._utils import detect_container_cmd

        def mock_which(cmd):
            return "/usr/bin/apptainer" if cmd == "apptainer" else None

        with patch("scitex.container._utils.shutil.which", side_effect=mock_which):
            result = detect_container_cmd()

        assert result == "apptainer"

    def test_returns_singularity_when_apptainer_missing(self):
        """Test returns 'singularity' when apptainer is absent but singularity is on PATH."""
        from scitex.container._utils import detect_container_cmd

        def mock_which(cmd):
            return "/usr/bin/singularity" if cmd == "singularity" else None

        with patch("scitex.container._utils.shutil.which", side_effect=mock_which):
            result = detect_container_cmd()

        assert result == "singularity"

    def test_prefers_apptainer_over_singularity(self):
        """Test apptainer is preferred when both are available."""
        from scitex.container._utils import detect_container_cmd

        def mock_which(cmd):
            if cmd == "apptainer":
                return "/usr/bin/apptainer"
            if cmd == "singularity":
                return "/usr/bin/singularity"
            return None

        with patch("scitex.container._utils.shutil.which", side_effect=mock_which):
            result = detect_container_cmd()

        assert result == "apptainer"

    def test_raises_when_neither_available(self):
        """Test raises FileNotFoundError when neither command is installed."""
        from scitex.container._utils import detect_container_cmd

        with patch("scitex.container._utils.shutil.which", return_value=None):
            with pytest.raises(
                FileNotFoundError, match="Neither apptainer nor singularity"
            ):
                detect_container_cmd()


class TestFindContainersDir:
    """Tests for find_containers_dir function."""

    def test_finds_cwd_containers(self, tmp_path):
        """Test finds containers/ in current working directory."""
        from scitex.container._utils import find_containers_dir

        containers_dir = tmp_path / "containers"
        containers_dir.mkdir()
        (containers_dir / "test.def").write_text("Bootstrap: docker\n")

        with patch("scitex.container._utils.Path.cwd", return_value=tmp_path):
            result = find_containers_dir()

        assert result == containers_dir

    def test_skips_cwd_without_def_files(self, tmp_path):
        """Test skips cwd containers/ if no .def files present."""
        from scitex.container._utils import find_containers_dir

        # cwd containers dir exists but has no .def files
        cwd_containers = tmp_path / "workdir" / "containers"
        cwd_containers.mkdir(parents=True)

        # Package-relative containers dir with .def files
        pkg_containers = tmp_path / "pkg" / "containers"
        pkg_containers.mkdir(parents=True)
        (pkg_containers / "test.def").write_text("Bootstrap: docker\n")

        import scitex.container._utils as utils_mod

        with patch(
            "scitex.container._utils.Path.cwd", return_value=tmp_path / "workdir"
        ):
            original_file = utils_mod.__file__
            try:
                utils_mod.__file__ = str(
                    tmp_path / "pkg" / "src" / "scitex" / "container" / "_utils.py"
                )
                result = find_containers_dir()
                assert result == pkg_containers
            finally:
                utils_mod.__file__ = original_file

    def test_finds_user_managed_containers(self, tmp_path):
        """Test finds ~/.scitex/containers/ as fallback."""
        from scitex.container._utils import find_containers_dir

        user_containers = tmp_path / ".scitex" / "containers"
        user_containers.mkdir(parents=True)
        (user_containers / "test.def").write_text("Bootstrap: docker\n")

        import scitex.container._utils as utils_mod

        with patch("scitex.container._utils.Path.cwd", return_value=tmp_path / "nodir"):
            with patch("scitex.container._utils.Path.home", return_value=tmp_path):
                original_file = utils_mod.__file__
                try:
                    utils_mod.__file__ = str(
                        tmp_path
                        / "nonexistent"
                        / "src"
                        / "scitex"
                        / "container"
                        / "_utils.py"
                    )
                    result = find_containers_dir()
                    assert result == user_containers
                finally:
                    utils_mod.__file__ = original_file

    def test_raises_when_no_containers_dir(self, tmp_path):
        """Test raises FileNotFoundError when no containers directory exists."""
        import scitex.container._utils as utils_mod
        from scitex.container._utils import find_containers_dir

        with patch("scitex.container._utils.Path.cwd", return_value=tmp_path):
            with patch("scitex.container._utils.Path.home", return_value=tmp_path):
                original_file = utils_mod.__file__
                try:
                    utils_mod.__file__ = str(
                        tmp_path
                        / "nonexistent"
                        / "src"
                        / "scitex"
                        / "container"
                        / "_utils.py"
                    )
                    with pytest.raises(
                        FileNotFoundError, match="No containers directory found"
                    ):
                        find_containers_dir()
                finally:
                    utils_mod.__file__ = original_file

    def test_search_order_cwd_first(self, tmp_path):
        """Test cwd is checked before package-relative and user dirs."""
        from scitex.container._utils import find_containers_dir

        # All three exist
        cwd_containers = tmp_path / "cwd" / "containers"
        cwd_containers.mkdir(parents=True)
        (cwd_containers / "cwd.def").write_text("Bootstrap: docker\n")

        user_containers = tmp_path / ".scitex" / "containers"
        user_containers.mkdir(parents=True)
        (user_containers / "user.def").write_text("Bootstrap: docker\n")

        with patch("scitex.container._utils.Path.cwd", return_value=tmp_path / "cwd"):
            with patch("scitex.container._utils.Path.home", return_value=tmp_path):
                result = find_containers_dir()

        assert result == cwd_containers


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
