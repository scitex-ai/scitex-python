#!/usr/bin/env python3
# File: src/scitex/scholar/storage/_search_filename.py

"""Generate normalized filenames for saved search results.

Format: ``<YYYYMMDD-HHMMSS>-<normalized-query>.<ext>``

Example::

    from scitex.scholar.storage import normalize_search_filename

    fname = normalize_search_filename("hippocampus theta year:2020-2024")
    # -> "20260218-083000-hippocampus-theta-2020-2024.bib"
"""

import re
from datetime import datetime


def normalize_search_filename(query: str, extension: str = ".bib") -> str:
    """Generate a timestamped, normalized filename from a search query.

    Encodes positive keywords and active filters using hyphens.
    Timestamp prefix ensures files sort chronologically.

    Args:
        query: Raw search query string (colon-syntax or plain keywords).
        extension: File extension to append (default: '.bib').

    Returns
    -------
        Filename string, e.g.
        ``20260218-083000-hippocampus-theta-2020-2024.bib``

    Examples
    --------
        >>> normalize_search_filename("hippocampus sharp wave year:2020-2024")  # doctest: +ELLIPSIS
        '...-hippocampus-sharp-wave-2020-2024.bib'

        >>> normalize_search_filename("neural network if:>5")  # doctest: +ELLIPSIS
        '...-neural-network-if5.bib'
    """
    # Import here to avoid circular dependency (storage <- pipelines <- storage)
    from ..pipelines.SearchQueryParser import SearchQueryParser

    parser = SearchQueryParser(query) if query else None

    parts = []

    if parser:
        # Keywords (positive only)
        for kw in parser.positive_keywords:
            safe = re.sub(r"[^a-z0-9]+", "-", kw.lower()).strip("-")
            if safe:
                parts.append(safe)

        # Year range
        if parser.year_start and parser.year_end:
            parts.append(f"{parser.year_start}-{parser.year_end}")
        elif parser.year_start:
            parts.append(f"from{parser.year_start}")
        elif parser.year_end:
            parts.append(f"to{parser.year_end}")

        # Impact factor
        if parser.min_impact_factor is not None:
            val = (
                int(parser.min_impact_factor)
                if parser.min_impact_factor == int(parser.min_impact_factor)
                else parser.min_impact_factor
            )
            parts.append(f"if{val}")

        # Citations
        if parser.min_citations is not None:
            parts.append(f"c{parser.min_citations}")

        # Open access
        if parser.open_access:
            parts.append("oa")

        # Document type
        if parser.document_type:
            parts.append(parser.document_type)

    stem = "-".join(parts) if parts else "search"
    stem = re.sub(r"-+", "-", stem).strip("-")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ext = extension if extension.startswith(".") else f".{extension}"
    return f"{timestamp}-{stem}{ext}"
