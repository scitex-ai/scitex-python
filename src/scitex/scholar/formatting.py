#!/usr/bin/env python3
"""Citation formatting for plain paper dicts.

Provides BibTeX, RIS, EndNote, CSV, and text-style (APA, MLA, Chicago,
Vancouver) formatters.  Every function accepts a standard paper dict —
no ORM or framework dependencies.

Standard paper dict keys::

    title, authors_str, journal, year, doi, pmid, arxiv_id, url,
    abstract, document_type, citation_count, impact_factor,
    is_open_access, source, volume, number, pages, cite_key
"""

from __future__ import annotations

import re
from typing import Dict, List

# ── Type mappings ───────────────────────────────────────────────

DOC_TYPE_TO_BIBTEX = {
    "article": "article",
    "preprint": "misc",
    "book": "book",
    "chapter": "inbook",
    "conference": "inproceedings",
    "thesis": "phdthesis",
    "report": "techreport",
    "dataset": "misc",
}

DOC_TYPE_TO_RIS = {
    "article": "JOUR",
    "book": "BOOK",
    "chapter": "CHAP",
    "conference": "CONF",
    "thesis": "THES",
}

DOC_TYPE_TO_ENDNOTE = {
    "article": "Journal Article",
    "book": "Book",
    "chapter": "Book Section",
    "conference": "Conference Paper",
    "thesis": "Thesis",
}

FORMAT_EXTENSIONS = {
    "bibtex": ".bib",
    "endnote": ".enw",
    "ris": ".ris",
    "csv": ".csv",
    "json": ".json",
}

# ── Text citation style templates ───────────────────────────────

CITATION_STYLES: Dict[str, Dict[str, str]] = {
    "apa": {
        "dataset": "{authors} ({year}). {title} [Data set]. {publisher}. {doi}",
        "article": (
            "{authors} ({year}). {title}. {journal}, {volume}({issue}), {pages}. {doi}"
        ),
    },
    "mla": {
        "dataset": '"{title}." {publisher}, {year}, {doi}.',
        "article": (
            '{authors}. "{title}." {journal}, vol. {volume}, '
            "no. {issue}, {year}, pp. {pages}. {doi}."
        ),
    },
    "chicago": {
        "dataset": '{authors}. "{title}." {publisher}, {year}. {doi}.',
        "article": (
            '{authors}. "{title}." {journal} {volume}, '
            "no. {issue} ({year}): {pages}. {doi}."
        ),
    },
    "vancouver": {
        "dataset": (
            "{authors}. {title} [dataset]. {publisher}; {year}. Available from: {doi}"
        ),
        "article": (
            "{authors}. {title}. "
            "{journal}. {year};{volume}({issue}):{pages}. "
            "Available from: {doi}"
        ),
    },
}

# ── Normalisation helpers ───────────────────────────────────────


def clean_text(text: str) -> str:
    """Remove characters that break citation formats and normalise whitespace."""
    if not text:
        return ""
    text = re.sub(r"[{}\[\]\\]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def generate_cite_key(paper: dict) -> str:
    """Generate a BibTeX citation key from a paper dict."""
    authors = paper.get("authors_str") or "unknown"
    first_author = authors.split(",")[0].split()[-1] if authors else "unknown"
    first_author = re.sub(r"[^a-zA-Z]", "", first_author).lower()
    year = str(paper.get("year") or "XXXX")
    return f"{first_author}{year}"


def paper_normalize(data: dict) -> dict:
    """Normalise a raw dict (e.g. API search result) to a standard paper dict."""
    return {
        "title": data.get("title") or "Unknown",
        "authors_str": data.get("authors") or data.get("author") or "",
        "journal": (data.get("journal") or "").replace(r"\s*\(IF.*\)", ""),
        "year": str(data.get("year") or ""),
        "doi": data.get("doi") or data.get("DOI") or "",
        "pmid": data.get("pmid") or "",
        "arxiv_id": data.get("arxiv_id") or "",
        "url": (
            data.get("externalUrl")
            or data.get("external_url")
            or data.get("url")
            or data.get("pdf_url")
            or ""
        ),
        "abstract": data.get("abstract") or data.get("snippet") or "",
        "document_type": data.get("document_type") or "article",
        "citation_count": data.get("citations") or data.get("citation_count") or 0,
        "impact_factor": data.get("impact_factor") or 0,
        "is_open_access": data.get("is_open_access", False),
        "source": data.get("source") or "unknown",
        "volume": data.get("volume") or "",
        "number": data.get("number") or "",
        "pages": data.get("pages") or "",
    }


# ── BibTeX ──────────────────────────────────────────────────────


def to_bibtex(paper: dict) -> str:
    """Format a standard paper dict as a BibTeX entry."""
    doc_type = paper.get("document_type", "article")
    entry_type = DOC_TYPE_TO_BIBTEX.get(doc_type, "article")
    key = paper.get("cite_key") or generate_cite_key(paper)

    lines = [f"@{entry_type}{{{key},"]

    title = clean_text(paper.get("title") or "")
    if title:
        lines.append(f"  title = {{{title}}},")

    authors = paper.get("authors_str") or ""
    lines.append(f"  author = {{{authors or 'Unknown'}}},")

    journal = clean_text(paper.get("journal") or "")
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    if paper.get("year"):
        lines.append(f"  year = {{{paper['year']}}},")
    for field in ("volume", "number", "pages"):
        if paper.get(field):
            lines.append(f"  {field} = {{{paper[field]}}},")
    if paper.get("doi"):
        lines.append(f"  doi = {{{paper['doi']}}},")
    if paper.get("pmid"):
        lines.append(f"  pmid = {{{paper['pmid']}}},")
    if paper.get("arxiv_id"):
        lines.append(f"  eprint = {{{paper['arxiv_id']}}},")
        lines.append("  archivePrefix = {arXiv},")
    if paper.get("url"):
        lines.append(f"  url = {{{paper['url']}}},")
    if paper.get("abstract"):
        abstract = clean_text(paper["abstract"])
        if len(abstract) > 500:
            abstract = abstract[:500] + "..."
        lines.append(f"  abstract = {{{abstract}}},")

    if lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]
    lines.append("}")
    return "\n".join(lines)


