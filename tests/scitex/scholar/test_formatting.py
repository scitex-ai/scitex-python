#!/usr/bin/env python3
"""Tests for scitex.scholar.formatting module."""

import pytest

from scitex.scholar.formatting import (
    CITATION_STYLES,
    DOC_TYPE_TO_BIBTEX,
    DOC_TYPE_TO_ENDNOTE,
    DOC_TYPE_TO_RIS,
    FORMAT_EXTENSIONS,
    clean_bibtex_for_arxiv,
    clean_text,
    generate_cite_key,
    paper_normalize,
    papers_to_format,
    to_bibtex,
    to_csv_row,
    to_endnote,
    to_ris,
    to_text_citation,
)


@pytest.fixture
def sample_paper():
    return {
        "title": "Deep Learning for Brain Signals",
        "authors_str": "Watanabe, Yusuke and Smith, John",
        "journal": "Nature Neuroscience",
        "year": "2024",
        "doi": "10.1038/s41593-024-0001",
        "pmid": "12345678",
        "arxiv_id": "",
        "url": "https://example.com/paper",
        "abstract": "We propose a novel deep learning approach.",
        "document_type": "article",
        "volume": "27",
        "number": "3",
        "pages": "100-115",
    }


@pytest.fixture
def minimal_paper():
    return {"title": "Minimal Paper", "authors_str": "Doe, Jane", "year": "2023"}


# ── clean_text ──────────────────────────────────────────────────


class TestCleanText:
    def test_removes_braces(self):
        assert clean_text("{hello} [world]") == "hello world"

    def test_normalises_whitespace(self):
        assert clean_text("  too   many   spaces  ") == "too many spaces"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_none_returns_empty(self):
        assert clean_text(None) == ""


# ── generate_cite_key ───────────────────────────────────────────


class TestGenerateCiteKey:
    def test_standard(self, sample_paper):
        assert generate_cite_key(sample_paper) == "watanabe2024"

    def test_single_author(self):
        paper = {"authors_str": "Einstein, Albert", "year": "1905"}
        assert generate_cite_key(paper) == "einstein1905"

    def test_missing_year(self):
        paper = {"authors_str": "Doe, Jane"}
        assert generate_cite_key(paper) == "doeXXXX"

    def test_missing_author(self):
        paper = {"year": "2024"}
        assert generate_cite_key(paper) == "unknown2024"


# ── paper_normalize ─────────────────────────────────────────────


class TestPaperNormalize:
    def test_standard_keys(self):
        raw = {"title": "Test", "authors": "Smith, J", "year": 2024, "doi": "10.1/x"}
        result = paper_normalize(raw)
        assert result["title"] == "Test"
        assert result["authors_str"] == "Smith, J"
        assert result["year"] == "2024"
        assert result["doi"] == "10.1/x"

    def test_alternate_keys(self):
        raw = {"title": "Test", "author": "Doe, J", "DOI": "10.2/y"}
        result = paper_normalize(raw)
        assert result["authors_str"] == "Doe, J"
        assert result["doi"] == "10.2/y"

    def test_defaults(self):
        result = paper_normalize({})
        assert result["title"] == "Unknown"
        assert result["document_type"] == "article"
        assert result["is_open_access"] is False

    def test_url_priority(self):
        raw = {"externalUrl": "https://a.com", "url": "https://b.com"}
        result = paper_normalize(raw)
        assert result["url"] == "https://a.com"


# ── to_bibtex ───────────────────────────────────────────────────


class TestToBibtex:
    def test_article(self, sample_paper):
        bib = to_bibtex(sample_paper)
        assert bib.startswith("@article{watanabe2024,")
        assert "title = {Deep Learning for Brain Signals}" in bib
        assert "author = {Watanabe, Yusuke and Smith, John}" in bib
        assert "journal = {Nature Neuroscience}" in bib
        assert "year = {2024}" in bib
        assert "doi = {10.1038/s41593-024-0001}" in bib
        assert "volume = {27}" in bib
        assert "number = {3}" in bib
        assert "pages = {100-115}" in bib

    def test_preprint(self):
        paper = {
            "title": "Preprint Title",
            "authors_str": "Author, A",
            "year": "2024",
            "document_type": "preprint",
        }
        bib = to_bibtex(paper)
        assert bib.startswith("@misc{")

    def test_custom_cite_key(self):
        paper = {
            "title": "Test",
            "authors_str": "X",
            "year": "2024",
            "cite_key": "custom2024",
        }
        bib = to_bibtex(paper)
        assert "@article{custom2024," in bib

    def test_arxiv_fields(self):
        paper = {
            "title": "T",
            "authors_str": "A",
            "year": "2024",
            "arxiv_id": "2401.12345",
        }
        bib = to_bibtex(paper)
        assert "eprint = {2401.12345}" in bib
        assert "archivePrefix = {arXiv}" in bib

    def test_abstract_truncation(self):
        paper = {
            "title": "T",
            "authors_str": "A",
            "year": "2024",
            "abstract": "x" * 600,
        }
        bib = to_bibtex(paper)
        assert "..." in bib

    def test_no_trailing_comma(self, sample_paper):
        bib = to_bibtex(sample_paper)
        lines = bib.strip().split("\n")
        last_field = lines[-2]  # line before closing }
        assert not last_field.rstrip().endswith(",")


