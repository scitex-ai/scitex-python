#!/usr/bin/env python3
"""Dataclasses for Zotero ↔ Scholar migration reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class MigratedItem:
    """A single migrated item."""

    zotero_key: str
    scholar_id: Optional[str]
    title: str
    doi: Optional[str]
    pdf_migrated: bool
    status: str  # "imported", "skipped", "failed"
    error: Optional[str] = None


@dataclass
class MigrationError:
    """An error during migration."""

    zotero_key: str
    title: str
    error: str


@dataclass
class MigrationReport:
    """Report from a Zotero ↔ Scholar migration operation."""

    direction: str  # "zotero_to_scholar" or "scholar_to_zotero"
    total_items: int = 0
    imported: int = 0
    skipped: int = 0
    failed: int = 0
    pdfs_copied: int = 0
    pdfs_missing: int = 0
    attachments_copied: int = 0
    errors: List[MigrationError] = field(default_factory=list)
    items: List[MigratedItem] = field(default_factory=list)

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Migration ({self.direction}): {self.total_items} items",
            f"  Imported: {self.imported}",
            f"  Skipped (duplicates): {self.skipped}",
            f"  Failed: {self.failed}",
            f"  PDFs copied: {self.pdfs_copied}",
            f"  PDFs missing: {self.pdfs_missing}",
        ]
        if self.errors:
            lines.append(f"  Errors ({len(self.errors)}):")
            for err in self.errors[:5]:
                lines.append(f"    - {err.title[:50]}: {err.error}")
            if len(self.errors) > 5:
                lines.append(f"    ... and {len(self.errors) - 5} more")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "direction": self.direction,
            "total_items": self.total_items,
            "imported": self.imported,
            "skipped": self.skipped,
            "failed": self.failed,
            "pdfs_copied": self.pdfs_copied,
            "pdfs_missing": self.pdfs_missing,
            "items": [
                {
                    "zotero_key": it.zotero_key,
                    "scholar_id": it.scholar_id,
                    "title": it.title,
                    "doi": it.doi,
                    "pdf_migrated": it.pdf_migrated,
                    "status": it.status,
                }
                for it in self.items
            ],
        }


@dataclass
class ExportPackage:
    """Package ready for Zotero File > Import."""

    bibtex_path: Path
    pdf_dir: Path
    total_papers: int
    total_pdfs: int
    instructions: str = ""

    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Export package: {self.total_papers} papers, {self.total_pdfs} PDFs\n"
            f"  BibTeX: {self.bibtex_path}\n"
            f"  PDFs:   {self.pdf_dir}\n"
            f"  {self.instructions}"
        )


@dataclass
class SyncDiffItem:
    """An item in a sync diff."""

    title: str
    doi: Optional[str]
    zotero_key: Optional[str] = None
    scholar_id: Optional[str] = None
    has_pdf_zotero: bool = False
    has_pdf_scholar: bool = False


@dataclass
class SyncDiff:
    """Comparison between Zotero and Scholar states."""

    only_in_zotero: List[SyncDiffItem] = field(default_factory=list)
    only_in_scholar: List[SyncDiffItem] = field(default_factory=list)
    in_both: List[SyncDiffItem] = field(default_factory=list)

    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Sync diff:\n"
            f"  Only in Zotero: {len(self.only_in_zotero)}\n"
            f"  Only in Scholar: {len(self.only_in_scholar)}\n"
            f"  In both: {len(self.in_both)}"
        )


# EOF
