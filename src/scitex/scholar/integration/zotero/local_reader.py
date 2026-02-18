#!/usr/bin/env python3
"""
Zotero local SQLite reader — no API key required.

Reads directly from Zotero's local database file (zotero.sqlite).
Auto-detects Linux and Windows (WSL) Zotero installations.

Usage:
    from scitex.scholar.integration.zotero import ZoteroLocalReader, export_for_zotero

    reader = ZoteroLocalReader()             # auto-detect
    papers = reader.read_all()               # all items
    papers = reader.read_by_tags(["EEG"])    # filter by tag
    export_for_zotero(papers, "out.bib")     # export for Zotero > File > Import
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from scitex.scholar.core.Papers import Papers

from .mapper import ZoteroMapper

# ── Known Zotero DB paths ─────────────────────────────────────────────────────

_LINUX_PATH = Path("~/Zotero/zotero.sqlite").expanduser()
_WSL_BASE = Path("/mnt/c/Users")

_SKIP_TYPES = {"attachment", "note", "annotation"}


# ── Reader ────────────────────────────────────────────────────────────────────


class ZoteroLocalReader:
    """Read papers from a local Zotero SQLite database.

    Parameters
    ----------
    db_path : str or Path, optional
        Path to zotero.sqlite. If None, auto-detects Linux then WSL paths.
    project : str
        Scholar project name for the returned Papers collection.
    """

    def __init__(
        self,
        db_path: Optional[str | Path] = None,
        project: str = "default",
    ):
        self.db_path = Path(db_path) if db_path else self._detect_db_path()
        self.project = project
        self._mapper = ZoteroMapper()

    # ── Public methods ────────────────────────────────────────────────────────

    def read_all(self, limit: Optional[int] = None) -> Papers:
        """Read all non-attachment items from the Zotero library.

        Parameters
        ----------
        limit : int, optional
            Maximum number of items to return.

        Returns
        -------
        Papers
        """
        item_ids = self._fetch_item_ids(limit=limit)
        return self._build_papers(item_ids)

    def read_by_collection(self, name: str) -> Papers:
        """Read items belonging to a Zotero collection.

        Parameters
        ----------
        name : str
            Collection name (case-sensitive).

        Returns
        -------
        Papers
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT ci.itemID
                FROM collectionItems ci
                JOIN collections col ON ci.collectionID = col.collectionID
                WHERE col.collectionName = ?
                """,
                (name,),
            ).fetchall()
        item_ids = [r[0] for r in rows]
        return self._build_papers(item_ids)

    def read_by_tags(self, tags: List[str], match_all: bool = False) -> Papers:
        """Read items matching given tags.

        Parameters
        ----------
        tags : list of str
            Tag names to filter by.
        match_all : bool
            If True, items must have ALL listed tags.
            If False (default), items with ANY listed tag are returned.

        Returns
        -------
        Papers
        """
        placeholders = ",".join("?" * len(tags))
        with self._connect() as conn:
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
        return self._build_papers(item_ids)

    def list_collections(self) -> List[str]:
        """Return all collection names in the Zotero library, sorted alphabetically.

        Returns
        -------
        list of str
            Collection names sorted alphabetically.
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT collectionName FROM collections ORDER BY collectionName"
            ).fetchall()
        return [r[0] for r in rows]

    def list_tags(self) -> List[Dict]:
        """Return all tag names with occurrence counts, sorted by count descending.

        Returns
        -------
        list of dict
            Tags with structure: [{"name": str, "count": int}, ...] sorted by count (descending).
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT name, COUNT(*) as cnt FROM tags GROUP BY name ORDER BY cnt DESC"
            ).fetchall()
        return [{"name": r[0], "count": r[1]} for r in rows]

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _detect_db_path(self) -> Path:
        """Auto-detect Zotero SQLite: Linux first, then WSL Windows mount."""
        if _LINUX_PATH.exists():
            return _LINUX_PATH
        if _WSL_BASE.exists():
            for candidate in _WSL_BASE.glob("*/Zotero/zotero.sqlite"):
                if candidate.exists():
                    return candidate
        raise FileNotFoundError(
            "No Zotero database found. Checked:\n"
            f"  {_LINUX_PATH}\n"
            f"  {_WSL_BASE}/*/Zotero/zotero.sqlite\n"
            "Pass db_path explicitly: ZoteroLocalReader(db_path='/path/to/zotero.sqlite')"
        )

    def _connect(self) -> sqlite3.Connection:
        """Open a read-only SQLite connection."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def _fetch_item_ids(self, limit: Optional[int] = None) -> List[int]:
        """Fetch IDs of all non-attachment, non-note items."""
        skip = ",".join(f"'{t}'" for t in _SKIP_TYPES)
        limit_clause = f"LIMIT {limit}" if limit else ""
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT i.itemID
                FROM items i
                JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
                WHERE it.typeName NOT IN ({skip})
                ORDER BY i.itemID
                {limit_clause}
                """
            ).fetchall()
        return [r[0] for r in rows]

    def _build_papers(self, item_ids: List[int]) -> Papers:
        """Batch-load all data for the given item IDs and convert to Papers."""
        if not item_ids:
            return Papers([], project=self.project)

        ids_str = ",".join(str(i) for i in item_ids)

        with self._connect() as conn:
            # Item base info
            type_rows = conn.execute(
                f"""
                SELECT i.itemID, i.key, it.typeName
                FROM items i
                JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
                WHERE i.itemID IN ({ids_str})
                """
            ).fetchall()

            # All field values (batch)
            field_rows = conn.execute(
                f"""
                SELECT id.itemID, f.fieldName, idv.value
                FROM itemData id
                JOIN fields f ON id.fieldID = f.fieldID
                JOIN itemDataValues idv ON id.valueID = idv.valueID
                WHERE id.itemID IN ({ids_str})
                """
            ).fetchall()

            # Creators (ordered)
            creator_rows = conn.execute(
                f"""
                SELECT ic.itemID, c.firstName, c.lastName, ct.creatorType
                FROM itemCreators ic
                JOIN creators c ON ic.creatorID = c.creatorID
                JOIN creatorTypes ct ON ic.creatorTypeID = ct.creatorTypeID
                WHERE ic.itemID IN ({ids_str})
                ORDER BY ic.itemID, ic.orderIndex
                """
            ).fetchall()

            # Tags
            tag_rows = conn.execute(
                f"""
                SELECT it.itemID, t.name
                FROM itemTags it
                JOIN tags t ON it.tagID = t.tagID
                WHERE it.itemID IN ({ids_str})
                """
            ).fetchall()

        # Group by itemID
        fields: Dict[int, Dict[str, str]] = {i: {} for i in item_ids}
        for row in field_rows:
            fields[row[0]][row[1]] = row[2]

        creators: Dict[int, List[dict]] = {i: [] for i in item_ids}
        for row in creator_rows:
            creators[row[0]].append(
                {
                    "firstName": row[1] or "",
                    "lastName": row[2] or "",
                    "creatorType": row[3],
                }
            )

        tags: Dict[int, List[str]] = {i: [] for i in item_ids}
        for row in tag_rows:
            tags[row[0]].append(row[1])

        # Convert to Papers via ZoteroMapper
        paper_list = []
        for row in type_rows:
            item_id, key, type_name = row[0], row[1], row[2]
            api_dict = self._to_api_format(
                key,
                type_name,
                fields.get(item_id, {}),
                creators.get(item_id, []),
                tags.get(item_id, []),
            )
            try:
                paper = self._mapper.zotero_to_paper(api_dict)
                paper_list.append(paper)
            except Exception:
                pass  # Skip malformed items silently

        return Papers(paper_list, project=self.project)

    def _to_api_format(
        self,
        key: str,
        type_name: str,
        fields: Dict[str, str],
        creators: List[dict],
        tags: List[str],
    ) -> dict:
        """Convert raw SQLite rows to the Zotero API dict format ZoteroMapper expects."""
        return {
            "key": key,
            "version": 0,
            "data": {
                "itemType": type_name,
                "title": fields.get("title", ""),
                "abstractNote": fields.get("abstractNote", ""),
                "creators": creators,
                "date": fields.get("date", ""),
                "DOI": fields.get("DOI", ""),
                "url": fields.get("url", ""),
                "publicationTitle": fields.get("publicationTitle", ""),
                "journalAbbreviation": fields.get("journalAbbreviation", ""),
                "volume": fields.get("volume", ""),
                "issue": fields.get("issue", ""),
                "pages": fields.get("pages", ""),
                "publisher": fields.get("publisher", ""),
                "ISSN": fields.get("ISSN", ""),
                "ISBN": fields.get("ISBN", ""),
                "extra": fields.get("extra", ""),
                "language": fields.get("language", ""),
                "tags": [{"tag": t} for t in tags],
                "collections": [],
            },
        }


# ── Convenience export ────────────────────────────────────────────────────────


def export_for_zotero(papers: Papers, path: str | Path, fmt: str = "bibtex") -> Path:
    """Export papers to a file that Zotero can import via File > Import.

    Parameters
    ----------
    papers : Papers
        Papers collection to export.
    path : str or Path
        Output file path (e.g. 'output.bib', 'output.ris').
    fmt : str
        Format: 'bibtex' (default) or 'ris'.

    Returns
    -------
    Path
        The written file path.

    Example
    -------
    >>> reader = ZoteroLocalReader()
    >>> papers = reader.read_all()
    >>> export_for_zotero(papers, "enriched.bib")
    >>> # Then: Zotero > File > Import > enriched.bib
    """
    from scitex.scholar.formatting import papers_to_format

    path = Path(path)

    # Convert Papers (which may hold Paper objects) to plain dicts for formatting
    paper_dicts = []
    for p in papers:
        if hasattr(p, "metadata"):
            # Paper object — convert to formatting dict
            paper_dicts.append(_paper_obj_to_dict(p))
        elif isinstance(p, dict):
            paper_dicts.append(p)

    content = papers_to_format(paper_dicts, fmt)
    path.write_text(content, encoding="utf-8")
    return path


def _paper_obj_to_dict(paper) -> dict:
    """Convert Paper object to the plain dict format used by formatting.py."""
    m = paper.metadata
    authors_list = getattr(m.basic, "authors", []) or []
    return {
        "title": getattr(m.basic, "title", "") or "",
        "authors_str": " and ".join(authors_list),
        "year": str(getattr(m.basic, "year", "") or ""),
        "abstract": getattr(m.basic, "abstract", "") or "",
        "journal": getattr(m.publication, "journal", "") or "",
        "volume": getattr(m.publication, "volume", "") or "",
        "number": getattr(m.publication, "issue", "") or "",
        "pages": getattr(m.publication, "pages", "") or "",
        "doi": getattr(m.id, "doi", "") or "",
        "pmid": getattr(m.id, "pmid", "") or "",
        "arxiv_id": getattr(m.id, "arxiv_id", "") or "",
        "url": (getattr(m.url, "publisher", "") or getattr(m.url, "doi", "") or ""),
        "document_type": getattr(m.basic, "type", "article") or "article",
        "is_open_access": False,
        "source": "zotero",
    }


# ── Public API ────────────────────────────────────────────────────────────────

__all__ = ["ZoteroLocalReader", "export_for_zotero"]

# EOF
