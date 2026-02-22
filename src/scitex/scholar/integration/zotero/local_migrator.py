#!/usr/bin/env python3
"""Bidirectional local migration between Zotero and Scholar library.

No API key required. Works entirely with local SQLite + file operations.

Usage:
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator

    migrator = ZoteroLocalMigrator(project="my_project")

    # Zotero -> Scholar (with PDFs)
    report = migrator.import_all(dry_run=True)   # preview
    report = migrator.import_all()                # actual

    # Scholar -> Zotero (import-ready package)
    pkg = migrator.export_for_import(output_dir="/tmp/zotero_import")

    # Compare
    diff = migrator.diff()
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from scitex.scholar.storage import LibraryManager

from ._diff_handler import ZoteroDiffHandler
from ._export_handler import ZoteroExportHandler
from ._import_handler import ZoteroImportHandler
from .attachment_resolver import ZoteroAttachmentResolver
from .local_reader import ZoteroLocalReader
from .migration_report import ExportPackage, MigrationReport, SyncDiff


class ZoteroLocalMigrator:
    """Bidirectional local migration between Zotero SQLite and Scholar library.

    Parameters
    ----------
    db_path : str or Path, optional
        Path to zotero.sqlite. Auto-detected if None.
    project : str
        Scholar project name for imported papers.
    """

    def __init__(
        self,
        db_path: Optional[str | Path] = None,
        project: str = "default",
    ):
        self.reader = ZoteroLocalReader(db_path=db_path, project=project)
        self.project = project
        self._resolver = ZoteroAttachmentResolver(self.reader.get_zotero_base_dir())
        self._library_manager = LibraryManager(project=project)

        self._importer = ZoteroImportHandler(
            reader=self.reader,
            resolver=self._resolver,
            library_manager=self._library_manager,
            project=project,
        )
        self._exporter = ZoteroExportHandler(
            library_manager=self._library_manager,
            project=project,
        )
        self._differ = ZoteroDiffHandler(
            reader=self.reader,
            library_manager=self._library_manager,
        )

    # ── Zotero -> Scholar ─────────────────────────────────────────────────────

    def import_all(
        self,
        limit: Optional[int] = None,
        include_pdfs: bool = True,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Import all items from Zotero to Scholar library.

        Parameters
        ----------
        limit : int, optional
            Max items to import.
        include_pdfs : bool
            Copy PDF files from Zotero storage (default True).
        dry_run : bool
            If True, report what would happen without changing anything.
        """
        return self._importer.import_all(
            limit=limit, include_pdfs=include_pdfs, dry_run=dry_run
        )

    def import_collection(
        self,
        collection_name: str,
        include_pdfs: bool = True,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Import items from a specific Zotero collection."""
        return self._importer.import_collection(
            collection_name=collection_name,
            include_pdfs=include_pdfs,
            dry_run=dry_run,
        )

    def import_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        include_pdfs: bool = True,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Import items matching given tags."""
        return self._importer.import_by_tags(
            tags=tags,
            match_all=match_all,
            include_pdfs=include_pdfs,
            dry_run=dry_run,
        )

    # ── Scholar -> Zotero ─────────────────────────────────────────────────────

    def export_for_import(
        self,
        project: Optional[str] = None,
        output_dir: Optional[str | Path] = None,
        include_pdfs: bool = True,
    ) -> ExportPackage:
        """Export Scholar papers as a Zotero-importable package.

        Creates papers.bib + pdfs/ directory for Zotero File > Import.
        """
        return self._exporter.export_for_import(
            project=project, output_dir=output_dir, include_pdfs=include_pdfs
        )

    # ── Diff ──────────────────────────────────────────────────────────────────

    def diff(self, project: Optional[str] = None) -> SyncDiff:
        """Compare Zotero library against Scholar library."""
        return self._differ.diff(project=project)


# EOF
