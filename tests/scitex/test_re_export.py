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


class TestSdkOwnedCompatibilityFacades:
    """Public umbrella facades resolve to the installed SDK implementation."""

    def test_app_files_api_preserves_sdk_object_identity(self):
        # Arrange
        import scitex
        from scitex_sdk import app

        # Act
        actual = scitex.app.get_files

        # Assert
        assert actual is app.get_files

    def test_app_launcher_preserves_sdk_object_identity(self):
        # Arrange
        import scitex.app.embed as facade
        from scitex_sdk.app import embed

        # Act
        actual = facade.run_standalone

        # Assert
        assert actual is embed.run_standalone

    def test_ui_module_preserves_sdk_version_owner(self):
        # Arrange
        import scitex
        from scitex_sdk import ui

        # Act
        actual = scitex.ui.__version__

        # Assert
        assert actual == ui.__version__


def test_sdk_deep_aliases_retain_real_module_metadata_and_objects(tmp_path):
    """Deep imports reuse SDK modules and preserve canonical reload semantics."""
    # Arrange
    import json
    import os
    import subprocess
    from pathlib import Path

    import scitex

    script = r'''
import sys,json,importlib
sys.path.insert(0,sys.argv[1])
def guard(event,args):
    if event=='import' and args[0].split('.')[0] in {'scitex_app','scitex_ui'}:
        raise RuntimeError('retired module import')
    if event in {'socket.bind','socket.connect','socket.getaddrinfo'}:
        raise RuntimeError('identity controls must remain offline')
sys.addaudithook(guard)
import scitex
from scitex_sdk import app
rows=[]
for alias,target in [('scitex.app.embed','scitex_sdk.app.embed'),('scitex.app._django','scitex_sdk.app._django'),('scitex.ui.branding','scitex_sdk.ui.branding')]:
    real=importlib.import_module(target);spec=real.__spec__;name=real.__name__;package=real.__package__;loader=real.__loader__
    facade=importlib.import_module(alias)
    rows.append(facade is real and real.__spec__ is spec and real.__name__==name and real.__package__==package and real.__loader__ is loader)
from scitex.app._django import ScitexAppConfig
from scitex_sdk.app._django import ScitexAppConfig as CanonicalConfig
class_identity=ScitexAppConfig is CanonicalConfig
from scitex.app.embed import run_standalone
from scitex_sdk.app.embed import run_standalone as canonical_launcher
function_identity=run_standalone is canonical_launcher
module=importlib.import_module('scitex.app.embed')
reload_identity=importlib.reload(module) is module and module.__spec__.name=='scitex_sdk.app.embed'
print(json.dumps({'module_metadata':rows,'class_identity':class_identity,'function_identity':function_identity,'reload_identity':reload_identity}))
'''
    root = str(Path(scitex.__file__).resolve().parents[1])
    # Act
    child = subprocess.run(
        [sys.executable, "-I", "-c", script, root],
        env=dict(os.environ, SCITEX_DIR=str(tmp_path / "state")),
        capture_output=True, text=True, check=True, timeout=30,
    )
    # Assert
    assert json.loads(child.stdout) == {
        "module_metadata": [True, True, True],
        "class_identity": True,
        "function_identity": True,
        "reload_identity": True,
    }


@pytest.mark.parametrize("kind", ["module", "package"])
def test_sdk_component_finder_preserves_actual_in_tree_module(tmp_path, kind):
    """An owned real module/package keeps precedence over a migrated facade."""
    # Arrange
    from scitex.re_export import EXTERNAL_REEXPORTS, _ScitexAliasFinder

    if kind == "module":
        (tmp_path / "app.py").write_text("OWNED = True\n")
    else:
        (tmp_path / "app").mkdir()
        (tmp_path / "app" / "__init__.py").write_text("OWNED = True\n")
    finder = _ScitexAliasFinder(
        {"app": EXTERNAL_REEXPORTS["app"]}, [str(tmp_path)], preserve_metadata=True
    )
    # Act
    actual = finder.find_spec("scitex.app", None)
    # Assert
    assert actual is None


def test_umbrella_import_does_not_load_sdk_gui(tmp_path):
    """Registering owned aliases does not eagerly start the SDK GUI stack."""
    # Arrange
    import json
    import os
    import subprocess
    from pathlib import Path

    import scitex

    script = r'''
import sys,json
sys.path.insert(0,sys.argv[1])
import scitex
prefixes=('django','scitex_sdk.cli','scitex_sdk.app._django','scitex_sdk.ui._cli')
print(json.dumps([n for n in sys.modules if any(n==p or n.startswith(p+'.') for p in prefixes)]))
'''
    root = str(Path(scitex.__file__).resolve().parents[1])
    # Act
    child = subprocess.run(
        [sys.executable, "-I", "-c", script, root],
        env=dict(os.environ, SCITEX_DIR=str(tmp_path / "state")),
        capture_output=True, text=True, check=True, timeout=30,
    )
    # Assert
    assert json.loads(child.stdout) == []
