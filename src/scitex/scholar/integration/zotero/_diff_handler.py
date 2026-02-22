#!/usr/bin/env python3
"""Compare Zotero library against Scholar library."""

from __future__ import annotations

import json
import re
from typing import Optional

from scitex import logging
from scitex.scholar.storage import LibraryManager

from .local_reader import ZoteroLocalReader
from .migration_report import SyncDiff, SyncDiffItem

logger = logging.getLogger(__name__)


class ZoteroDiffHandler:
    """Compare Zotero and Scholar libraries by DOI/title matching.

    Parameters
    ----------
    reader : ZoteroLocalReader
        Configured local reader.
    library_manager : LibraryManager
        Scholar library manager.
    """

    def __init__(self, reader: ZoteroLocalReader, library_manager: LibraryManager):
        self._reader = reader
        self._library_manager = library_manager

    def diff(self, project: Optional[str] = None) -> SyncDiff:
        """Compare Zotero library against Scholar library.

        Matches by DOI (primary) then normalized title (fallback).

        Parameters
        ----------
        project : str, optional
            Scholar project to compare against.

        Returns
        -------
        SyncDiff
        """
        zotero_papers = self._reader.read_all()
        zotero_index = self._index_zotero_papers(zotero_papers)
        scholar_entries = self._load_scholar_entries()

        result = SyncDiff()
        matched_zotero_ids = set()

        for scholar_id, meta in scholar_entries.items():
            doi = (meta.get("doi") or "").lower()
            title = _normalize_title(meta.get("title") or "")

            matched = None
            if doi and doi in zotero_index["by_doi"]:
                matched = zotero_index["by_doi"][doi]
            elif title and title in zotero_index["by_title"]:
                matched = zotero_index["by_title"][title]

            if matched:
                matched_zotero_ids.add(id(matched))
                result.in_both.append(
                    SyncDiffItem(
                        title=meta.get("title", ""),
                        doi=meta.get("doi"),
                        zotero_key=getattr(matched, "_zotero_key", ""),
                        scholar_id=scholar_id,
                        has_pdf_scholar=meta.get("_has_pdf", False),
                    )
                )
            else:
                result.only_in_scholar.append(
                    SyncDiffItem(
                        title=meta.get("title", ""),
                        doi=meta.get("doi"),
                        scholar_id=scholar_id,
                        has_pdf_scholar=meta.get("_has_pdf", False),
                    )
                )

        for p in zotero_papers:
            if id(p) not in matched_zotero_ids:
                result.only_in_zotero.append(
                    SyncDiffItem(
                        title=getattr(p.metadata.basic, "title", ""),
                        doi=getattr(p.metadata.id, "doi", None),
                        zotero_key=getattr(p, "_zotero_key", ""),
                    )
                )

        logger.info(result.summary())
        return result

    @staticmethod
    def _index_zotero_papers(papers):
        """Build DOI and title indexes for Zotero papers."""
        by_doi = {}
        by_title = {}
        for p in papers:
            doi = getattr(p.metadata.id, "doi", None)
            if doi:
                by_doi[doi.lower()] = p
            title = getattr(p.metadata.basic, "title", None)
            if title:
                by_title[_normalize_title(title)] = p
        return {"by_doi": by_doi, "by_title": by_title}

    def _load_scholar_entries(self):
        """Load all Scholar MASTER entries as flat dicts."""
        master_dir = self._library_manager.config.path_manager.library_dir / "MASTER"
        entries = {}
        if not master_dir.exists():
            return entries

        for entry_dir in master_dir.iterdir():
            metadata_file = entry_dir / "metadata.json"
            if not metadata_file.exists():
                continue
            try:
                with open(metadata_file) as f:
                    raw = json.load(f)
                flat = _flatten_scholar_metadata(raw)
                flat["_scholar_id"] = entry_dir.name
                flat["_has_pdf"] = bool(list(entry_dir.glob("*.pdf")))
                entries[entry_dir.name] = flat
            except (OSError, json.JSONDecodeError):
                continue
        return entries


def _normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    return re.sub(r"\s+", " ", title.lower().strip())


def _flatten_scholar_metadata(raw: dict) -> dict:
    """Flatten nested Scholar metadata.json to a flat dict with title/doi/etc."""
    meta = raw.get("metadata", {})
    basic = meta.get("basic", {})
    id_info = meta.get("id", {})
    pub = meta.get("publication", {})
    return {
        "title": basic.get("title", ""),
        "doi": id_info.get("doi", ""),
        "authors": basic.get("authors", []),
        "year": basic.get("year"),
        "journal": pub.get("journal", ""),
    }


# EOF
