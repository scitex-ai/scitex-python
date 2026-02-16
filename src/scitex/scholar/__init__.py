"""SciTeX Scholar - Scientific Literature Management Made Simple.

This module provides a unified interface for:
- Searching scientific literature across multiple sources
- Automatic paper enrichment with journal metrics
- PDF downloads and local library management
- Bibliography generation in multiple formats

Quick Start:
    from scitex.scholar import Scholar

    scholar = Scholar()
    papers = scholar.search("deep learning")
    papers.save("pac.bib")

Installation:
    pip install scitex[scholar]
"""

# Check for missing dependencies and warn user (internal)
from scitex._install_guide import warn_module_deps as _warn_module_deps

_missing = _warn_module_deps("scholar")

# Import configuration - wrap all in try/except for graceful degradation
try:
    from scitex.scholar.auth import ScholarAuthManager
except ImportError:
    ScholarAuthManager = None  # type: ignore[misc,assignment]

try:
    from scitex.scholar.browser import ScholarBrowserManager
except ImportError:
    ScholarBrowserManager = None  # type: ignore[misc,assignment]

try:
    from scitex.scholar.config import ScholarConfig
except ImportError:
    ScholarConfig = None  # type: ignore[misc,assignment]

try:
    from scitex.scholar.core import Paper, Papers, Scholar
except ImportError:
    Paper = None
    Papers = None
    Scholar = None

try:
    from scitex.scholar.metadata_engines import ScholarEngine
except ImportError:
    ScholarEngine = None

try:
    from scitex.scholar.pdf_download import ScholarPDFDownloader
except ImportError:
    ScholarPDFDownloader = None

try:
    from scitex.scholar.storage import ScholarLibrary
except ImportError:
    ScholarLibrary = None

try:
    from scitex.scholar.url_finder import ScholarURLFinder
except ImportError:
    ScholarURLFinder = None

try:
    from . import _utils  # Internal utilities
except ImportError:
    _utils = None

# Local database integrations (crossref-local, openalex-local)
try:
    from .local_dbs import crossref_scitex
except ImportError:
    crossref_scitex = None

try:
    from .local_dbs import openalex_scitex
except ImportError:
    openalex_scitex = None

