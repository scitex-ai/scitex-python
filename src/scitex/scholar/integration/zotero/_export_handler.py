#!/usr/bin/env python3
"""Scholar -> Zotero export handler (import-ready packages)."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Optional

from scitex import logging
from scitex.scholar.core.Paper import Paper
from scitex.scholar.core.Papers import Papers
from scitex.scholar.storage import LibraryManager

from .local_reader import export_for_zotero
from .migration_report import ExportPackage

logger = logging.getLogger(__name__)


class ZoteroExportHandler:
    """Export Scholar papers as Zotero-importable packages.

    Creates a directory with papers.bib + pdfs/ that Zotero can import
    via File > Import.

    Parameters
    ----------
    library_manager : LibraryManager
        Scholar library manager.
    project : str
        Scholar project name.
    """

    def __init__(self, library_manager: LibraryManager, project: str):
        self._library_manager = library_manager
        self._project = project

    def export_for_import(
        self,
        project: Optional[str] = None,
        output_dir: Optional[str | Path] = None,
        include_pdfs: bool = True,
    ) -> ExportPackage:
        """Export Scholar papers as a Zotero-importable package.

        Parameters
        ----------
        project : str, optional
            Scholar project to export (default: self._project).
        output_dir : str or Path, optional
            Output directory. Default: /tmp/scitex_zotero_export/<project>/
        include_pdfs : bool
            Include PDF files in the package.

        Returns
        -------
        ExportPackage
        """
        project = project or self._project
        if output_dir is None:
            output_dir = Path(f"/tmp/scitex_zotero_export/{project}")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_dir = output_dir / "pdfs"
        pdf_dir.mkdir(exist_ok=True)

        master_dir = self._library_manager.config.path_manager.library_dir / "MASTER"
        papers = []
        pdf_count = 0

        if not master_dir.exists():
            logger.warning(f"MASTER directory not found: {master_dir}")
            return ExportPackage(
                bibtex_path=output_dir / "papers.bib",
                pdf_dir=pdf_dir,
                total_papers=0,
                total_pdfs=0,
                instructions="No papers found in Scholar library.",
            )

        for entry_dir in sorted(master_dir.iterdir()):
            metadata_file = entry_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file) as f:
                    meta = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue

            paper = self._metadata_to_paper(meta)
            if paper is None:
                continue
            papers.append(paper)

            if include_pdfs:
                pdf_count += self._copy_pdfs(entry_dir, paper, pdf_dir)

        bibtex_path = output_dir / "papers.bib"
        if papers:
            papers_collection = Papers(papers, project=project)
            export_for_zotero(papers_collection, bibtex_path, fmt="bibtex")

        instructions = (
            f"To import into Zotero:\n"
            f"1. Open Zotero\n"
            f"2. File > Import > {bibtex_path}\n"
            f"3. Drag-drop PDFs from {pdf_dir}/ onto imported items"
        )

        pkg = ExportPackage(
            bibtex_path=bibtex_path,
            pdf_dir=pdf_dir,
            total_papers=len(papers),
            total_pdfs=pdf_count,
            instructions=instructions,
        )
        logger.info(pkg.summary())
        return pkg

    @staticmethod
    def _copy_pdfs(entry_dir: Path, paper: Paper, pdf_dir: Path) -> int:
        """Copy PDFs from a MASTER entry to the export pdf_dir. Returns count."""
        copied = 0
        for pdf_file in entry_dir.glob("*.pdf"):
            dest_name = _scholar_pdf_name(paper, pdf_file.name)
            dest = pdf_dir / dest_name
            if not dest.exists():
                shutil.copy2(pdf_file, dest)
                copied += 1
        return copied

    @staticmethod
    def _metadata_to_paper(raw: dict) -> Optional[Paper]:
        """Convert Scholar metadata.json dict to a Paper object.

        Handles the nested structure: metadata.basic, metadata.id, metadata.publication.
        """
        try:
            meta = raw.get("metadata", raw)  # handle both nested and flat
            basic = meta.get("basic", meta)
            id_info = meta.get("id", meta)
            pub = meta.get("publication", meta)

            paper = Paper()
            paper.metadata.basic.title = basic.get("title", "")
            paper.metadata.basic.authors = basic.get("authors", [])
            paper.metadata.basic.year = basic.get("year")
            paper.metadata.basic.abstract = basic.get("abstract", "")
            doi = id_info.get("doi", "")
            if doi:
                paper.metadata.set_doi(doi)
            paper.metadata.publication.journal = pub.get("journal", "")
            paper.metadata.publication.volume = pub.get("volume", "")
            paper.metadata.publication.issue = pub.get("issue", "")
            paper.metadata.publication.pages = pub.get("pages", "")
            paper.metadata.publication.publisher = pub.get("publisher", "")
            return paper
        except Exception:
            return None


def _scholar_pdf_name(paper: Paper, fallback: str = "paper.pdf") -> str:
    """Generate a standardized PDF filename from paper metadata."""
    authors = getattr(paper.metadata.basic, "authors", []) or []
    first_author = authors[0].split(",")[0].strip() if authors else "Unknown"
    year = getattr(paper.metadata.basic, "year", None) or "NoYear"
    journal = getattr(paper.metadata.publication, "journal", None) or "NoJournal"
    name = f"{first_author}-{year}-{journal}.pdf"
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name if name != "Unknown-NoYear-NoJournal.pdf" else fallback


# EOF
