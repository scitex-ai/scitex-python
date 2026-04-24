#!/usr/bin/env python3
"""SciTeX Scholar — delegates to scitex-scholar."""

from scitex_scholar import (
    SCHOLAR_AVAILABLE,
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

try:
    from scitex_scholar import clean_abstract
except ImportError:
    # clean_abstract lands in scitex-scholar >= 1.3; fall back to no-op
    # so this umbrella shim imports cleanly against 1.2.x on PyPI.
    def clean_abstract(text):
        return text


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
    "clean_abstract",
    "SCHOLAR_AVAILABLE",
]

# EOF
