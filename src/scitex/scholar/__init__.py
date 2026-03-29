#!/usr/bin/env python3
# Timestamp: 2026-03-29
# File: src/scitex/scholar/__init__.py
"""SciTeX Scholar - Scientific Literature Management Made Simple.

Searching, enriching, downloading, and organising scientific papers.

Quick Start:
    from scitex.scholar import Scholar

    scholar = Scholar()
    papers = scholar.search("deep learning")
    papers.save("results.bib")

Installation:
    pip install scitex[scholar]

This module is a thin re-export wrapper around the standalone
``scitex-scholar`` package.  All code lives in scitex_scholar;
this file simply re-exports the public API so that
``from scitex.scholar import ...`` keeps working.
"""

# =============================================================================
# Core re-exports from scitex-scholar (single source of truth)
# =============================================================================

try:
    from scitex_scholar import __version__ as __version__
except ImportError as exc:
    raise ImportError(
        "scitex.scholar requires the standalone 'scitex-scholar' package.\n"
        "Install it with:  pip install scitex-scholar\n"
        "  or:             pip install scitex[scholar]"
    ) from exc

# ── Config ────────────────────────────────────────────────────────────────────
try:
    from scitex_scholar.config import ScholarConfig
except ImportError:
    ScholarConfig = None  # type: ignore[assignment,misc]

# ── Core classes ──────────────────────────────────────────────────────────────
try:
    from scitex_scholar.core import Paper, Papers, Scholar
except ImportError:
    Paper = None  # type: ignore[assignment,misc]
    Papers = None  # type: ignore[assignment,misc]
    Scholar = None  # type: ignore[assignment,misc]

# ── Paper filtering ──────────────────────────────────────────────────────────
from scitex_scholar.filters import apply_filters  # noqa: E402
from scitex_scholar.ensure_workspace import ensure_workspace as _ensure_workspace  # noqa: E402

# ── Citation formatting (internal, accessible via __getattr__) ───────────────
from scitex_scholar.formatting import clean_bibtex_for_arxiv as _clean_bibtex_for_arxiv  # noqa: E402
from scitex_scholar.formatting import clean_text as _clean_text  # noqa: E402

# ── Citation formatting (public) ─────────────────────────────────────────────
from scitex_scholar.formatting import (  # noqa: E402
    generate_cite_key,
    make_citation_key,
    papers_to_format,
    to_bibtex,
    to_endnote,
    to_ris,
    to_text_citation,
)
from scitex_scholar.formatting import (
    paper_from_search_result as _paper_from_search_result,  # noqa: E402
)
from scitex_scholar.formatting import paper_normalize as _paper_normalize  # noqa: E402
from scitex_scholar.formatting import sanitize_filename as _sanitize_filename  # noqa: E402
from scitex_scholar.formatting import to_csv_row as _to_csv_row  # noqa: E402
from scitex_scholar.storage import (
    normalize_search_filename as _normalize_search_filename,  # noqa: E402
)

# ── Migration (Connected Papers) ─────────────────────────────────────────────
try:
    from scitex_scholar.migration import from_connected_papers, to_connected_papers
except ImportError:
    from_connected_papers = None  # type: ignore[assignment,misc]
    to_connected_papers = None  # type: ignore[assignment,misc]

# ── Citation graph ───────────────────────────────────────────────────────────
try:
    from scitex_scholar.citation_graph import (
        CitationGraphBuilder as _CitationGraphBuilder,
    )
    from scitex_scholar.citation_graph import (
        plot_citation_graph as _plot_citation_graph,
    )

    CitationGraphBuilder = _CitationGraphBuilder
    plot_citation_graph = _plot_citation_graph
except ImportError:
    CitationGraphBuilder = None  # type: ignore[assignment,misc]
    plot_citation_graph = None  # type: ignore[assignment,misc]

# ── Advanced / power-user classes (hidden, accessible via __getattr__) ───────
try:
    from scitex_scholar.auth import ScholarAuthManager as _ScholarAuthManager
except ImportError:
    _ScholarAuthManager = None  # type: ignore[assignment]

try:
    from scitex_scholar.browser import ScholarBrowserManager as _ScholarBrowserManager
except ImportError:
    _ScholarBrowserManager = None  # type: ignore[assignment]

try:
    from scitex_scholar.metadata_engines import ScholarEngine as _ScholarEngine
except ImportError:
    _ScholarEngine = None  # type: ignore[assignment]

try:
    from scitex_scholar.pdf_download import (
        ScholarPDFDownloader as _ScholarPDFDownloader,
    )
except ImportError:
    _ScholarPDFDownloader = None  # type: ignore[assignment]

try:
    from scitex_scholar.storage import ScholarLibrary as _ScholarLibrary
except ImportError:
    _ScholarLibrary = None  # type: ignore[assignment]

try:
    from scitex_scholar.url_finder import ScholarURLFinder as _ScholarURLFinder
except ImportError:
    _ScholarURLFinder = None  # type: ignore[assignment]

# Local database integrations (available if crossref-local / openalex-local installed)
try:
    from scitex_scholar.local_dbs import crossref_scitex as _crossref_scitex
except ImportError:
    _crossref_scitex = None  # type: ignore[assignment]

try:
    from scitex_scholar.local_dbs import openalex_scitex as _openalex_scitex
except ImportError:
    _openalex_scitex = None  # type: ignore[assignment]

# ── Lazy access for hidden names (backward compat for internal imports) ──────
_LAZY_NAMES = {
    # Power-user classes
    "ScholarAuthManager": "_ScholarAuthManager",
    "ScholarBrowserManager": "_ScholarBrowserManager",
    "ScholarEngine": "_ScholarEngine",
    "ScholarPDFDownloader": "_ScholarPDFDownloader",
    "ScholarLibrary": "_ScholarLibrary",
    "ScholarURLFinder": "_ScholarURLFinder",
    # Internal helpers
    "ensure_workspace": "_ensure_workspace",
    "normalize_search_filename": "_normalize_search_filename",
    "clean_bibtex_for_arxiv": "_clean_bibtex_for_arxiv",
    "clean_text": "_clean_text",
    "paper_normalize": "_paper_normalize",
    "paper_from_search_result": "_paper_from_search_result",
    "sanitize_filename": "_sanitize_filename",
    "to_csv_row": "_to_csv_row",
}


def __getattr__(name):  # noqa: C901
    if name in _LAZY_NAMES:
        return globals()[_LAZY_NAMES[name]]
    raise AttributeError(f"module 'scitex.scholar' has no attribute {name!r}")


# ── Public API ────────────────────────────────────────────────────────────────
__all__ = [
    # Core classes
    "Scholar",
    "Paper",
    "Papers",
    "ScholarConfig",
    # Citation graph
    "CitationGraphBuilder",
    "plot_citation_graph",
    # Formatting (user-facing)
    "to_bibtex",
    "to_ris",
    "to_endnote",
    "to_text_citation",
    "papers_to_format",
    "generate_cite_key",
    "make_citation_key",
    # Migration
    "from_connected_papers",
    "to_connected_papers",
    # Filtering
    "apply_filters",
]

# EOF
