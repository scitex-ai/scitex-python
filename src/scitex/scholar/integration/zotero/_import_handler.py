#!/usr/bin/env python3
"""Zotero -> Scholar import handler with PDF migration."""

from __future__ import annotations

import shutil
from typing import Dict, List, Optional

from scitex import logging
from scitex.scholar.storage import LibraryManager

from .attachment_resolver import ResolvedAttachment, ZoteroAttachmentResolver
from .local_reader import ZoteroLocalReader
from .migration_report import MigratedItem, MigrationError, MigrationReport

logger = logging.getLogger(__name__)


class ZoteroImportHandler:
    """Handle Zotero -> Scholar import with PDF file migration.

    Parameters
    ----------
    reader : ZoteroLocalReader
        Configured local reader.
    resolver : ZoteroAttachmentResolver
        Configured attachment resolver.
    library_manager : LibraryManager
        Scholar library manager.
    project : str
        Scholar project name.
    """

    def __init__(
        self,
        reader: ZoteroLocalReader,
        resolver: ZoteroAttachmentResolver,
        library_manager: LibraryManager,
        project: str,
    ):
        self._reader = reader
        self._resolver = resolver
        self._library_manager = library_manager
        self._project = project

    def import_all(
        self,
        limit: Optional[int] = None,
        include_pdfs: bool = True,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Import all items from Zotero."""
        item_ids = self._reader._fetch_item_ids(limit=limit)
        return self._import_items(item_ids, include_pdfs=include_pdfs, dry_run=dry_run)

    def import_collection(
        self,
        collection_name: str,
        include_pdfs: bool = True,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Import items from a specific Zotero collection."""
        with self._reader._connect() as conn:
            rows = conn.execute(
                """
                SELECT ci.itemID
                FROM collectionItems ci
                JOIN collections col ON ci.collectionID = col.collectionID
                WHERE col.collectionName = ?
                """,
                (collection_name,),
            ).fetchall()
        return self._import_items(
            [r[0] for r in rows], include_pdfs=include_pdfs, dry_run=dry_run
        )

    def import_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        include_pdfs: bool = True,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Import items matching given tags."""
        placeholders = ",".join("?" * len(tags))
        with self._reader._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT it.itemID, COUNT(DISTINCT t.name) as tag_count
                FROM itemTags it
                JOIN tags t ON it.tagID = t.tagID
                WHERE t.name IN ({placeholders})
                GROUP BY it.itemID
                """,
                tags,
            ).fetchall()

        required = len(tags) if match_all else 1
        item_ids = [r[0] for r in rows if r[1] >= required]
        return self._import_items(item_ids, include_pdfs=include_pdfs, dry_run=dry_run)

    def _import_items(  # noqa: C901
        self,
        item_ids: List[int],
        include_pdfs: bool = True,
        dry_run: bool = False,
    ) -> MigrationReport:
        """Core import logic."""
        report = MigrationReport(
            direction="zotero_to_scholar", total_items=len(item_ids)
        )
        if not item_ids:
            return report

        papers = self._reader._build_papers(item_ids)

        # Fetch attachment info
        attachments: Dict[int, List[ResolvedAttachment]] = {}
        if include_pdfs:
            with self._reader._connect() as conn:
                attachments = self._resolver.list_attachments_for_items(
                    item_ids, conn, pdf_only=True
                )

        # Build zotero_key -> paper mapping for safe pairing
        ids_str = ",".join(str(i) for i in item_ids)
        with self._reader._connect() as conn:
            type_rows = conn.execute(
                f"""
                SELECT i.itemID, i.key
                FROM items i
                JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
                WHERE i.itemID IN ({ids_str})
                AND it.typeName NOT IN ('attachment', 'note', 'annotation')
                ORDER BY i.itemID
                """
            ).fetchall()

        # Index papers by _zotero_key for safe matching (avoids positional drift)
        paper_by_key = {}
        for p in papers:
            key = getattr(p, "_zotero_key", None)
            if key:
                paper_by_key[key] = p

        for row in type_rows:
            item_id, zotero_key = row[0], row[1]
            paper = paper_by_key.get(zotero_key)
            if paper is None:
                continue

            title = getattr(paper.metadata.basic, "title", "") or ""
            doi = getattr(paper.metadata.id, "doi", None)
            item_pdfs = attachments.get(item_id, [])

            if dry_run:
                self._record_dry_run(report, zotero_key, title, doi, item_pdfs)
                continue

            self._do_import(
                report, paper, zotero_key, title, doi, item_pdfs, include_pdfs
            )

        logger.info(report.summary())
        return report

    def _record_dry_run(self, report, zotero_key, title, doi, item_pdfs):
        """Record a dry-run item in the report."""
        report.items.append(
            MigratedItem(
                zotero_key=zotero_key,
                scholar_id=None,
                title=title,
                doi=doi,
                pdf_migrated=bool(item_pdfs),
                status="would_import",
            )
        )
        if item_pdfs:
            report.pdfs_copied += 1
        else:
            report.pdfs_missing += 1
        report.imported += 1

    def _do_import(
        self, report, paper, zotero_key, title, doi, item_pdfs, include_pdfs
    ):
        """Perform actual import of a single item."""
        try:
            scholar_id = self._library_manager.save_resolved_paper(
                paper_data=paper, project=self._project, source="zotero"
            )
            pdf_migrated = False
            if include_pdfs and item_pdfs:
                pdf_migrated = self._copy_pdfs(item_pdfs, scholar_id)
            if include_pdfs and not item_pdfs:
                report.pdfs_missing += 1
            if pdf_migrated:
                report.pdfs_copied += 1

            report.items.append(
                MigratedItem(
                    zotero_key=zotero_key,
                    scholar_id=scholar_id,
                    title=title,
                    doi=doi,
                    pdf_migrated=pdf_migrated,
                    status="imported",
                )
            )
            report.imported += 1
            logger.info(f"Imported: {title[:60]} -> {scholar_id}")

        except Exception as e:
            report.failed += 1
            report.errors.append(
                MigrationError(zotero_key=zotero_key, title=title, error=str(e))
            )
            report.items.append(
                MigratedItem(
                    zotero_key=zotero_key,
                    scholar_id=None,
                    title=title,
                    doi=doi,
                    pdf_migrated=False,
                    status="failed",
                    error=str(e),
                )
            )
            logger.error(f"Failed to import {title[:60]}: {e}")

    def _copy_pdfs(self, pdfs: List[ResolvedAttachment], scholar_id: str) -> bool:
        """Copy PDFs from Zotero storage to Scholar MASTER."""
        master_dir = (
            self._library_manager.config.path_manager.library_dir
            / "MASTER"
            / scholar_id
        )
        master_dir.mkdir(parents=True, exist_ok=True)

        copied = False
        for pdf in pdfs:
            if not pdf.path.exists():
                continue
            dest = master_dir / pdf.filename
            if dest.exists() and dest.stat().st_size == pdf.size_bytes:
                copied = True
                continue
            try:
                shutil.copy2(pdf.path, dest)
                copied = True
                logger.debug(f"Copied PDF: {pdf.filename} -> {dest}")
            except OSError as e:
                logger.warning(f"Failed to copy PDF {pdf.filename}: {e}")
        return copied


# EOF
