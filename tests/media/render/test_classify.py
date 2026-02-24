#!/usr/bin/env python3
"""Tests for scitex.media.render._classify."""

import pytest

from scitex.media.render import MEDIA_EXTENSIONS, classify


class TestClassify:
    """Test file type classification."""

    @pytest.mark.parametrize(
        "path,expected_type",
        [
            ("figure.png", "image"),
            ("plot.jpg", "image"),
            ("photo.jpeg", "image"),
            ("anim.gif", "image"),
            ("icon.svg", "image"),
            ("img.webp", "image"),
            ("img.bmp", "image"),
            ("paper.pdf", "pdf"),
            ("data.csv", "csv"),
            ("results.tsv", "csv"),
            ("chart.html", "plotly"),
            ("diagram.mmd", "mermaid"),
        ],
    )
    def test_known_extensions(self, path, expected_type):
        ref = classify(path)
        assert ref is not None
        assert ref["type"] == expected_type
        assert ref["path"] == path

    def test_unknown_extension_returns_none(self):
        assert classify("readme.txt") is None
        assert classify("script.py") is None
        assert classify("noext") is None

    def test_case_insensitive(self):
        ref = classify("FIGURE.PNG")
        assert ref is not None
        assert ref["type"] == "image"

    def test_nested_path(self):
        ref = classify("figures/sub/plot.png")
        assert ref is not None
        assert ref["path"] == "figures/sub/plot.png"

    def test_media_extensions_complete(self):
        """All extension sets are non-empty."""
        for media_type, exts in MEDIA_EXTENSIONS.items():
            assert len(exts) > 0, f"{media_type} has no extensions"

    def test_media_extensions_immutable(self):
        """MEDIA_EXTENSIONS cannot be mutated."""
        with pytest.raises(TypeError):
            MEDIA_EXTENSIONS["new_type"] = frozenset({".xyz"})


# EOF
