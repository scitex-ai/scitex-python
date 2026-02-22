"""SciTeX Scholar - Scientific Literature Management Made Simple.

Searching, enriching, downloading, and organising scientific papers.

Quick Start:
    from scitex.scholar import Scholar

    scholar = Scholar()
    papers = scholar.search("deep learning")
    papers.save("results.bib")

Installation:
    pip install scitex[scholar]
"""

# ── Internal bootstrap ───────────────────────────────────────────────────────
from scitex._install_guide import warn_module_deps as _warn_module_deps

_warn_module_deps("scholar")

# ── Config first (required by Scholar via circular dep) ──────────────────────
try:
    from scitex.scholar.config import ScholarConfig
except ImportError:
    ScholarConfig = None  # type: ignore[assignment,misc]

# ── Core classes ─────────────────────────────────────────────────────────────
try:
    from scitex.scholar.core import Paper, Papers, Scholar
except ImportError:
    Paper = None  # type: ignore[assignment,misc]
    Papers = None  # type: ignore[assignment,misc]
    Scholar = None  # type: ignore[assignment,misc]

# ── Paper filtering ──────────────────────────────────────────────────────────
# ── Internal helpers (accessible via __getattr__) ────────────────────────────
from .ensure_workspace import ensure_workspace as _ensure_workspace  # noqa: E402
from .filters import apply_filters  # noqa: E402

# ── Citation formatting (internal, accessible via __getattr__) ───────────────
from .formatting import clean_bibtex_for_arxiv as _clean_bibtex_for_arxiv  # noqa: E402
from .formatting import clean_text as _clean_text  # noqa: E402

# ── Citation formatting (public) ─────────────────────────────────────────────
from .formatting import (  # noqa: E402
    generate_cite_key,
    make_citation_key,
    papers_to_format,
    to_bibtex,
    to_endnote,
    to_ris,
    to_text_citation,
)
from .formatting import (
    paper_from_search_result as _paper_from_search_result,  # noqa: E402
)
from .formatting import paper_normalize as _paper_normalize  # noqa: E402
from .formatting import sanitize_filename as _sanitize_filename  # noqa: E402
from .formatting import to_csv_row as _to_csv_row  # noqa: E402
from .storage import (
    normalize_search_filename as _normalize_search_filename,  # noqa: E402
)

# ── Migration (Connected Papers) ─────────────────────────────────────────────
try:
    from scitex.scholar.migration import from_connected_papers, to_connected_papers
except ImportError:
    from_connected_papers = None  # type: ignore[assignment,misc]
    to_connected_papers = None  # type: ignore[assignment,misc]

# ── Citation graph ───────────────────────────────────────────────────────────
try:
    from scitex.scholar.citation_graph import (
        CitationGraphBuilder as _CitationGraphBuilder,
    )
    from scitex.scholar.citation_graph import (
        plot_citation_graph as _plot_citation_graph,
    )

    CitationGraphBuilder = _CitationGraphBuilder
    plot_citation_graph = _plot_citation_graph
except ImportError:
    CitationGraphBuilder = None  # type: ignore[assignment,misc]
    plot_citation_graph = None  # type: ignore[assignment,misc]

# ── Advanced / power-user classes (hidden, accessible via __getattr__) ───────
try:
    from scitex.scholar.auth import ScholarAuthManager as _ScholarAuthManager
except ImportError:
    _ScholarAuthManager = None  # type: ignore[assignment]

try:
    from scitex.scholar.browser import ScholarBrowserManager as _ScholarBrowserManager
except ImportError:
    _ScholarBrowserManager = None  # type: ignore[assignment]

try:
    from scitex.scholar.metadata_engines import ScholarEngine as _ScholarEngine
except ImportError:
    _ScholarEngine = None  # type: ignore[assignment]

try:
    from scitex.scholar.pdf_download import (
        ScholarPDFDownloader as _ScholarPDFDownloader,
    )
except ImportError:
    _ScholarPDFDownloader = None  # type: ignore[assignment]

try:
    from scitex.scholar.storage import ScholarLibrary as _ScholarLibrary
except ImportError:
    _ScholarLibrary = None  # type: ignore[assignment]

try:
    from scitex.scholar.url_finder import ScholarURLFinder as _ScholarURLFinder
except ImportError:
    _ScholarURLFinder = None  # type: ignore[assignment]

# Local database integrations (available if crossref-local / openalex-local installed)
try:
    from .local_dbs import crossref_scitex as _crossref_scitex
except ImportError:
    _crossref_scitex = None  # type: ignore[assignment]

try:
    from .local_dbs import openalex_scitex as _openalex_scitex
except ImportError:
    _openalex_scitex = None  # type: ignore[assignment]

# ── Hide leaked submodule attributes ─────────────────────────────────────────
import sys as _sys

_this_module = _sys.modules[__name__]
for _submod in [
    "auth",
    "browser",
    "config",
    "core",
    "ensure_workspace",
    "filters",
    "formatting",
    "impact_factor",
    "local_dbs",
    "metadata_engines",
    "pdf_download",
    "storage",
    "url_finder",
    "citation_graph",
    "migration",
    "_utils",
]:
    try:
        delattr(_this_module, _submod)
    except AttributeError:
        pass
del _this_module, _submod, _sys

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
