#!/usr/bin/env python3
"""Tests for ``scitex.helpers._install_guide``.

The install-guide helper powers the umbrella's "missing extra" UX:
``MODULE_REQUIREMENTS`` (the per-module → packages map), ``require_module``
(raises a friendly hint when an extra is absent), ``show_install_guide``,
and the ``@requires`` decorator. Pins the public surface so a refactor
that drops one of these is caught here. No mocks.
"""

import pytest

from scitex.helpers import _install_guide as ig


def test_module_requirements_is_a_nonempty_dict():
    # Arrange
    reqs = ig.MODULE_REQUIREMENTS
    # Act
    is_dict = isinstance(reqs, dict)
    # Assert
    assert is_dict and len(reqs) > 0


def test_require_module_succeeds_for_present_core_dep():
    # Arrange — numpy is a hard core dep; require_module must not raise
    name = "numpy"
    # Act
    result = ig.require_module(name)
    # Assert
    assert result is None


def test_check_module_deps_reports_availability_shape():
    # Arrange — a known scitex module from the requirements map
    name = next(iter(ig.MODULE_REQUIREMENTS))
    # Act
    result = ig.check_module_deps(name)
    # Assert
    assert set(result) >= {"available", "missing", "install_cmd"}


@pytest.fixture
def module_with_missing_deps():
    """A scitex module whose declared deps are genuinely absent (no mocks).

    Skips the dependent test when every requirements module is satisfied in
    the current environment.
    """
    name = next(
        (m for m in ig.MODULE_REQUIREMENTS if not ig.check_module_deps(m)["available"]),
        None,
    )
    if name is None:
        pytest.skip("all MODULE_REQUIREMENTS modules have their deps installed")
    return name


def test_require_module_raises_when_deps_missing(module_with_missing_deps):
    # Arrange
    raises = pytest.raises(ImportError)
    # Act
    # Assert
    with raises:
        ig.require_module(module_with_missing_deps)


def test_requires_decorator_returns_callable():
    # Arrange
    decorator = ig.requires("numpy")
    # Act

    @decorator
    def _demo():
        return 42

    # Assert
    assert callable(_demo)


def test_show_install_guide_runs_without_error():
    # Arrange
    fn = ig.show_install_guide
    # Act
    result = fn()
    # Assert
    assert result is None


# EOF
