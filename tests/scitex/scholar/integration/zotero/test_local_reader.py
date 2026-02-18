#!/usr/bin/env python3
"""Tests for ZoteroLocalReader and export_for_zotero.

Tests use the actual ~/Zotero/zotero.sqlite when present.
All tests skip gracefully when no local Zotero database is found.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_LINUX_DB = Path("~/Zotero/zotero.sqlite").expanduser()
_WINDOWS_DB = Path("/mnt/c/Users/wyusu/Zotero/zotero.sqlite")

pytestmark = pytest.mark.skipif(
    not _LINUX_DB.exists(),
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def reader():
    from scitex.scholar.integration.zotero import ZoteroLocalReader

    return ZoteroLocalReader()


@pytest.fixture(scope="module")
def all_papers(reader):
    return reader.read_all()


# ── Path detection ────────────────────────────────────────────────────────────


def test_detect_db_path_linux():
    from scitex.scholar.integration.zotero import ZoteroLocalReader

    r = ZoteroLocalReader()
    assert r.db_path.exists()
    assert r.db_path.suffix == ".sqlite"


def test_explicit_db_path():
    from scitex.scholar.integration.zotero import ZoteroLocalReader

    r = ZoteroLocalReader(db_path=str(_LINUX_DB))
    assert r.db_path == _LINUX_DB


# ── read_all ─────────────────────────────────────────────────────────────────


def test_read_all_returns_papers(all_papers):
    from scitex.scholar.core.Papers import Papers

    assert isinstance(all_papers, Papers)


def test_read_all_count(all_papers):
    # Linux DB has 49 items — at least a few must load
    assert len(all_papers) >= 1


def test_read_all_titles_not_empty(all_papers):
    titles = [p.metadata.basic.title for p in all_papers if p.metadata.basic.title]
    assert len(titles) >= 1


def test_read_all_has_authors(all_papers):
    papers_with_authors = [p for p in all_papers if p.metadata.basic.authors]
    assert len(papers_with_authors) >= 1


def test_read_all_with_limit(reader):
    papers = reader.read_all(limit=3)
    assert len(papers) <= 3


# ── read_by_tags ──────────────────────────────────────────────────────────────


def test_read_by_tags_returns_subset(reader, all_papers):
    # "Epilepsy" tag is known to exist in the Linux DB
    epilepsy_papers = reader.read_by_tags(["Epilepsy"])
    assert len(epilepsy_papers) >= 1
    assert len(epilepsy_papers) <= len(all_papers)


def test_read_by_tags_any(reader):
    # OR logic: items with either tag
    papers = reader.read_by_tags(["Epilepsy", "EEG"], match_all=False)
    assert len(papers) >= 1


def test_read_by_tags_all(reader):
    # AND logic: items with BOTH tags (may be 0 if no overlap)
    papers = reader.read_by_tags(["Epilepsy", "EEG"], match_all=True)
    assert isinstance(papers.papers, list)  # result is valid, even if empty


def test_read_by_tags_nonexistent(reader):
    papers = reader.read_by_tags(["NonExistentTag_XYZ_999"])
    assert len(papers) == 0


# ── read_by_collection ────────────────────────────────────────────────────────


def test_read_by_collection_nonexistent(reader):
    # Linux DB has 0 collections; should return empty Papers, not raise
    papers = reader.read_by_collection("NonExistentCollection")
    assert len(papers) == 0


# ── export_for_zotero ─────────────────────────────────────────────────────────


def test_export_for_zotero_bibtex(all_papers, tmp_path):
    from scitex.scholar.integration.zotero import export_for_zotero

    out = tmp_path / "export.bib"
    result = export_for_zotero(all_papers, out, fmt="bibtex")

    assert result == out
    assert out.exists()
    content = out.read_text()
    assert "@" in content  # at least one BibTeX entry


def test_export_for_zotero_ris(all_papers, tmp_path):
    from scitex.scholar.integration.zotero import export_for_zotero

    out = tmp_path / "export.ris"
    result = export_for_zotero(all_papers, out, fmt="ris")

    assert result == out
    assert out.exists()
    content = out.read_text()
    assert "TY  -" in content  # at least one RIS entry


def test_export_roundtrip_titles(all_papers, tmp_path):
    """Titles present in Papers appear in BibTeX output."""
    from scitex.scholar.integration.zotero import export_for_zotero

    out = tmp_path / "roundtrip.bib"
    export_for_zotero(all_papers, out, fmt="bibtex")

    content = out.read_text()
    titles = [p.metadata.basic.title for p in all_papers if p.metadata.basic.title]
    # At least one title should appear (partially) in the output
    assert any(t[:20] in content for t in titles if len(t) >= 20)


# ── Windows WSL path ──────────────────────────────────────────────────────────


@pytest.mark.skipif(
    not _WINDOWS_DB.exists(),
    reason="Windows Zotero DB not accessible at /mnt/c/Users/wyusu/Zotero/",
)
def test_windows_db_read():
    from scitex.scholar.integration.zotero import ZoteroLocalReader

    r = ZoteroLocalReader(db_path=_WINDOWS_DB)
    papers = r.read_all(limit=10)
    assert len(papers) >= 1
    assert len(papers) <= 10


# EOF
