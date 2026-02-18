#!/usr/bin/env python3
# Timestamp: "2026-01-24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/scholar/storage/_LibraryManager.py

"""
Unified manager for Scholar library structure and paper storage.

This module provides a comprehensive library manager that:
- Manages paper storage in the master library
- Handles metadata conversion and standardization
- Creates project symlinks for organization
- Generates BibTeX entries and structures
- Resolves DOIs and updates library metadata

The main class inherits from multiple mixins for modular functionality:
- StorageHelpersMixin: Storage helper methods (has_*, load, save)
- MetadataConversionMixin: Metadata conversion utilities
- PaperSavingMixin: Paper saving methods
- ResolutionMixin: DOI resolution and library structure creation
- SymlinkHandlersMixin: Symlink generation and management
- BibtexHandlersMixin: BibTeX structure and entry generation
- LibraryOperationsMixin: Library operations (update, validate)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._DeduplicationManager import DeduplicationManager

from ._mixins import (
    BibtexHandlersMixin,
    LibraryOperationsMixin,
    MetadataConversionMixin,
    PaperSavingMixin,
    ResolutionMixin,
    StorageHelpersMixin,
    SymlinkHandlersMixin,
)

logger = logging.getLogger(__name__)


class LibraryManager(
    StorageHelpersMixin,
    MetadataConversionMixin,
    PaperSavingMixin,
    ResolutionMixin,
    SymlinkHandlersMixin,
    BibtexHandlersMixin,
    LibraryOperationsMixin,
):
    """
    Unified manager for Scholar library structure and paper storage.

    This class provides comprehensive functionality for managing the Scholar
    library, including:
    - Storage helpers (check metadata, URLs, PDFs)
    - Paper loading and incremental saving
    - Metadata conversion to standardized format
    - DOI resolution and library structure creation
    - Project symlink management
    - BibTeX entry generation
    - Library validation and updates

    Parameters
    ----------
    project : str, optional
        Project name for organizing papers
    single_doi_resolver : object, optional
        DOI resolver instance for resolving DOIs from metadata
    config : ScholarConfig, optional
        Configuration object for Scholar settings

    Attributes
    ----------
    config : ScholarConfig
        Configuration object
    project : str
        Current project name
    library_master_dir : Path
        Path to the master library directory
    single_doi_resolver : object
        DOI resolver instance
    dedup_manager : DeduplicationManager
        Deduplication manager instance

    Examples
    --------
    >>> # Basic usage
    >>> manager = LibraryManager(project="my_research")
    >>> paper_id = manager.save_resolved_paper(
    ...     title="My Paper",
    ...     doi="10.1234/example",
    ...     authors=["Author One", "Author Two"],
    ...     year=2024,
    ... )

    >>> # Check if paper exists
    >>> has_pdf = manager.has_pdf(paper_id)
    >>> has_meta = manager.has_metadata(paper_id)

    >>> # Load paper
    >>> paper = manager.load_paper_from_id(paper_id)
    """

    def __init__(
        self,
        project: str = None,
        single_doi_resolver=None,
        config: Optional[ScholarConfig] = None,
        project_dir=None,
    ):
        """Initialize library manager.

        Parameters
        ----------
        project_dir : str or Path, optional
            Root of the user's code project (e.g. ``~/my-project``).
            When provided, project-local symlinks are also created at
            ``{project_dir}/scitex/scholar/library/{project}/``.
        """
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        self.library_master_dir = self.config.path_manager.get_library_master_dir()
        self.single_doi_resolver = single_doi_resolver
        self.project_dir = Path(project_dir) if project_dir else None
        self._source_filename = "papers"
        self.dedup_manager = DeduplicationManager(config=self.config)


__all__ = ["LibraryManager"]


# EOF
