#!/usr/bin/env python3
"""Tests for scitex.media.render._detect."""

import pytest

from scitex.media.render import detect


class TestDetect:
    """Test media detection from text."""

    def test_basic_detection(self):
        text = "Saved to /home/user/proj/figures/plot.png"
        refs = detect(text, root_path="/home/user/proj")
        assert len(refs) == 1
        assert refs[0]["type"] == "image"
        assert refs[0]["path"] == "figures/plot.png"
        assert refs[0]["ext"] == ".png"

    def test_multiple_refs(self):
        text = "Created /home/user/proj/fig.png and /home/user/proj/data.csv"
        refs = detect(text, root_path="/home/user/proj")
        assert len(refs) == 2
        types = {r["type"] for r in refs}
        assert types == {"image", "csv"}

    def test_dedup(self):
        text = "/home/user/proj/fig.png and again /home/user/proj/fig.png"
        refs = detect(text, root_path="/home/user/proj")
        assert len(refs) == 1

    def test_no_root_returns_empty(self):
        assert detect("some text", root_path=None) == []

    def test_empty_text_returns_empty(self):
        assert detect("", root_path="/root") == []

    def test_no_match(self):
        text = "No file paths here"
        assert detect(text, root_path="/home/user/proj") == []

    def test_ignores_non_media_extensions(self):
        text = "Wrote /home/user/proj/script.py"
        assert detect(text, root_path="/home/user/proj") == []

    def test_trailing_slash_on_root(self):
        text = "File at /home/user/proj/fig.png"
        refs = detect(text, root_path="/home/user/proj/")
        assert len(refs) == 1
        assert refs[0]["path"] == "fig.png"

    def test_filename_with_parens(self):
        text = "Saved /home/user/proj/Figure(v2).png done"
        refs = detect(text, root_path="/home/user/proj")
        assert len(refs) == 1
        assert refs[0]["path"] == "Figure(v2).png"

    def test_filename_with_brackets(self):
        text = "Saved /home/user/proj/data[final].csv done"
        refs = detect(text, root_path="/home/user/proj")
        assert len(refs) == 1
        assert refs[0]["path"] == "data[final].csv"

    def test_trailing_period_stripped(self):
        text = "Saved to /home/user/proj/fig.png."
        refs = detect(text, root_path="/home/user/proj")
        assert len(refs) == 1
        assert refs[0]["path"] == "fig.png"

    def test_trailing_comma_stripped(self):
        text = "Created /home/user/proj/a.png, /home/user/proj/b.csv"
        refs = detect(text, root_path="/home/user/proj")
        assert len(refs) == 2


# EOF
