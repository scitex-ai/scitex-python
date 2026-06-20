#!/usr/bin/env python3
"""Tests for ``scitex.helpers._optional_deps``.

The optional-deps helper backs the umbrella's "install what you need"
contract: ``has_<feature>()`` probes, ``optional_import`` with a friendly
error, the ``PACKAGE_TO_EXTRA`` map, and ``get_install_command``. These
pin the public surface so a refactor that drops a probe surfaces here, not
in a downstream project. No mocks — every probe runs against the real env.
"""

import importlib

import pytest

from scitex.helpers import _optional_deps as od


def test_has_io_returns_bool():
    # Arrange
    probe = od.has_io
    # Act
    result = probe()
    # Assert
    assert isinstance(result, bool)


def test_package_to_extra_maps_to_name_extra_tuple():
    # Arrange
    mapping = od.PACKAGE_TO_EXTRA
    # Act
    sample = mapping["openai"]
    # Assert
    assert isinstance(sample, tuple) and len(sample) == 2


def test_get_install_command_returns_pip_string():
    # Arrange
    pkg = "numpy"
    # Act
    cmd = od.get_install_command(pkg)
    # Assert
    assert cmd.startswith("pip install")


def test_list_available_extras_returns_list():
    # Arrange
    fn = od.list_available_extras
    # Act
    extras = fn()
    # Assert
    assert isinstance(extras, list)


def test_optional_import_returns_module_when_present():
    # Arrange — numpy is a hard core dep, always importable
    name = "numpy"
    # Act
    mod = od.optional_import(name)
    # Assert
    assert mod is importlib.import_module(name)


def test_optional_import_raises_for_missing_when_raise_error_true():
    # Arrange — a package that does not exist
    name = "scitex_definitely_missing_pkg_xyz"
    raises = pytest.raises(ImportError)
    # Act
    # Assert
    with raises:
        od.optional_import(name, raise_error=True)


def test_optional_import_returns_none_for_missing_when_raise_error_false():
    # Arrange
    name = "scitex_definitely_missing_pkg_xyz"
    # Act
    result = od.optional_import(name, raise_error=False)
    # Assert
    assert result is None


def test_check_optional_deps_runs_without_error():
    # Arrange
    fn = od.check_optional_deps
    # Act
    result = fn()
    # Assert
    assert result is None or isinstance(result, (dict, list, bool))


# EOF