# ── RIS ─────────────────────────────────────────────────────────


def to_ris(paper: dict) -> str:
    """Format a standard paper dict as a RIS entry."""
    doc_type = paper.get("document_type", "article")
    ris_type = DOC_TYPE_TO_RIS.get(doc_type, "GEN")
    lines = [f"TY  - {ris_type}"]

    title = clean_text(paper.get("title") or "")
    if title:
        lines.append(f"TI  - {title}")

    authors = paper.get("authors_str") or ""
    if authors:
        for author in re.split(r"\s+and\s+|,\s*", authors):
            author = author.strip()
            if author:
                lines.append(f"AU  - {author}")

    journal = clean_text(paper.get("journal") or "")
    if journal:
        lines.append(f"JO  - {journal}")
    if paper.get("year"):
        lines.append(f"PY  - {paper['year']}")
    if paper.get("doi"):
        lines.append(f"DO  - {paper['doi']}")
    if paper.get("url"):
        lines.append(f"UR  - {paper['url']}")
    if paper.get("abstract"):
        abstract = clean_text(paper["abstract"])
        if len(abstract) > 1000:
            abstract = abstract[:1000] + "..."
        lines.append(f"AB  - {abstract}")

    lines.append("ER  - ")
    return "\n".join(lines)


# ── EndNote ─────────────────────────────────────────────────────


def to_endnote(paper: dict) -> str:
    """Format a standard paper dict as an EndNote entry."""
    doc_type = paper.get("document_type", "article")
    endnote_type = DOC_TYPE_TO_ENDNOTE.get(doc_type, "Generic")
    lines = [f"%0 {endnote_type}"]

    title = clean_text(paper.get("title") or "")
    if title:
        lines.append(f"%T {title}")

    authors = paper.get("authors_str") or ""
    if authors:
        for author in re.split(r"\s+and\s+|,\s*", authors):
            author = author.strip()
            if author:
                lines.append(f"%A {author}")

    journal = clean_text(paper.get("journal") or "")
    if journal:
        lines.append(f"%J {journal}")
    if paper.get("year"):
        lines.append(f"%D {paper['year']}")
    if paper.get("doi"):
        lines.append(f"%R {paper['doi']}")
    if paper.get("url"):
        lines.append(f"%U {paper['url']}")
    if paper.get("abstract"):
        abstract = clean_text(paper["abstract"])
        if len(abstract) > 1000:
            abstract = abstract[:1000] + "..."
        lines.append(f"%X {abstract}")

    return "\n".join(lines)


# ── CSV ─────────────────────────────────────────────────────────


def to_csv_row(paper: dict) -> dict:
    """Format a standard paper dict as a CSV row dict."""
    return {
        "Title": clean_text(paper.get("title") or ""),
        "Authors": paper.get("authors_str") or "",
        "Journal": clean_text(paper.get("journal") or ""),
        "Year": paper.get("year") or "",
        "DOI": paper.get("doi") or "",
        "PMID": paper.get("pmid") or "",
        "URL": paper.get("url") or "",
        "Abstract": clean_text(paper.get("abstract") or ""),
    }


# ── Text citation styles ───────────────────────────────────────


