#!/usr/bin/env python3
"""
Scholar storage module - Library and paper storage management.

Public API (actively used):
- LibraryManager: Low-level library operations
- ScholarLibrary: High-level library operations
- BibTeXHandler: BibTeX import/export and bibliography management
- BibTeXValidator: BibTeX file validation for syntax and content integrity
- PaperIO: Individual paper I/O operations

Internal (not for external use):
- _LibraryCacheManager: Used by ScholarLibrary
- _DeduplicationManager: Used by LibraryManager
"""

from ._BibTeXValidator import (
    BibTeXValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    validate_bibtex_content,
    validate_bibtex_file,
)
from ._LibraryCacheManager import LibraryCacheManager
from ._LibraryManager import LibraryManager
from ._search_filename import normalize_search_filename
from .BibTeXHandler import BibTeXHandler
from .PaperIO import PaperIO
from .ScholarLibrary import ScholarLibrary

__all__ = [
    "LibraryManager",
    "ScholarLibrary",
    "BibTeXHandler",
    "BibTeXValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "validate_bibtex_file",
    "validate_bibtex_content",
    "PaperIO",
    "normalize_search_filename",
]
