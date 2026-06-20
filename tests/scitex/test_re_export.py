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


def _capture_access_error(proxy, attr: str) -> str:
    """Trigger ``proxy.<attr>`` and return the raised error's message.

    Fails the test if the access unexpectedly succeeds. Keeps each test to a
    single assertion (the message check) by moving the raise into a helper.
    """
    try:
        getattr(proxy, attr)
    except (ImportError, AttributeError) as exc:
        return str(exc)
    raise AssertionError(f"accessing {attr!r} did not raise")


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
        message = _capture_access_error(proxy, "load_configs")
        # Assert
        assert "scitex.io.load_configs" in message

    def test_known_redirect_message_omits_extras_install(self):
        # Arrange
        proxy = _LazyModule(
            "gen", external="scitex_canonical_redirect_test_missing_pkg"
        )
        # Act
        message = _capture_access_error(proxy, "load_configs")
        # Assert — the redirect path must not tell the user to pip-install
        # scitex[gen] (that defeats the redirect: "you don't need that extra").
        assert "pip install" not in message.lower()

    def test_no_redirect_hint_names_the_venv_executable(self):
        # Arrange — request an attribute that is NOT in the redirect map.
        proxy = _LazyModule(
            "gen", external="scitex_canonical_redirect_test_missing_pkg"
        )
        # Act
        message = _capture_access_error(
            proxy, "this_attr_is_definitely_not_in_the_redirect_map"
        )
        # Assert — generic hint shows {sys.executable} so venv users land right.
        assert sys.executable in message

    def test_no_redirect_hint_names_the_extra_spec(self):
        # Arrange
        proxy = _LazyModule(
            "gen", external="scitex_canonical_redirect_test_missing_pkg"
        )
        # Act
        message = _capture_access_error(
            proxy, "this_attr_is_definitely_not_in_the_redirect_map"
        )
        # Assert
        assert "'scitex[gen]'" in message


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
        message = _capture_access_error(proxy, "load_configs")
        # Assert
        assert "scitex.io.load_configs" in message

    def test_no_redirect_propagates_original_attribute_error(self):
        # Arrange — same setup, but request an attribute with no
        # redirect entry under "gen".
        proxy = _LazyModule("gen", external="sys")
        # Act
        message = _capture_access_error(
            proxy, "this_attr_definitely_does_not_exist_anywhere"
        )
        # Assert — the original Python AttributeError shape is preserved
        # (not wrapped or rewritten) when there's no canonical home.
        assert "this_attr_definitely_does_not_exist_anywhere" in message


class TestExternalFallback:
    """When the primary ``external`` is unimportable but a ``fallback``
    external IS importable, ``_LazyModule`` resolves to the fallback.

    This is the scitex.security case: ADR-0001 routed it to
    ``scitex_audit.github`` while ADR-0002 made ``scitex_security`` the
    unified home — the fallback keeps it reachable whichever is installed.
    """

    def test_fallback_used_when_primary_external_missing(self):
        # Arrange — primary is guaranteed-missing; fallback is the always
        # importable stdlib ``json`` module.
        proxy = _LazyModule(
            "demo",
            external="scitex_fallback_test_missing_pkg",
            fallback="json",
        )
        # Act
        loaded = proxy._load_module()
        # Assert
        import json as _json

        assert loaded is _json

    def test_fallback_attribute_access_resolves(self):
        # Arrange — attribute access must transparently reach the fallback.
        proxy = _LazyModule(
            "demo",
            external="scitex_fallback_test_missing_pkg",
            fallback="json",
        )
        # Act
        dumps = proxy.dumps
        # Assert
        import json as _json

        assert dumps is _json.dumps

    def test_primary_wins_when_importable(self):
        # Arrange — primary (``sys``) IS importable; fallback must be ignored.
        proxy = _LazyModule("demo", external="sys", fallback="json")
        # Act
        loaded = proxy._load_module()
        # Assert
        assert loaded is sys

    def test_security_module_is_reachable_via_umbrella(self):
        # Arrange — the real umbrella facade for the security ADR conflict.
        import importlib

        # Act
        module = importlib.import_module("scitex.security")
        # Assert
        assert hasattr(module, "check_github_alerts")