def to_text_citation(
    paper: dict,
    style: str = "apa",
    doc_type: str = "article",
) -> str:
    """Format a paper dict as a text citation in the given style.

    Parameters
    ----------
    paper : dict
        Standard paper dict.
    style : str
        One of ``apa``, ``mla``, ``chicago``, ``vancouver``.
    doc_type : str
        One of ``article``, ``dataset``.

    Returns
    -------
    str
        Formatted citation string.
    """
    templates = CITATION_STYLES.get(style, CITATION_STYLES["apa"])
    template = templates.get(doc_type, templates.get("article", ""))

    data = {
        "authors": paper.get("authors_str") or "Unknown",
        "year": paper.get("year") or "",
        "title": clean_text(paper.get("title") or ""),
        "journal": clean_text(paper.get("journal") or ""),
        "volume": paper.get("volume") or "",
        "issue": paper.get("number") or "",
        "pages": paper.get("pages") or "",
        "doi": paper.get("doi") or paper.get("url") or "",
        "publisher": paper.get("publisher") or "",
    }

    try:
        return template.format(**data)
    except KeyError:
        return (
            f"{data['authors']} ({data['year']}). {data['title']}. {data['journal']}."
        )


# ── arXiv BibTeX cleaning ──────────────────────────────────────

_BIBLATEX_TO_BIBTEX = {
    "journaltitle": "journal",
    "location": "address",
    "date": "year",
}

_ARXIV_UNSUPPORTED_FIELDS = ["url", "urldate", "file", "abstract"]


def clean_bibtex_for_arxiv(bibtex_entry: str) -> str:
    """Clean a BibTeX entry for arXiv compatibility.

    Converts biblatex fields to standard bibtex and removes
    unsupported fields (url, urldate, file, abstract).
    """
    for biblatex_field, bibtex_field in _BIBLATEX_TO_BIBTEX.items():
        bibtex_entry = re.sub(
            rf"\b{biblatex_field}\s*=", f"{bibtex_field} =", bibtex_entry
        )

    for field in _ARXIV_UNSUPPORTED_FIELDS:
        bibtex_entry = re.sub(
            rf"\s*{field}\s*=\s*\{{[^}}]*\}},?\s*",
            "",
            bibtex_entry,
            flags=re.IGNORECASE,
        )

    bibtex_entry = re.sub(r",\s*}", "\n}", bibtex_entry)
    return bibtex_entry


# ── Batch helpers ───────────────────────────────────────────────

_FORMAT_FUNCS = {
    "bibtex": to_bibtex,
    "ris": to_ris,
    "endnote": to_endnote,
}


def papers_to_format(papers: List[dict], fmt: str) -> str:
    """Format a list of paper dicts to the given format string."""
    func = _FORMAT_FUNCS.get(fmt)
    if not func:
        raise ValueError(f"Unsupported format: {fmt}. Use: {', '.join(_FORMAT_FUNCS)}")
    return "\n\n".join(func(p) for p in papers)


# ── Search result normalization ─────────────────────────────────


def paper_from_search_result(result: dict) -> dict:
    """Normalize a raw search-API result dict to the standard paper format.

    Handles field aliases from different search engines (externalUrl, snippet, etc.)
    and fills missing fields with safe defaults.
    """
    journal = result.get("journal") or ""
    import re as _re

    journal = _re.sub(r"\s*\(IF[^)]*\)", "", journal)
    return {
        "title": result.get("title") or "Unknown",
        "authors": result.get("authors") or "",
        "journal": journal,
        "year": str(result.get("year") or ""),
        "doi": result.get("doi") or result.get("DOI") or "",
        "pmid": result.get("pmid") or "",
        "arxiv_id": result.get("arxiv_id") or "",
        "citations": result.get("citations") or result.get("citation_count") or 0,
        "impact_factor": result.get("impact_factor") or 0,
        "is_open_access": result.get("is_open_access", False),
        "abstract": result.get("abstract") or result.get("snippet") or "",
        "url": (
            result.get("externalUrl")
            or result.get("external_url")
            or result.get("pdf_url")
            or ""
        ),
        "source": result.get("source") or "unknown",
    }


def make_citation_key(last_name: str, year=None) -> str:
    """Generate a citation key from author last name and year.

    Args:
        last_name: Author last name (special chars stripped).
        year: Publication year (optional).

    Returns
    -------
        Citation key string, e.g. ``smith2024``.
    """
    import re as _re

    name = _re.sub(r"[^a-zA-Z]", "", last_name).lower()
    return f"{name}{year}" if year else name


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """Sanitize a string for use as a download filename.

    Replaces shell-unsafe characters with underscores, collapses whitespace,
    and truncates to *max_length* characters.
    """
    import re as _re

    filename = _re.sub(r'[<>:"/\\|?*]', "_", filename)
    filename = filename[:max_length]
    return _re.sub(r"\s+", "_", filename.strip())


# ── Public API ──────────────────────────────────────────────────

__all__ = [
    "clean_text",
    "generate_cite_key",
    "paper_normalize",
    "paper_from_search_result",
    "make_citation_key",
    "sanitize_filename",
    "to_bibtex",
    "to_ris",
    "to_endnote",
    "to_csv_row",
    "to_text_citation",
    "clean_bibtex_for_arxiv",
    "papers_to_format",
    "FORMAT_EXTENSIONS",
    "DOC_TYPE_TO_BIBTEX",
    "DOC_TYPE_TO_RIS",
    "DOC_TYPE_TO_ENDNOTE",
    "CITATION_STYLES",
]

# EOF
