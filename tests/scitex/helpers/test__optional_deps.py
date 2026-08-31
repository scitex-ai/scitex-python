#!/usr/bin/env python3
"""Tests for ``scitex.helpers._optional_deps``.

The optional-deps helper backs the umbrella's "install what you need"
contract: ``has_<feature>()`` probes, ``optional_import`` with a friendly
error, the ``PACKAGE_TO_EXTRA`` map, and ``get_install_command``. These
pin the public surface so a refactor that drops a probe surfaces here, not
in a downstream project. No mocks — every probe runs against the real env.
"""

import importlib
import sys

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


def test_check_optional_deps_maps_names_to_installed_state():
    # Arrange — one name that is always installed, one that never is
    names = ("numpy", "scitex_definitely_missing_pkg_xyz")
    # Act
    result = od.check_optional_deps(*names)
    # Assert
    assert result == {"numpy": True, "scitex_definitely_missing_pkg_xyz": False}


def test_check_optional_deps_values_are_plain_bools():
    # Arrange — `has_stats` compares the returned dict to a {name: True}
    # literal, so values must be bools, not truthy ModuleSpec objects.
    names = ("numpy", "scitex_definitely_missing_pkg_xyz")
    # Act
    result = od.check_optional_deps(*names)
    # Assert
    assert all(type(value) is bool for value in result.values())


def _install_real_package(root, name, body):
    """Write a real importable package under ``root`` and put it on sys.path."""
    pkg = root / name
    pkg.mkdir()
    (pkg / "__init__.py").write_text(body)
    sys.path.insert(0, str(root))
    return pkg


@pytest.fixture
def side_effect_package(tmp_path):
    """A REAL importable package that records having had its body executed."""
    sentinel = tmp_path / "executed.marker"
    name = "scitex_probe_side_effect_pkg"
    _install_real_package(
        tmp_path,
        name,
        "from pathlib import Path\nPath(%r).write_text('executed')\n" % str(sentinel),
    )
    yield name, sentinel
    sys.path.remove(str(tmp_path))
    sys.modules.pop(name, None)


def test_check_optional_deps_does_not_execute_the_module(side_effect_package):
    # Arrange — probing availability must never run third-party top-level
    # code: in CI that walk imported the whole optional stack (233 C
    # extensions) into the pytest process just to answer "is it installed".
    name, sentinel = side_effect_package
    # Act
    od.check_optional_deps(name)
    # Assert
    assert not sentinel.exists(), "availability probe executed the module body"


def test_check_optional_deps_finds_package_without_executing_it(side_effect_package):
    # Arrange
    name, _sentinel = side_effect_package
    # Act
    result = od.check_optional_deps(name)
    # Assert
    assert result == {name: True}


def test_check_optional_deps_reports_installed_package_that_raises_on_import(tmp_path):
    # Arrange — a REAL installed package whose import raises a non-ImportError,
    # exactly like `sounddevice` raising OSError('PortAudio library not found')
    # on a host without PortAudio. The probe must answer, not propagate.
    name = "scitex_probe_raises_pkg"
    _install_real_package(
        tmp_path, name, "raise OSError('PortAudio library not found')\n"
    )
    try:
        # Act
        result = od.check_optional_deps(name)
        # Assert — installed is the honest answer; it is on disk and locatable
        assert result == {name: True}
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop(name, None)


def test_check_optional_deps_reports_false_for_dotted_name_with_missing_parent():
    # Arrange — find_spec RAISES ModuleNotFoundError for an absent parent
    # package rather than returning None; that must read as "not installed".
    name = "scitex_definitely_missing_pkg_xyz.submodule"
    # Act
    result = od.check_optional_deps(name)
    # Assert
    assert result == {name: False}


# EOF
