#!/usr/bin/env python3
# Timestamp: "2025-08-04 08:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/utils/__init__.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Import TextNormalizer from central location
from scitex.scholar._utils.text import TextNormalizer

from ._metadata2bibtex import metadata2bibtex
from ._PubMedConverter import PubMedConverter, pmid2doi
from ._standardize_metadata import BASE_STRUCTURE, standardize_metadata
from ._URLDOIExtractor import URLDOIExtractor

__all__ = [
    "PubMedConverter",
    "pmid2doi",
    "TextNormalizer",
    "URLDOIExtractor",
    "standardize_metadata",
    "metadata2bibtex",
    "BASE_STRUCTURE",
]


# EOF
