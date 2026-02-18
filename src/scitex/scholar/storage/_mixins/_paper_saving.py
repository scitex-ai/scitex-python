#!/usr/bin/env python3
# Timestamp: "2026-01-24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/scholar/storage/_mixins/_paper_saving.py

"""
Paper saving mixin for LibraryManager.
"""

from __future__ import annotations

import json
import re
from collections import OrderedDict
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from scitex import logging
from scitex.scholar._utils import TextNormalizer

if TYPE_CHECKING:
    from scitex.scholar.core.Paper import Paper

logger = logging.getLogger(__name__)


class PaperSavingMixin:
    """Mixin providing paper saving methods."""

    def save_resolved_paper(
        self,
        paper_data: Optional[Paper] = None,
        title: Optional[str] = None,
        doi: Optional[str] = None,
        authors: Optional[List[str]] = None,
        year: Optional[int] = None,
        journal: Optional[str] = None,
        abstract: Optional[str] = None,
        volume: Optional[str] = None,
        issue: Optional[str] = None,
        pages: Optional[str] = None,
        publisher: Optional[str] = None,
        issn: Optional[str] = None,
        short_journal: Optional[str] = None,
        citation_count: Optional[int] = None,
        impact_factor: Optional[float] = None,
        doi_source: Optional[str] = None,
        title_source: Optional[str] = None,
        abstract_source: Optional[str] = None,
        authors_source: Optional[str] = None,
        year_source: Optional[str] = None,
        journal_source: Optional[str] = None,
        library_id: Optional[str] = None,
        project: Optional[str] = None,
        metadata: Optional[Dict] = None,
        bibtex_source: Optional[str] = None,
        source: Optional[str] = None,
        paper_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Save successfully resolved paper to Scholar library."""
        # Extract fields from paper_data if provided
        if paper_data is not None:
            (
                title,
                doi,
                authors,
                year,
                journal,
                abstract,
                publisher,
                impact_factor,
                library_id,
            ) = self._extract_paper_data_fields(
                paper_data,
                title,
                doi,
                authors,
                year,
                journal,
                abstract,
                publisher,
                impact_factor,
                library_id,
            )

        # Handle legacy parameters
        if paper_id and not library_id:
            library_id = paper_id
        if source and not doi_source:
            doi_source = source

        paper_info = {
            "title": title,
            "year": year,
            "authors": authors or [],
            "doi": doi,
            "journal": journal,
        }

        # Use metadata dict as fallback
        if metadata:
            if not journal:
                paper_info["journal"] = metadata.get("journal")
            if not year:
                paper_info["year"] = metadata.get("year")
            if not authors:
                paper_info["authors"] = metadata.get("authors") or []

        # Check for existing paper (deduplication)
        check_metadata = {
            "doi": doi,
            "title": title,
            "authors": authors or [],
            "year": year,
        }
        existing_paper_dir = self.dedup_manager.check_for_existing_paper(check_metadata)

        if existing_paper_dir:
            logger.info(f"Found existing paper: {existing_paper_dir.name}")
            master_storage_path = existing_paper_dir
            paper_id = existing_paper_dir.name
            readable_name = None
        else:
            storage_path, readable_name, paper_id = (
                self.config.path_manager.get_paper_storage_paths(
                    doi=doi,
                    title=title,
                    authors=authors or [],
                    year=year,
                    journal=journal,
                    project="MASTER",
                )
            )
            master_storage_path = storage_path
            if library_id:
                paper_id = library_id

        master_metadata_file = master_storage_path / "metadata.json"

        existing_metadata = {}
        if master_metadata_file.exists():
            try:
                with open(master_metadata_file) as file_:
                    existing_metadata = json.load(file_)
            except (OSError, json.JSONDecodeError):
                existing_metadata = {}

        comprehensive_metadata = self._build_comprehensive_metadata(
            existing_metadata=existing_metadata,
            title=title,
            doi=doi,
            authors=authors,
            year=year,
            journal=journal,
            abstract=abstract,
            volume=volume,
            issue=issue,
            pages=pages,
            publisher=publisher,
            issn=issn,
            short_journal=short_journal,
            citation_count=citation_count,
            impact_factor=impact_factor,
            doi_source=doi_source,
            title_source=title_source,
            abstract_source=abstract_source,
            authors_source=authors_source,
            year_source=year_source,
            journal_source=journal_source,
            paper_id=paper_id,
            master_storage_path=master_storage_path,
            master_metadata_file=master_metadata_file,
            readable_name=readable_name,
            source=source,
            metadata=metadata,
        )

        comprehensive_metadata_plain = self._dotdict_to_dict(comprehensive_metadata)
        standardized_metadata = self._convert_to_standardized_metadata(
            comprehensive_metadata_plain
        )

        final_structure = self._create_final_structure(
            standardized_metadata,
            comprehensive_metadata_plain,
            paper_id,
            master_storage_path,
            readable_name,
            master_metadata_file,
        )

        with open(master_metadata_file, "w") as file_:
            json.dump(final_structure, file_, indent=2, ensure_ascii=False)

        logger.success(f"Saved paper to MASTER Scholar library: {paper_id}")

        # Create project symlinks if needed
        if self.project and self.project not in ["master", "MASTER"]:
            try:
                readable_name = self._generate_readable_name(
                    comprehensive_metadata=comprehensive_metadata,
                    master_storage_path=master_storage_path,
                    authors=authors,
                    year=year,
                    journal=journal,
                )
                # ~/.scitex/scholar/library/{project}/ view
                self._create_project_symlink(
                    master_storage_path=master_storage_path,
                    project=self.project,
                    readable_name=readable_name,
                )
                # {project_dir}/scitex/scholar/library/{project}/ view
                self._create_project_local_symlink(
                    master_storage_path=master_storage_path,
                    readable_name=readable_name,
                )
            except Exception as exc_:
                logger.error(f"Failed to create symlink for {paper_id}: {exc_}")

        return paper_id

    def _extract_paper_data_fields(
        self,
        paper_data,
        title,
        doi,
        authors,
        year,
        journal,
        abstract,
        publisher,
        impact_factor,
        library_id,
    ):
        """Extract fields from paper_data object."""
        if hasattr(paper_data, "metadata"):
            title = title or (paper_data.metadata.basic.title or "")
            doi = doi or (paper_data.metadata.id.doi or "")
            authors = authors or paper_data.metadata.basic.authors
            year = year or paper_data.metadata.basic.year
            journal = journal or paper_data.metadata.publication.journal
            abstract = abstract or paper_data.metadata.basic.abstract
            publisher = publisher or paper_data.metadata.publication.publisher
            impact_factor = (
                impact_factor or paper_data.metadata.publication.impact_factor
            )
            library_id = library_id or paper_data.container.library_id
        elif isinstance(paper_data, dict):
            title = title or paper_data.get("title", "")
            doi = doi or paper_data.get("doi", "")
            authors = authors or paper_data.get("authors", [])
            year = year or paper_data.get("year")
            journal = journal or paper_data.get("journal")
            abstract = abstract or paper_data.get("abstract")
            publisher = publisher or paper_data.get("publisher")
            impact_factor = impact_factor or paper_data.get("impact_factor")
            library_id = (
                library_id
                or paper_data.get("scitex_id")
                or paper_data.get("scholar_id")
            )
        return (
            title,
            doi,
            authors,
            year,
            journal,
            abstract,
            publisher,
            impact_factor,
            library_id,
        )

    def _build_comprehensive_metadata(self, **kwargs) -> Dict[str, Any]:
        """Build comprehensive metadata dictionary."""
        existing_metadata = kwargs["existing_metadata"]
        title = kwargs["title"]
        abstract = kwargs["abstract"]
        metadata = kwargs["metadata"]
        source = kwargs["source"]
        doi_source = kwargs["doi_source"]

        clean_title = TextNormalizer.clean_metadata_text(
            existing_metadata.get("title", title)
        )

        clean_abstract = None
        if abstract:
            clean_abstract = TextNormalizer.clean_metadata_text(abstract)
        elif metadata and metadata.get("abstract"):
            clean_abstract = TextNormalizer.clean_metadata_text(metadata["abstract"])
        elif existing_metadata.get("abstract"):
            clean_abstract = TextNormalizer.clean_metadata_text(
                existing_metadata["abstract"]
            )

        doi_source_value = doi_source or existing_metadata.get("doi_source")
        if not doi_source_value and source:
            doi_source_value = self._normalize_source(source)

        return {
            "title": clean_title,
            "title_source": kwargs["title_source"]
            or existing_metadata.get("title_source", "input"),
            "doi": existing_metadata.get("doi", kwargs["doi"]),
            "doi_source": doi_source_value,
            "year": existing_metadata.get("year", kwargs["year"]),
            "year_source": kwargs["year_source"]
            or existing_metadata.get(
                "year_source", "input" if kwargs["year"] else None
            ),
            "authors": existing_metadata.get("authors", kwargs["authors"] or []),
            "authors_source": kwargs["authors_source"]
            or existing_metadata.get(
                "authors_source", "input" if kwargs["authors"] else None
            ),
            "journal": existing_metadata.get("journal", kwargs["journal"]),
            "journal_source": kwargs["journal_source"]
            or existing_metadata.get(
                "journal_source", "input" if kwargs["journal"] else None
            ),
            "volume": existing_metadata.get("volume", kwargs["volume"]),
            "issue": existing_metadata.get("issue", kwargs["issue"]),
            "pages": existing_metadata.get("pages", kwargs["pages"]),
            "publisher": existing_metadata.get("publisher", kwargs["publisher"]),
            "issn": existing_metadata.get("issn", kwargs["issn"]),
            "short_journal": existing_metadata.get(
                "short_journal", kwargs["short_journal"]
            ),
            "abstract": existing_metadata.get("abstract", clean_abstract),
            "abstract_source": kwargs["abstract_source"]
            or existing_metadata.get("abstract_source", "input" if abstract else None),
            "citation_count": existing_metadata.get(
                "citation_count", kwargs["citation_count"]
            ),
            "impact_factor": existing_metadata.get(
                "impact_factor", kwargs["impact_factor"]
            ),
            "scitex_id": existing_metadata.get(
                "scitex_id", existing_metadata.get("scholar_id", kwargs["paper_id"])
            ),
            "created_at": existing_metadata.get(
                "created_at", datetime.now().isoformat()
            ),
            "created_by": existing_metadata.get("created_by", "SciTeX Scholar"),
            "updated_at": datetime.now().isoformat(),
            "projects": existing_metadata.get(
                "projects", [] if self.project == "master" else [self.project]
            ),
            "master_storage_path": str(kwargs["master_storage_path"]),
            "readable_name": kwargs["readable_name"],
            "metadata_file": str(kwargs["master_metadata_file"]),
        }

    def _normalize_source(self, source: str) -> str:
        """Normalize legacy source parameter to standard format."""
        if "crossref" in source.lower():
            return "crossref"
        elif "semantic" in source.lower():
            return "semantic_scholar"
        elif "pubmed" in source.lower():
            return "pubmed"
        elif "openalex" in source.lower():
            return "openalex"
        return source

    def _create_final_structure(
        self,
        standardized_metadata,
        comprehensive_metadata_plain,
        paper_id,
        master_storage_path,
        readable_name,
        master_metadata_file,
    ) -> OrderedDict:
        """Create final structure for saving."""
        return OrderedDict(
            [
                ("metadata", standardized_metadata),
                (
                    "container",
                    OrderedDict(
                        [
                            (
                                "scitex_id",
                                comprehensive_metadata_plain.get("scitex_id"),
                            ),
                            ("library_id", paper_id),
                            (
                                "created_at",
                                comprehensive_metadata_plain.get("created_at"),
                            ),
                            (
                                "created_by",
                                comprehensive_metadata_plain.get("created_by"),
                            ),
                            (
                                "updated_at",
                                comprehensive_metadata_plain.get("updated_at"),
                            ),
                            (
                                "projects",
                                comprehensive_metadata_plain.get("projects", []),
                            ),
                            ("master_storage_path", str(master_storage_path)),
                            ("readable_name", readable_name),
                            ("metadata_file", str(master_metadata_file)),
                            (
                                "pdf_downloaded_at",
                                comprehensive_metadata_plain.get("pdf_downloaded_at"),
                            ),
                            (
                                "pdf_size_bytes",
                                comprehensive_metadata_plain.get("pdf_size_bytes"),
                            ),
                        ]
                    ),
                ),
            ]
        )

    def save_unresolved_paper(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        reason: str = "DOI not found",
        bibtex_source: Optional[str] = None,
    ) -> None:
        """Save paper that couldn't be resolved to unresolved directory."""
        clean_title = TextNormalizer.clean_metadata_text(title) if title else ""
        unresolved_info = {
            "title": clean_title,
            "year": year,
            "authors": authors or [],
            "reason": reason,
            "bibtex_source": bibtex_source,
            "project": self.project,
            "created_at": datetime.now().isoformat(),
            "created_by": "SciTeX Scholar",
        }

        project_lib_path = (
            self.config.path_manager.get_scholar_library_path() / self.project
        )
        unresolved_dir = project_lib_path / "unresolved"
        unresolved_dir.mkdir(parents=True, exist_ok=True)

        safe_title = title or "untitled"
        safe_title = re.sub(r"[^\w\s-]", "", safe_title)[:50]
        safe_title = re.sub(r"[-\s]+", "_", safe_title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unresolved_file = unresolved_dir / f"{safe_title}_{timestamp}.json"

        with open(unresolved_file, "w") as file_:
            json.dump(unresolved_info, file_, indent=2, ensure_ascii=False)

        logger.warning(f"Saved unresolved entry: {unresolved_file.name}")


# EOF
