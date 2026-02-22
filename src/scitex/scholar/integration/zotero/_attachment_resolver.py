#!/usr/bin/env python3
"""Resolve Zotero attachment paths to actual file locations.

Zotero stores attachment paths in several formats depending on linkMode:
- linkMode 0/1: Imported file/URL -> "storage:<filename>" -> <base>/storage/<key>/<filename>
- linkMode 2: Linked file -> absolute or relative path on disk
- linkMode 3: Embedded note -> no file
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ResolvedAttachment:
    """A resolved Zotero attachment."""

    path: Path
    filename: str
    content_type: str
    is_pdf: bool
    link_mode: int
    zotero_key: str
    size_bytes: int


class ZoteroAttachmentResolver:
    """Resolve Zotero attachment paths to actual filesystem locations.

    Parameters
    ----------
    zotero_base_dir : Path
        Zotero data directory (parent of zotero.sqlite, contains storage/).
    """

    def __init__(self, zotero_base_dir: Path):
        self.base_dir = Path(zotero_base_dir)
        self.storage_dir = self.base_dir / "storage"

    def resolve(
        self,
        path_field: Optional[str],
        item_key: str,
        link_mode: int,
        content_type: str = "",
    ) -> Optional[Path]:
        """Resolve a Zotero attachment path to an actual file.

        Parameters
        ----------
        path_field : str or None
            Value from itemAttachments.path column.
        item_key : str
            Zotero item key (8-char alphanumeric, e.g. '39KUWQ3Y').
        link_mode : int
            0=imported file, 1=imported URL, 2=linked file, 3=embedded note.
        content_type : str
            MIME type (e.g. 'application/pdf').

        Returns
        -------
        Path or None
            Resolved path if file exists, None otherwise.
        """
        if link_mode == 3 or not path_field:
            return None

        # linkMode 0 or 1: stored in storage/<key>/<filename>
        if path_field.startswith("storage:"):
            filename = path_field[len("storage:") :]
            full_path = (self.storage_dir / item_key / filename).resolve()
            # Guard against path traversal (e.g. "storage:../../etc/passwd")
            if not str(full_path).startswith(str(self.storage_dir.resolve())):
                return None
            return full_path if full_path.exists() else None

        # linkMode 2: linked file (absolute or relative path)
        if link_mode == 2:
            p = Path(path_field)
            if p.is_absolute() and p.exists():
                return p
            # Try relative to base dir
            rel = (self.base_dir / path_field).resolve()
            if not str(rel).startswith(str(self.base_dir.resolve())):
                return None
            if rel.exists():
                return rel

        return None

    def list_attachments_for_items(
        self,
        item_ids: List[int],
        conn: sqlite3.Connection,
        pdf_only: bool = True,
    ) -> Dict[int, List[ResolvedAttachment]]:
        """Batch-resolve attachments for multiple parent items.

        Parameters
        ----------
        item_ids : list of int
            Parent item IDs to find attachments for.
        conn : sqlite3.Connection
            Open SQLite connection to Zotero database.
        pdf_only : bool
            If True (default), only return PDF attachments.

        Returns
        -------
        dict
            Mapping from parent itemID to list of ResolvedAttachment.
        """
        if not item_ids:
            return {}

        ids_str = ",".join(str(i) for i in item_ids)
        content_filter = "AND ia.contentType = 'application/pdf'" if pdf_only else ""

        rows = conn.execute(
            f"""
            SELECT ia.parentItemID, ia.path, ia.contentType, ia.linkMode,
                   i.key
            FROM itemAttachments ia
            JOIN items i ON ia.itemID = i.itemID
            WHERE ia.parentItemID IN ({ids_str})
            {content_filter}
            """
        ).fetchall()

        result: Dict[int, List[ResolvedAttachment]] = {i: [] for i in item_ids}

        for row in rows:
            parent_id = row[0]
            path_field = row[1]
            content_type = row[2] or ""
            link_mode = row[3]
            item_key = row[4]

            resolved = self.resolve(path_field, item_key, link_mode, content_type)
            if resolved is None:
                continue

            try:
                size = resolved.stat().st_size
            except OSError:
                size = 0

            attachment = ResolvedAttachment(
                path=resolved,
                filename=resolved.name,
                content_type=content_type,
                is_pdf="pdf" in content_type.lower(),
                link_mode=link_mode,
                zotero_key=item_key,
                size_bytes=size,
            )
            result[parent_id].append(attachment)

        return result


# EOF
