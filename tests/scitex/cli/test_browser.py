#!/usr/bin/env python3
# File: tests/scitex/cli/test_browser.py
"""Tests for ``scitex browser`` CLI commands."""

from __future__ import annotations

import subprocess
import sys

import pytest

# Runs the real CLI in a fresh interpreter in which playwright cannot be
# imported -- a ``None`` entry in sys.modules makes ``import`` raise
# ImportError, exactly as on an install without the [browser] extra.
_OPEN_WITHOUT_PLAYWRIGHT = """
import sys
sys.modules["playwright"] = None
sys.modules["playwright.async_api"] = None
from scitex.cli.browser import browser
browser(["open", "example.com"], prog_name="scitex browser")
"""


@pytest.fixture(scope="module")
def open_without_playwright():
    return subprocess.run(
        [sys.executable, "-c", _OPEN_WITHOUT_PLAYWRIGHT],
        capture_output=True,
        text=True,
        timeout=300,
    )


def test_open_without_playwright_exits_with_click_error_code(
    open_without_playwright,
):
    # Arrange
    result = open_without_playwright
    # Act
    code = result.returncode
    # Assert
    assert code == 1


def test_open_without_playwright_names_the_browser_extra(open_without_playwright):
    # Arrange
    result = open_without_playwright
    # Act
    stderr = result.stderr
    # Assert
    assert "pip install 'scitex[browser]'" in stderr


def test_open_without_playwright_does_not_leak_a_traceback(open_without_playwright):
    # Arrange
    result = open_without_playwright
    # Act
    stderr = result.stderr
    # Assert
    assert "Traceback" not in stderr


# EOF
