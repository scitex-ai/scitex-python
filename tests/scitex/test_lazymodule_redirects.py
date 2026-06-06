#!/usr/bin/env python3
"""Integration tests for ``_LazyModule`` + the canonical redirect map.

Pins the actual behaviour at the attribute-access surface (not just the
helper functions):

* When the external package is **not importable** (missing extras /
  package), the ``ImportError`` raised on ``scitex.<short>.<attr>``
  access carries the canonical-redirect hint if one exists.
* When the external package IS importable but **doesn't carry the
  requested attribute** (the "phantom" case — e.g.
  ``scitex.gen.load_configs`` for ``load_configs`` that actually lives
  in ``scitex.io``), the ``AttributeError`` carries the canonical hint
  too.
* When NO redirect exists and the attribute simply isn't there, the
  original ``AttributeError`` propagates unchanged so callers still see
  the standard Python ``"module 'X' has no attribute 'Y'"`` message.

Tests use a real-but-clearly-fake package name for the missing-external
case (no monkeypatching of ``sys.modules``) so the test exercises the
production import-failure path. The phantom case is constructed against
``sys`` — a module that's always importable but where contrived
attribute names don't exist.
"""

import sys

import pytest

from scitex.re_export import _LazyModule


class TestMissingExternalPackage:
    """When the external package can't be imported, ``__getattr__``
    raises ``ImportError`` with the canonical-redirect hint when one
    exists, and the generic venv-pip hint otherwise."""

    def test_known_redirect_names_canonical_module(self):
        # Arrange — a lazy module pointing at a guaranteed-missing
        # external. The redirect map has ("gen", "load_configs") →
        # "io", so we expect that to appear in the error.
        proxy = _LazyModule(
            "gen", external="scitex_canonical_redirect_test_missing_pkg"
        )
        # Act
        with pytest.raises(ImportError) as excinfo:
            proxy.load_configs
        # Assert
        assert "scitex.io.load_configs" in str(excinfo.value)

    def test_known_redirect_message_omits_extras_install(self):
        # Arrange
        proxy = _LazyModule(
            "gen", external="scitex_canonical_redirect_test_missing_pkg"
        )
        # Act
        with pytest.raises(ImportError) as excinfo:
            proxy.load_configs
        # Assert — the redirect path must not tell the user to
        # pip-install scitex[gen] (that would defeat the whole point
        # of the redirect, which is "you don't need that extra").
        assert "pip install" not in str(excinfo.value).lower()

    def test_no_redirect_falls_back_to_venv_pip_hint(self):
        # Arrange — same lazy module, but request an attribute that is
        # NOT in the redirect map for "gen".
        proxy = _LazyModule(
            "gen", external="scitex_canonical_redirect_test_missing_pkg"
        )
        # Act
        with pytest.raises(ImportError) as excinfo:
            proxy.this_attr_is_definitely_not_in_the_redirect_map
        # Assert — generic hint must show {sys.executable} -m pip
        # install 'scitex[gen]' so venv users land in the right venv.
        assert sys.executable in str(excinfo.value)
        assert "'scitex[gen]'" in str(excinfo.value)


class TestPhantomAttribute:
    """When the external package IS importable but the requested
    attribute isn't on it, the redirect map (if it has an entry) turns
    the AttributeError into a sharp hint naming the canonical home.
    Without a redirect, the original AttributeError propagates."""

    def test_known_redirect_with_present_external_names_canonical(self):
        # Arrange — point a lazy module at ``sys`` (always importable),
        # then ask for an attribute that doesn't exist on ``sys`` but
        # has a redirect under the lazy module's own short name.
        proxy = _LazyModule("gen", external="sys")
        # Act
        with pytest.raises(AttributeError) as excinfo:
            proxy.load_configs
        # Assert
        assert "scitex.io.load_configs" in str(excinfo.value)

    def test_no_redirect_propagates_original_attribute_error(self):
        # Arrange — same setup, but request an attribute with no
        # redirect entry under "gen".
        proxy = _LazyModule("gen", external="sys")
        # Act
        with pytest.raises(AttributeError) as excinfo:
            proxy.this_attr_definitely_does_not_exist_anywhere
        # Assert — the original Python AttributeError shape should be
        # preserved (not wrapped or rewritten) when there's no
        # canonical home to point at.
        assert "this_attr_definitely_does_not_exist_anywhere" in str(
            excinfo.value
        )
