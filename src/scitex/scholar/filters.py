#!/usr/bin/env python3
# File: ./src/scitex/scholar/filters.py

"""
Pure-function paper filtering for scitex.scholar.

Works on plain dicts only — no Django ORM or model imports required.

Expected paper dict keys:
    title         : str
    authors       : list[str]
    journal       : str
    year          : int or str
    citations     : int or str
    impact_factor : float or str or None
    is_open_access: bool
    source        : str
    snippet       : str  (optional, used for doc_type detection)
"""

from typing import Any, Dict, List, Optional


def apply_filters(
    papers: List[Dict[str, Any]],
    filters: Optional[Dict[str, Any]] = None,
    parsed_operators: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Filter a list of paper dicts by various criteria.

    Args:
        papers: List of paper dicts.  Each dict should contain the keys
            described in the module docstring; missing keys are treated as
            empty / zero values.
        filters: Dict of filter criteria extracted from a search form or URL
            parameters.  Supported keys:
                year_from, year_to          – year range (int)
                min_citations, max_citations – citation range (int)
                min_impact_factor           – minimum IF (float)
                max_impact_factor           – maximum IF (float)
                authors                     – list of author name strings (legacy)
                journal                     – journal name substring (legacy, str)
                open_access                 – bool
                doc_type                    – "review" | "preprint" | other
                language                    – language string ("english" passes)
        parsed_operators: Dict produced by
            SearchQueryParser.from_shell_syntax() or the equivalent
            parse_query_operators() function from scitex-cloud.  Supported
            keys:
                title_includes, title_excludes   – list[str]
                author_includes, author_excludes – list[str]
                journal_includes, journal_excludes – list[str]
                year_min, year_max               – int
                citations_min, citations_max     – int
                impact_factor_min, impact_factor_max – float

    Returns
    -------
        Filtered list of paper dicts (same objects, not copies).
    """
    if not filters and not parsed_operators:
        return papers

    filtered: List[Dict[str, Any]] = []

    for paper in papers:
        # ------------------------------------------------------------------
        # Title includes / excludes  (from parsed_operators)
        # ------------------------------------------------------------------
        if parsed_operators:
            title = paper.get("title", "").lower()

            if parsed_operators.get("title_includes"):
                if not all(
                    term.lower() in title for term in parsed_operators["title_includes"]
                ):
                    continue

            if parsed_operators.get("title_excludes"):
                if any(
                    term.lower() in title for term in parsed_operators["title_excludes"]
                ):
                    continue

            # ------------------------------------------------------------------
            # Author includes / excludes  (from parsed_operators)
            # ------------------------------------------------------------------
            authors_text = " ".join(paper.get("authors", [])).lower()

            if parsed_operators.get("author_includes"):
                if not all(
                    term.lower() in authors_text
                    for term in parsed_operators["author_includes"]
                ):
                    continue

            if parsed_operators.get("author_excludes"):
                if any(
                    term.lower() in authors_text
                    for term in parsed_operators["author_excludes"]
                ):
                    continue

            # ------------------------------------------------------------------
            # Journal includes / excludes  (from parsed_operators)
            # ------------------------------------------------------------------
            journal_name = paper.get("journal", "").lower()

            if parsed_operators.get("journal_includes"):
                if not all(
                    term.lower() in journal_name
                    for term in parsed_operators["journal_includes"]
                ):
                    continue

            if parsed_operators.get("journal_excludes"):
                if any(
                    term.lower() in journal_name
                    for term in parsed_operators["journal_excludes"]
                ):
                    continue

        # ------------------------------------------------------------------
        # Year range  (filters take precedence, parsed_operators can override)
        # ------------------------------------------------------------------
        year_from = filters.get("year_from") if filters else None
        year_to = filters.get("year_to") if filters else None

        if parsed_operators:
            year_from = parsed_operators.get("year_min") or year_from
            year_to = parsed_operators.get("year_max") or year_to

        if year_from is not None or year_to is not None:
            try:
                year = int(paper.get("year", 0))
                if year_from is not None and year < year_from:
                    continue
                if year_to is not None and year > year_to:
                    continue
            except (ValueError, TypeError):
                continue

        # ------------------------------------------------------------------
        # Citation count
        # ------------------------------------------------------------------
        min_citations = filters.get("min_citations") if filters else None
        max_citations = filters.get("max_citations") if filters else None

        if parsed_operators:
            min_citations = parsed_operators.get("citations_min") or min_citations
            max_citations = parsed_operators.get("citations_max") or max_citations

        if min_citations is not None or max_citations is not None:
            try:
                citations = int(paper.get("citations", 0))
                if min_citations is not None and citations < min_citations:
                    continue
                if max_citations is not None and citations > max_citations:
                    continue
            except (ValueError, TypeError):
                continue

        # ------------------------------------------------------------------
        # Impact factor
        # ------------------------------------------------------------------
        min_if = filters.get("min_impact_factor") if filters else None
        max_if = filters.get("max_impact_factor") if filters else None

        if parsed_operators:
            min_if = parsed_operators.get("impact_factor_min") or min_if
            max_if = parsed_operators.get("impact_factor_max") or max_if

        if min_if is not None or max_if is not None:
            try:
                impact_factor = float(paper.get("impact_factor", 0) or 0)
                if min_if is not None and impact_factor < min_if:
                    continue
                if max_if is not None and impact_factor > max_if:
                    continue
            except (ValueError, TypeError):
                continue

        # ------------------------------------------------------------------
        # Legacy author filter  (filters["authors"] is a list of name strings)
        # ------------------------------------------------------------------
        if filters and filters.get("authors"):
            authors_text = " ".join(paper.get("authors", [])).lower()
            if not any(name.lower() in authors_text for name in filters["authors"]):
                continue

        # ------------------------------------------------------------------
        # Legacy journal filter  (filters["journal"] is a substring)
        # ------------------------------------------------------------------
        if filters and filters.get("journal"):
            journal_name = paper.get("journal", "").lower()
            if filters["journal"].lower() not in journal_name:
                continue

        # ------------------------------------------------------------------
        # Open access
        # ------------------------------------------------------------------
        if filters and filters.get("open_access") and not paper.get("is_open_access"):
            continue

        # ------------------------------------------------------------------
        # Document type  (basic heuristic)
        # ------------------------------------------------------------------
        if filters and filters.get("doc_type"):
            title_and_snippet = (
                paper.get("title", "") + " " + paper.get("snippet", "")
            ).lower()
            doc_type = filters["doc_type"].lower()

            if doc_type == "review" and "review" not in title_and_snippet:
                continue
            elif (
                doc_type == "preprint"
                and "preprint" not in paper.get("source", "").lower()
            ):
                continue

        # ------------------------------------------------------------------
        # Language  (basic: only "english" passes)
        # ------------------------------------------------------------------
        if filters and filters.get("language"):
            if filters["language"].lower() != "english":
                continue

        filtered.append(paper)

    return filtered


# EOF
