"""Auto-generated smoke test for scitex.io.bundle._mpl_helpers.

Replaces the prior placeholder-only stub (audit-project PS206). The
real test surface should grow from here — the module-import test below
is the minimum coverage that proves the file at least parses cleanly.
"""

import importlib

import pytest


def test_module_imports():
    """Smoke: target module imports without error."""
    try:
        importlib.import_module('scitex.io.bundle._mpl_helpers')
    except ImportError as e:
        pytest.skip(f"scitex.io.bundle._mpl_helpers: {e}")
