#!/usr/bin/env python3
# File: ./tests/scitex/test___version__.py
"""Tests for the thin scitex.__version__ module.

The version module is a *thin* shim: the single source of truth is
pyproject.toml, surfaced at runtime via importlib.metadata.version("scitex").
The module therefore only exposes ``__version__`` (a str) — it deliberately
does NOT carry ``__FILE__`` / ``__DIR__`` or a hard-coded literal. These
tests assert that thin contract (dynamic, metadata-sourced, PEP 440-shaped)
rather than an obsolete pinned-string contract.
"""

import importlib.metadata
import os
import re
import time

import pytest

# Pre-compiled release-core matcher (PEP 440 leading major.minor.patch).
_SEMVER_CORE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def _installed_scitex_version_or_skip() -> str:
    """Installed metadata version for ``scitex``, or skip if absent.

    Kept out of the test body so each test keeps a single assertion
    (the skip-guard is setup, not an assertion).
    """
    try:
        return importlib.metadata.version("scitex")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("scitex package metadata not available")


class TestVersionBasics:
    """Basic tests for the version module."""

    def test_version_attr_is_not_none(self):
        # Arrange / import the thin module attribute
        from scitex.__version__ import __version__

        # Act
        value = __version__
        # Assert
        assert value is not None

    def test_version_attr_is_a_string(self):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        is_string = isinstance(__version__, str)
        # Assert
        assert is_string

    def test_version_string_is_not_empty(self):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        stripped = __version__.strip()
        # Assert
        assert stripped != ""


class TestVersionFormat:
    """Tests for version format validation."""

    def test_version_starts_with_semver_core(self):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        match = _SEMVER_CORE.match(__version__)
        # Assert
        assert match is not None

    def test_version_core_components_are_digit_strings(self):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        match = _SEMVER_CORE.match(__version__)
        # Assert
        assert all(component.isdigit() for component in match.groups())


class TestVersionModuleImport:
    """Tests for version module import behavior."""

    def test_main_package_exposes_version_attr(self):
        # Arrange
        import scitex

        # Act
        has_version = hasattr(scitex, "__version__")
        # Assert
        assert has_version

    def test_main_package_version_is_a_string(self):
        # Arrange
        import scitex

        # Act
        is_string = isinstance(scitex.__version__, str)
        # Assert
        assert is_string

    def test_package_version_matches_submodule_version(self):
        # Arrange
        import scitex
        from scitex.__version__ import __version__

        # Act
        package_version = scitex.__version__
        # Assert
        assert package_version == __version__

    def test_package_version_attr_is_a_string_not_a_module(self):
        # The ``scitex.__version__`` *attribute* is the version string itself
        # (set in scitex/__init__.py); it shadows the same-named submodule on
        # the package object. This is the public, thin contract.
        # Arrange
        import scitex

        # Act
        attr = scitex.__version__
        # Assert
        assert isinstance(attr, str)


class TestVersionModuleFile:
    """Tests for version module file handling."""

    def _version_file_path(self):
        import scitex

        package_dir = os.path.dirname(scitex.__file__)
        return os.path.join(package_dir, "__version__.py")

    def test_version_file_exists_on_disk(self):
        # Arrange
        version_file = self._version_file_path()
        # Act
        exists = os.path.isfile(version_file)
        # Assert
        assert exists

    def test_version_file_sources_from_importlib_metadata(self):
        # Arrange
        version_file = self._version_file_path()
        # Act
        with open(version_file) as f:
            content = f.read()
        # Assert
        assert "importlib" in content and "metadata" in content


class TestVersionEdgeCases:
    """Edge case tests for the version module."""

    def test_version_reference_is_stable(self):
        # Arrange
        from scitex.__version__ import __version__

        original = __version__
        # Act
        again = __version__
        # Assert
        assert again is original

    def test_version_is_consistent_across_imports(self):
        # Arrange
        from scitex.__version__ import __version__ as v1
        from scitex.__version__ import __version__ as v2

        # Act
        equal = v1 == v2
        # Assert
        assert equal

    def test_version_string_is_ascii_only(self):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        is_ascii = __version__.isascii()
        # Assert
        assert is_ascii

    def test_version_string_has_no_surrounding_whitespace(self):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        stripped = __version__.strip()
        # Assert
        assert __version__ == stripped


class TestVersionIntegration:
    """Integration tests for the version module."""

    def test_version_matches_installed_package_metadata(self):
        # Arrange
        from scitex.__version__ import __version__

        package_version = _installed_scitex_version_or_skip()
        # Act
        equal = __version__ == package_version
        # Assert
        assert equal


class TestVersionPerformance:
    """Performance tests for the version module."""

    def test_repeated_version_access_is_fast(self):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        start = time.time()
        for _ in range(10_000):
            _ = __version__
        elapsed = time.time() - start
        # Assert
        assert elapsed < 0.1


class TestVersionDocumentation:
    """Tests for version module documentation."""

    def test_module_docstring_is_a_string_when_present(self):
        # Arrange
        import scitex.__version__ as version_module

        doc = version_module.__doc__
        # Act
        ok = doc is None or isinstance(doc, str)
        # Assert
        assert ok


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__)])