# ── to_ris ──────────────────────────────────────────────────────


class TestToRis:
    def test_article(self, sample_paper):
        ris = to_ris(sample_paper)
        assert "TY  - JOUR" in ris
        assert "TI  - Deep Learning for Brain Signals" in ris
        assert "AU  - Watanabe" in ris
        assert "JO  - Nature Neuroscience" in ris
        assert "PY  - 2024" in ris
        assert "DO  - 10.1038/s41593-024-0001" in ris
        assert "ER  - " in ris

    def test_book_type(self):
        paper = {
            "title": "Book",
            "authors_str": "Writer",
            "year": "2020",
            "document_type": "book",
        }
        ris = to_ris(paper)
        assert "TY  - BOOK" in ris

    def test_unknown_type(self):
        paper = {"title": "X", "year": "2024", "document_type": "unknown"}
        ris = to_ris(paper)
        assert "TY  - GEN" in ris


# ── to_endnote ──────────────────────────────────────────────────


class TestToEndnote:
    def test_article(self, sample_paper):
        enw = to_endnote(sample_paper)
        assert "%0 Journal Article" in enw
        assert "%T Deep Learning for Brain Signals" in enw
        assert "%A Watanabe" in enw
        assert "%J Nature Neuroscience" in enw
        assert "%D 2024" in enw
        assert "%R 10.1038/s41593-024-0001" in enw

    def test_conference(self):
        paper = {
            "title": "Conf Paper",
            "authors_str": "Author",
            "year": "2024",
            "document_type": "conference",
        }
        enw = to_endnote(paper)
        assert "%0 Conference Paper" in enw


# ── to_csv_row ──────────────────────────────────────────────────


class TestToCsvRow:
    def test_keys(self, sample_paper):
        row = to_csv_row(sample_paper)
        assert "Title" in row
        assert "Authors" in row
        assert "Journal" in row
        assert "Year" in row
        assert "DOI" in row
        assert row["Year"] == "2024"


# ── to_text_citation ───────────────────────────────────────────


class TestToTextCitation:
    def test_apa(self, sample_paper):
        cit = to_text_citation(sample_paper, style="apa")
        assert "Watanabe, Yusuke and Smith, John" in cit
        assert "(2024)" in cit
        assert "Nature Neuroscience" in cit

    def test_vancouver(self, sample_paper):
        cit = to_text_citation(sample_paper, style="vancouver")
        assert "Available from:" in cit

    def test_unknown_style_defaults_apa(self, sample_paper):
        cit = to_text_citation(sample_paper, style="nonexistent")
        assert "(2024)" in cit

    def test_missing_fields_fallback(self):
        paper = {"title": "Test", "authors_str": "A", "year": "2024"}
        cit = to_text_citation(paper, style="apa")
        assert "A (2024)" in cit


# ── clean_bibtex_for_arxiv ──────────────────────────────────────


class TestCleanBibtexForArxiv:
    def test_converts_biblatex_fields(self):
        entry = "@article{key,\n  journaltitle = {Nature},\n  location = {London}\n}"
        cleaned = clean_bibtex_for_arxiv(entry)
        assert "journal = {Nature}" in cleaned
        assert "address = {London}" in cleaned

    def test_removes_unsupported_fields(self):
        entry = (
            "@article{key,\n"
            "  title = {Test},\n"
            "  url = {https://example.com},\n"
            "  abstract = {Some abstract}\n"
            "}"
        )
        cleaned = clean_bibtex_for_arxiv(entry)
        assert "url" not in cleaned
        assert "abstract" not in cleaned
        assert "title = {Test}" in cleaned

    def test_cleans_trailing_comma(self):
        entry = "@article{key,\n  title = {Test},\n}"
        cleaned = clean_bibtex_for_arxiv(entry)
        assert ",\n}" not in cleaned


# ── papers_to_format ────────────────────────────────────────────


class TestPapersToFormat:
    def test_bibtex_batch(self, sample_paper, minimal_paper):
        result = papers_to_format([sample_paper, minimal_paper], "bibtex")
        assert "@article{watanabe2024," in result
        assert "@article{doe2023," in result
        assert "\n\n" in result

    def test_ris_batch(self, sample_paper):
        result = papers_to_format([sample_paper], "ris")
        assert "TY  - JOUR" in result

    def test_unsupported_format(self, sample_paper):
        with pytest.raises(ValueError, match="Unsupported format"):
            papers_to_format([sample_paper], "xml")


# ── Type mappings ───────────────────────────────────────────────


class TestTypeMappings:
    def test_bibtex_mappings(self):
        assert DOC_TYPE_TO_BIBTEX["article"] == "article"
        assert DOC_TYPE_TO_BIBTEX["conference"] == "inproceedings"

    def test_ris_mappings(self):
        assert DOC_TYPE_TO_RIS["article"] == "JOUR"

    def test_endnote_mappings(self):
        assert DOC_TYPE_TO_ENDNOTE["article"] == "Journal Article"

    def test_format_extensions(self):
        assert FORMAT_EXTENSIONS["bibtex"] == ".bib"
        assert FORMAT_EXTENSIONS["ris"] == ".ris"

    def test_citation_styles_keys(self):
        assert set(CITATION_STYLES.keys()) == {"apa", "mla", "chicago", "vancouver"}


# EOF
