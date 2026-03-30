"""SciTeX Scholar -- delegates to scitex-scholar package.

Searching, enriching, downloading, and organising scientific papers.

Quick Start:
    from scitex.scholar import Scholar

    scholar = Scholar()
    papers = scholar.search("deep learning")
    papers.save("results.bib")

Installation:
    pip install scitex[scholar]
"""

try:
    # ── Delegate to standalone scitex-scholar package ────────────────────────
    from scitex_scholar import (
        CitationGraphBuilder,
        Paper,
        Papers,
        Scholar,
        ScholarConfig,
        apply_filters,
        from_connected_papers,
        generate_cite_key,
        make_citation_key,
        papers_to_format,
        plot_citation_graph,
        to_bibtex,
        to_connected_papers,
        to_endnote,
        to_ris,
        to_text_citation,
    )

    # Internal helpers accessible via __getattr__
    from scitex_scholar import (
        __version__ as _scholar_version,
    )

    _BACKEND = "scitex-scholar"
    SCHOLAR_AVAILABLE = True

    # Power-user classes (lazy access)
    try:
        from scitex_scholar.auth import ScholarAuthManager as _ScholarAuthManager
    except ImportError:
        _ScholarAuthManager = None

    try:
        from scitex_scholar.browser import (
            ScholarBrowserManager as _ScholarBrowserManager,
        )
    except ImportError:
        _ScholarBrowserManager = None

    try:
        from scitex_scholar.metadata_engines import ScholarEngine as _ScholarEngine
    except ImportError:
        _ScholarEngine = None

    try:
        from scitex_scholar.pdf_download import (
            ScholarPDFDownloader as _ScholarPDFDownloader,
        )
    except ImportError:
        _ScholarPDFDownloader = None

    try:
        from scitex_scholar.storage import ScholarLibrary as _ScholarLibrary
    except ImportError:
        _ScholarLibrary = None

    try:
        from scitex_scholar.url_finder import ScholarURLFinder as _ScholarURLFinder
    except ImportError:
        _ScholarURLFinder = None

    try:
        from scitex_scholar.ensure_workspace import (
            ensure_workspace as _ensure_workspace,
        )
    except ImportError:
        _ensure_workspace = None

    try:
        from scitex_scholar.formatting import (
            clean_bibtex_for_arxiv as _clean_bibtex_for_arxiv,
        )
        from scitex_scholar.formatting import clean_text as _clean_text
        from scitex_scholar.formatting import (
            paper_from_search_result as _paper_from_search_result,
        )
        from scitex_scholar.formatting import paper_normalize as _paper_normalize
        from scitex_scholar.formatting import sanitize_filename as _sanitize_filename
        from scitex_scholar.formatting import to_csv_row as _to_csv_row
    except ImportError:
        _clean_bibtex_for_arxiv = None
        _clean_text = None
        _paper_from_search_result = None
        _paper_normalize = None
        _sanitize_filename = None
        _to_csv_row = None

    try:
        from scitex_scholar.storage import (
            normalize_search_filename as _normalize_search_filename,
        )
    except ImportError:
        _normalize_search_filename = None

    # Local database integrations
    try:
        from scitex_scholar.local_dbs import crossref_scitex as _crossref_scitex
    except ImportError:
        _crossref_scitex = None

    try:
        from scitex_scholar.local_dbs import openalex_scitex as _openalex_scitex
    except ImportError:
        _openalex_scitex = None

except ImportError:
    # ── Fallback to local implementation ─────────────────────────────────────
    _BACKEND = "local"
    SCHOLAR_AVAILABLE = False
    _scholar_version = None

    from scitex._install_guide import warn_module_deps as _warn_module_deps

    _warn_module_deps("scholar")

    try:
        from scitex.scholar.config import ScholarConfig
    except ImportError:
        ScholarConfig = None

    try:
        from scitex.scholar.core import Paper, Papers, Scholar
    except ImportError:
        Paper = None
        Papers = None
        Scholar = None

    from .ensure_workspace import ensure_workspace as _ensure_workspace
    from .filters import apply_filters
    from .formatting import clean_bibtex_for_arxiv as _clean_bibtex_for_arxiv
    from .formatting import clean_text as _clean_text
    from .formatting import (
        generate_cite_key,
        make_citation_key,
        papers_to_format,
        to_bibtex,
        to_endnote,
        to_ris,
        to_text_citation,
    )
    from .formatting import (
        paper_from_search_result as _paper_from_search_result,
    )
    from .formatting import paper_normalize as _paper_normalize
    from .formatting import sanitize_filename as _sanitize_filename
    from .formatting import to_csv_row as _to_csv_row
    from .storage import (
        normalize_search_filename as _normalize_search_filename,
    )

    try:
        from scitex.scholar.migration import (
            from_connected_papers,
            to_connected_papers,
        )
    except ImportError:
        from_connected_papers = None
        to_connected_papers = None

    try:
        from scitex.scholar.citation_graph import (
            CitationGraphBuilder,
            plot_citation_graph,
        )
    except ImportError:
        CitationGraphBuilder = None
        plot_citation_graph = None

    _ScholarAuthManager = None
    _ScholarBrowserManager = None
    _ScholarEngine = None
    _ScholarPDFDownloader = None
    _ScholarLibrary = None
    _ScholarURLFinder = None
    _crossref_scitex = None
    _openalex_scitex = None


# ── Lazy access for hidden names (backward compat) ──────────────────────────
_LAZY_NAMES = {
    "ScholarAuthManager": "_ScholarAuthManager",
    "ScholarBrowserManager": "_ScholarBrowserManager",
    "ScholarEngine": "_ScholarEngine",
    "ScholarPDFDownloader": "_ScholarPDFDownloader",
    "ScholarLibrary": "_ScholarLibrary",
    "ScholarURLFinder": "_ScholarURLFinder",
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
    "Scholar",
    "Paper",
    "Papers",
    "ScholarConfig",
    "CitationGraphBuilder",
    "plot_citation_graph",
    "to_bibtex",
    "to_ris",
    "to_endnote",
    "to_text_citation",
    "papers_to_format",
    "generate_cite_key",
    "make_citation_key",
    "from_connected_papers",
    "to_connected_papers",
    "apply_filters",
    "SCHOLAR_AVAILABLE",
]

# EOF
