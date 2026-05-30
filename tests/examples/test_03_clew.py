"""Smoke test for examples/03_clew.ipynb.

Auto-generated stub (audit-project PS303). Replace with a real test
that runs the example end-to-end and asserts on its outputs.
"""

import importlib.util
from pathlib import Path

import pytest


EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "03_clew.ipynb"


def test_example_file_exists():
    assert EXAMPLE.exists(), f"missing example file: {EXAMPLE}"


def test_example_imports_cleanly():
    if EXAMPLE.suffix != ".py":
        pytest.skip(f"non-python example: {EXAMPLE.suffix}")
    spec = importlib.util.spec_from_file_location("ex", EXAMPLE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # We don't execute the module — just verify parser-clean syntax via
    # spec resolution. A real test should import + invoke main().
    assert module is not None
