#!/usr/bin/env python3
"""Tests for scitex.media.render._targets."""

import base64
import json

import pytest

from scitex.media.render._targets import _to_chat, _to_markdown, _to_terminal


class TestToTerminal:
    """Test OSC escape generation."""

    def test_osc_format(self):
        osc = _to_terminal("/tmp/test.png")
        assert osc.startswith("\033]9998;media:")
        assert osc.endswith("\007")

    def test_osc_payload_decodable(self):
        osc = _to_terminal("/tmp/test.png")
        b64 = osc[len("\033]9998;media:") : -1]
        payload = json.loads(base64.b64decode(b64))
        assert payload["type"] == "image"
        assert "url" in payload

    def test_unknown_extension(self):
        osc = _to_terminal("/tmp/readme.txt")
        b64 = osc[len("\033]9998;media:") : -1]
        payload = json.loads(base64.b64decode(b64))
        assert payload["type"] == "file"


class TestToChat:
    """Test chat SSE event formatting."""

    def test_basic(self):
        ref = _to_chat("figures/plot.png")
        assert ref["type"] == "image"
        assert ref["path"] == "figures/plot.png"
        assert ref["ext"] == ".png"

    def test_relative_from_root(self):
        ref = _to_chat("/home/user/proj/fig.png", root_path="/home/user/proj")
        assert ref["path"] == "fig.png"

    def test_unknown_type(self):
        ref = _to_chat("readme.txt")
        assert ref["type"] == "file"


class TestToMarkdown:
    """Test markdown embed formatting."""

    def test_image(self):
        md = _to_markdown("figure.png")
        assert md == "![figure.png](figure.png)"

    def test_image_with_alt(self):
        md = _to_markdown("figure.png", alt="My plot")
        assert md == "![My plot](figure.png)"

    def test_non_image(self):
        md = _to_markdown("data.csv")
        assert md == "[data.csv](data.csv)"

    def test_pdf(self):
        md = _to_markdown("paper.pdf")
        assert md == "[paper.pdf](paper.pdf)"


# EOF
