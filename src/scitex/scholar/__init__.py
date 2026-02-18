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

# ── Workspace ────────────────────────────────────────────────────────────────
from .ensure_workspace import ensure_workspace  # noqa: E402

# ── Paper filtering ──────────────────────────────────────────────────────────
from .filters import apply_filters  # noqa: E402

# ── Citation formatting ──────────────────────────────────────────────────────
from .formatting import (  # noqa: E402
    clean_bibtex_for_arxiv,
    clean_text,
    generate_cite_key,
    make_citation_key,
    paper_from_search_result,
    paper_normalize,
    papers_to_format,
    sanitize_filename,
    to_bibtex,
    to_csv_row,
    to_endnote,
    to_ris,
    to_text_citation,
)

# ── Storage filename helper ──────────────────────────────────────────────────
from .storage import normalize_search_filename  # noqa: E402

# ── Advanced / power-user classes (not in __all__ but importable) ────────────
# These are kept accessible for advanced users but intentionally
# excluded from the default public API to keep the surface minimal.
try:
    from scitex.scholar.auth import ScholarAuthManager as _ScholarAuthManager

    ScholarAuthManager = _ScholarAuthManager
except ImportError:
    ScholarAuthManager = None  # type: ignore[assignment,misc]

try:
    from scitex.scholar.browser import ScholarBrowserManager as _ScholarBrowserManager

    ScholarBrowserManager = _ScholarBrowserManager
except ImportError:
    ScholarBrowserManager = None  # type: ignore[assignment,misc]

try:
    from scitex.scholar.metadata_engines import ScholarEngine as _ScholarEngine

    ScholarEngine = _ScholarEngine
except ImportError:
    ScholarEngine = None  # type: ignore[assignment,misc]

try:
    from scitex.scholar.pdf_download import (
        ScholarPDFDownloader as _ScholarPDFDownloader,
    )

    ScholarPDFDownloader = _ScholarPDFDownloader
except ImportError:
    ScholarPDFDownloader = None  # type: ignore[assignment,misc]

try:
    from scitex.scholar.storage import ScholarLibrary as _ScholarLibrary

    ScholarLibrary = _ScholarLibrary
except ImportError:
    ScholarLibrary = None  # type: ignore[assignment,misc]

try:
    from scitex.scholar.url_finder import ScholarURLFinder as _ScholarURLFinder

    ScholarURLFinder = _ScholarURLFinder
except ImportError:
    ScholarURLFinder = None  # type: ignore[assignment,misc]

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
# When Python loads a subpackage (e.g. scitex.scholar.auth) it automatically
# sets it as an attribute on the parent package.  We delete these references
# so that dir(scitex.scholar) only shows the intended public surface.
import sys as _sys

_this_module = _sys.modules[__name__]
for _submod in [
    "auth",
    "browser",
    "config",
    "core",
    "filters",
    "formatting",
    "impact_factor",
    "local_dbs",
    "metadata_engines",
    "pdf_download",
    "storage",
    "url_finder",
    "_utils",
]:
    try:
        delattr(_this_module, _submod)
    except AttributeError:
        pass
del _this_module, _submod, _sys

# ── Public API ────────────────────────────────────────────────────────────────
__all__ = [
    # Core classes
    "Scholar",
    "Paper",
    "Papers",
    "ScholarConfig",
    # Workspace
    "ensure_workspace",
    # Filtering
    "apply_filters",
    # Filename for saved search results
    "normalize_search_filename",
    # Citation formatting
    "generate_cite_key",
    "make_citation_key",
    "paper_normalize",
    "paper_from_search_result",
    "sanitize_filename",
    "to_bibtex",
    "to_ris",
    "to_endnote",
    "to_csv_row",
    "to_text_citation",
    "clean_bibtex_for_arxiv",
    "clean_text",
    "papers_to_format",
]

# EOF