# Citation formatting (plain-dict based, no ORM dependencies)
from .formatting import (  # noqa: E402
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

__all__ = [
    # Core classes
    "Scholar",
    "Paper",
    "Papers",
    # Configuration and managers
    "ScholarConfig",
    "ScholarEngine",
    "ScholarURLFinder",
    "ScholarAuthManager",
    "ScholarBrowserManager",
    "ScholarLibrary",
    "ScholarPDFDownloader",
    # Local database integrations
    "crossref_scitex",  # CrossRef (167M+ papers via crossref-local)
    "openalex_scitex",  # OpenAlex (284M+ works via openalex-local)
    # Citation formatting
    "clean_text",
    "generate_cite_key",
    "paper_normalize",
    "to_bibtex",
    "to_ris",
    "to_endnote",
    "to_csv_row",
    "to_text_citation",
    "clean_bibtex_for_arxiv",
    "papers_to_format",
]

# # Import core classes for advanced users
# from scitex.scholar.core import Paper
# from .core.Papers import Papers

# # DOI resolver is available via: python -m scitex.scholar.resolve_doi_asyncs
# from . import doi

# # Backward compatibility alias
# PaperCollection = Papers

# # Import utility functions
# from .utils._formatters import (
#     papers_to_bibtex,
#     papers_to_ris,
#     papers_to_json,
#     papers_to_markdown
# )

# # Import enrichment functionality
# from .metadata.enrichment._MetadataEnricher import (
#     MetadataEnricher,
#     _enrich_papers_with_all,
#     _enrich_papers_with_impact_factors,
#     _enrich_papers_with_citations,
# )

# # PDF download functionality
# from .download._ScholarPDFDownloader import (
#     ScholarPDFDownloader,
#     download_pdf_async,
#     download_pdf_asyncs_async,
# )
# from .download._SmartScholarPDFDownloader import SmartScholarPDFDownloader

# # Browser-based download functionality removed - simplified structure

# # Create module-level convenience function
# def download_pdf_asyncs(
#     dois,
#     download_dir=None,
#     force=False,
#     max_worker=4,
#     show_async_progress=True,
#     acknowledge_ethical_usage=None,
#     **kwargs
# ):
#     """
#     Download PDFs for DOIs using default Scholar instance.

#     This is a convenience function that creates a Scholar instance if needed.
#     For more control, use Scholar().download_pdf_asyncs() directly.

#     Args:
#         dois: DOI strings (list or single string) or Papers/Paper objects
#         download_dir: Directory to save PDFs
#         force: Force re-download
#         max_worker: Maximum concurrent downloads
#         show_async_progress: Show download progress
#         acknowledge_ethical_usage: Acknowledge ethical usage for Sci-Hub
#         **kwargs: Additional arguments

#     Returns:
#         Dictionary with download results

#     Examples:
#         >>> import scitex as stx
#         >>> stx.scholar.download_pdf_asyncs(["10.1234/doi1", "10.5678/doi2"])
#         >>> stx.scholar.download_pdf_asyncs("10.1234/single-doi")
#     """
#     scholar = Scholar()
#     return scholar.download_pdf_asyncs(
#         dois,
#         download_dir=download_dir,
#         force=force,
#         max_worker=max_worker,
#         show_async_progress=show_async_progress,
#         acknowledge_ethical_usage=acknowledge_ethical_usage,
#         **kwargs
#     )

# # Version
# __version__ = "0.1.0"

# # What users see with "from scitex.scholar import *"
# __all__ = [
#     # Main interface
#     'Scholar',
#     'ScholarConfig',


#     # Convenience functions
#     'search',
#     'search_quick',
#     'enrich_bibtex',
#     'download_pdf_asyncs',  # NEW: Module-level convenience function

#     "doi",
#     "resolve_doi_asyncs",

#     # Core classes
#     'Paper',
#     'Papers',
#     'PaperCollection',  # Backward compatibility alias

#     # Format converters
#     'papers_to_bibtex',
#     'papers_to_ris',
#     'papers_to_json',
#     'papers_to_markdown',

#     # Enrichment
#     'MetadataEnricher',

#     # PDF download functionality
#     'ScholarPDFDownloader',
#     'download_pdf_async',
#     'download_pdf_asyncs_async',

#     # Browser-based functionality

#     # Authentication
#     'ScholarAuthManager',
#     # 'OpenAthensAuthenticator',
#     # 'ShibbolethAuthenticator',
#     # 'EZProxyAuthenticator',

#     # Resolution
#     'SingleDOIResolver',
#     'OpenURLResolver',
#     'ResumableOpenURLResolver',
#     # 'BatchDOIResolver',

#     # Enrichment
#     'MetadataEnricher',
#     'JCR_YEAR',

#     # Validation
#     'PDFValidator',
#     'ValidationResult',

#     # # Database
#     # 'PaperDatabase',
#     # 'DatabaseEntry',
#     # 'DatabaseIndex',

#     # Semantic Search
#     # 'SemanticSearchEngine',
#     # 'VectorDatabase',
#     # 'Embedder',
# ]

# # # For backward compatibility, provide access to old functions with deprecation warnings
# # def __getattr__(name):
# #     """Provide backward compatibility with deprecation warnings."""
# #     import warnings

# #     # Handle special IPython attributes
# #     if name in ['__custom_documentations__', '__wrapped__']:
# #         raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# #     # Map old names to new functionality
# #     compatibility_map = {
# #         'search_sync': 'search',
# #         'build_index': 'Scholar()._index_local_pdfs',
# #         'get_scholar_dir': 'Scholar().get_workspace_dir()',
# #         'LocalSearchEngine': 'Scholar',
# #         'VectorSearchEngine': 'Scholar',
# #         'ScholarPDFDownloader': 'Scholar',
# #         'search_papers': 'search',
# #         'SemanticScholarPaper': 'Paper',
# #         'PaperMetadata': 'Paper',
# #         'PaperAcquisition': 'Scholar',
# #         'SemanticScholarClient': 'Scholar',
# #         'JournalMetrics': 'Scholar',
# #         'PaperEnrichmentService': 'Scholar',
# #         'generate_enriched_bibliography': 'Papers.save'
# #     }

# #     if name in compatibility_map:
# #         warnings.warn(
# #             f"{name} is deprecated. Use {compatibility_map[name]} instead.",
# #             DeprecationWarning,
# #             stacklevel=2
# #         )

# #         # Return the Scholar class for most cases
# #         if name in ['search_sync', 'search_papers']:
# #             return search
# #         elif name == 'build_index':
# #             def build_index(paths, **kwargs):
# #                 scholar = Scholar()
# #                 stats = {}
# #                 for path in paths:
# #                     stats.update(scholar._index_local_pdfs(path))
# #                 return stats
# #             return build_index
# #         else:
# #             return Scholar

# #     from scitex.logging import ScholarError
# #     raise ScholarError(
# #         f"Module attribute not found: '{name}'",
# #         context={"module": __name__, "attribute": name},
# #         suggestion=f"Available attributes: Scholar, Paper, Papers, search, enrich_bibtex"
# #     )


# # Import new modules
# from .auth import (
#     ScholarAuthManager,
#     # OpenAthensAuthenticator,
#     # ShibbolethAuthenticator,
#     # EZProxyAuthenticator,
# )
# from .metadata.doi._SingleDOIResovler import SingleDOIResolver
# from .open_url import OpenURLResolver, ResumableOpenURLResolver
# from .metadata.enrichment import (
#     MetadataEnricher,
#     JCR_YEAR,
# )
# # from .cli import resolve_doi_asyncs
# from .validation import PDFValidator, ValidationResult
# # from .database import PaperDatabase, DatabaseEntry, DatabaseIndex
# # from .search import SemanticSearchEngine, VectorDatabase, Embedder

# # Module docstring for help()
# def _module_docstring():
#     """
#     SciTeX Scholar - Scientific Literature Management

#     Main Classes:
#         Scholar: Main interface for all functionality
#         Paper: Represents a scientific paper
#         Papers: Collection of papers with analysis tools

#     Quick Start:
#         >>> from scitex.scholar import Scholar
#         >>> scholar = Scholar()
#         >>> papers = scholar.search("machine learning")
#         >>> papers.filter(year_min=2020).save("ml_pac.bib")

#     Common Workflows:
#         # Search and enrich
#         papers = scholar.search("deep learning", year_min=2022)

#         # Download PDFs
#         scholar.download_pdf_asyncs(papers)

#         # Filter results
#         high_impact = papers.filter(impact_factor_min=5.0)

#         # Save bibliography
#         papers.save("bibliography.bib", format="bibtex")

#         # Search local library
#         scholar._index_local_pdfs("./my_papers")
#         local = scholar.search_local("transformer")

#     For more information, see the documentation at:
#     https://github.com/ywatanabe1989/SciTeX-Code
#     """
#     pass

# # Set module docstring
# __doc__ = _module_docstring.__doc__

# # EOF

# EOF
