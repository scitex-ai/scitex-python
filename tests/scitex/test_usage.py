#!/usr/bin/env python3
# File: tests/scitex/test_usage.py
"""Output-stream contract of ``scitex.usage`` (PS-220).

``show()`` writes the usage text to stdout verbatim and returns it.
``_render()`` returns the same text and writes nothing. The MCP tool calls
``_render()`` because stdout is the protocol channel under stdio.
"""

from __future__ import annotations

import pytest

pytest.importorskip("scitex_template")

from scitex import usage  # noqa: E402


def test_show_writes_returned_overview_verbatim_to_stdout(capsys):
    # Arrange
    topic = None
    # Act
    text = usage.show(topic)
    captured = capsys.readouterr()
    # Assert
    assert captured.out == text + "\n"


def test_show_writes_returned_unknown_topic_message_verbatim_to_stdout(capsys):
    # Arrange
    topic = "definitely-not-a-topic"
    # Act
    text = usage.show(topic)
    captured = capsys.readouterr()
    # Assert
    assert captured.out == text + "\n"


def test_show_writes_nothing_to_stderr(capsys):
    # Arrange
    topic = None
    # Act
    usage.show(topic)
    captured = capsys.readouterr()
    # Assert
    assert captured.err == ""


def test_render_returns_the_same_text_as_show(capsys):
    # Arrange
    shown = usage.show(None)
    capsys.readouterr()
    # Act
    rendered = usage._render(None)
    # Assert
    assert rendered == shown


def test_render_writes_nothing_to_stdout(capsys):
    # Arrange
    topic = None
    # Act
    usage._render(topic)
    captured = capsys.readouterr()
    # Assert
    assert captured.out == ""


# EOF
