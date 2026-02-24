#!/usr/bin/env python3
"""Tests for scitex.media.render._show."""

import json

import pytest

from scitex.media.render import show


class TestShow:
    """Test show() dispatching to targets."""

    def test_markdown_target(self):
        result = show("figure.png", target="markdown")
        assert "![" in result
        assert "figure.png" in result

    def test_chat_target(self):
        result = show("data.csv", target="chat")
        parsed = json.loads(result)
        assert parsed["type"] == "csv"

    def test_terminal_target(self, capsys):
        result = show("/tmp/test.png", target="terminal")
        assert result.startswith("\033]9998;media:")
        captured = capsys.readouterr()
        assert "\033]9998;media:" in captured.out

    def test_invalid_target(self):
        with pytest.raises(ValueError, match="Unknown target"):
            show("fig.png", target="invalid")


# EOF
