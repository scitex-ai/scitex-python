#!/usr/bin/env python3
# Timestamp: "2026-01-24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/scholar/storage/_mixins/_symlink_handlers.py

"""
Symlink handling mixin for LibraryManager.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class SymlinkHandlersMixin:
    """Mixin providing symlink handling methods."""

    def _generate_readable_name(
        self,
        comprehensive_metadata: Dict,
        master_storage_path: Path,
        authors: Optional[List[str]] = None,
        year: Optional[int] = None,
        journal: Optional[str] = None,
    ) -> str:
        """Generate readable symlink name from metadata."""
        from scitex.dict import DotDict

        # Extract author
        first_author = "Unknown"
        if authors and len(authors) > 0:
            author_parts = authors[0].split()
            first_author = (
                author_parts[-1] if len(author_parts) > 1 else author_parts[0]
            )
            first_author = "".join(c for c in first_author if c.isalnum() or c == "-")[
                :20
            ]

        # Format year
        if isinstance(year, DotDict):
            year = None

        if isinstance(year, str) and year.isdigit():
            year = int(year)

        year_str = f"{year:04d}" if isinstance(year, int) else "0000"

        # Clean journal name
        journal_clean = "Unknown"
        if journal:
            journal_clean = self.config.path_manager._sanitize_filename(journal)[:30]
            if not journal_clean:
                journal_clean = "Unknown"

        # Get citation count and impact factor
        cc, if_val = self._extract_cc_and_if(comprehensive_metadata)

        # Count PDFs
        pdf_files = list(master_storage_path.glob("*.pdf"))
        n_pdfs = len(pdf_files)

        readable_name = f"PDF-{n_pdfs:02d}_CC-{cc:06d}_IF-{int(if_val):03d}_{year_str}_{first_author}_{journal_clean}"
        return readable_name

    def _extract_cc_and_if(self, comprehensive_metadata: Dict) -> tuple:
        """Extract citation count and impact factor from metadata."""
        if "metadata" in comprehensive_metadata:
            metadata_section = comprehensive_metadata.get("metadata", {})
            cc_val = metadata_section.get("citation_count", {})
            if isinstance(cc_val, dict):
                cc = cc_val.get("total", 0) or 0
            else:
                cc = cc_val or 0

            publication_section = metadata_section.get("publication", {})
            if_val = publication_section.get("impact_factor", 0.0) or 0.0
        else:
            cc_val = comprehensive_metadata.get("citation_count", 0)
            if isinstance(cc_val, dict):
                cc = cc_val.get("total", 0) or 0
            else:
                cc = cc_val or 0

            if_val = (
                comprehensive_metadata.get("journal_impact_factor")
                or comprehensive_metadata.get("impact_factor")
                or comprehensive_metadata.get("publication", {}).get("impact_factor")
            )
            if isinstance(if_val, dict):
                if_val = if_val.get("value", 0.0) or 0.0
            else:
                if_val = if_val or 0.0

        return cc, if_val

    def update_symlink(
        self,
        master_storage_path: Path,
        project: str,
        metadata: Optional[Dict] = None,
    ) -> Optional[Path]:
        """Update project symlink to reflect current paper status."""
        try:
            if metadata is None:
                metadata_file = master_storage_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                else:
                    logger.warning(f"No metadata found for {master_storage_path.name}")
                    return None

            # Extract metadata from nested structure if needed
            if "metadata" in metadata:
                meta_section = metadata.get("metadata", {})
                basic_section = meta_section.get("basic", {})
                pub_section = meta_section.get("publication", {})
                authors = basic_section.get("authors")
                year = basic_section.get("year")
                journal = pub_section.get("journal")
            else:
                authors = metadata.get("authors")
                year = metadata.get("year")
                journal = metadata.get("journal")

            readable_name = self._generate_readable_name(
                comprehensive_metadata=metadata,
                master_storage_path=master_storage_path,
                authors=authors,
                year=year,
                journal=journal,
            )

            return self._create_project_symlink(
                master_storage_path=master_storage_path,
                project=project,
                readable_name=readable_name,
            )
        except Exception as exc_:
            logger.error(
                f"Failed to update symlink for {master_storage_path.name}: {exc_}"
            )
            return None

    def _create_project_symlink(
        self, master_storage_path: Path, project: str, readable_name: str
    ) -> Optional[Path]:
        """Create symlink in project directory pointing to master storage."""
        try:
            project_dir = self.config.path_manager.get_library_project_dir(project)
            symlink_path = project_dir / readable_name
            master_id = master_storage_path.name

            # Remove old symlinks pointing to the same master entry
            for existing_link in project_dir.iterdir():
                if not existing_link.is_symlink():
                    continue

                try:
                    target = existing_link.resolve()
                    if target.name == master_id and existing_link.name != readable_name:
                        logger.debug(f"Removing old symlink: {existing_link.name}")
                        existing_link.unlink()
                except Exception as e:
                    logger.debug(f"Skipping broken symlink {existing_link.name}: {e}")
                    continue

            # Create new symlink
            if not symlink_path.exists():
                relative_path = os.path.relpath(master_storage_path, project_dir)
                symlink_path.symlink_to(relative_path)
                logger.success(
                    f"Created project symlink: {symlink_path} -> {relative_path}"
                )
            else:
                logger.debug(f"Project symlink already exists: {symlink_path}")

            return symlink_path

        except Exception as exc_:
            logger.warning(f"Failed to create project symlink: {exc_}")
            return None

    def _create_project_local_symlink(
        self,
        master_storage_path: Path,
        readable_name: str,
    ) -> Optional[Path]:
        """Create symlink inside the project's own directory tree.

        Target location: ``{project_dir}/scitex/scholar/library/{project}/{readable_name}``
        Target of symlink: absolute path to master storage entry.

        This mirrors the ``~/.scitex/scholar/library/{project}/`` view directly
        inside the user's code project so papers are visible alongside source code.

        Args:
            master_storage_path: Absolute path to the MASTER entry directory.
            readable_name: Human-readable symlink name (PDF-xx_CC-... format).

        Returns
        -------
            Path to the created symlink, or None on failure.
        """
        if not getattr(self, "project_dir", None):
            return None
        if not self.project or self.project in ("master", "MASTER"):
            return None

        try:
            local_lib = (
                Path(self.project_dir) / "scitex" / "scholar" / "library" / self.project
            )
            local_lib.mkdir(parents=True, exist_ok=True)

            symlink_path = local_lib / readable_name

            # Remove stale symlinks pointing to the same master entry
            master_id = master_storage_path.name
            for existing in local_lib.iterdir():
                if not existing.is_symlink():
                    continue
                try:
                    if (
                        existing.resolve().name == master_id
                        and existing.name != readable_name
                    ):
                        existing.unlink()
                except Exception:
                    pass

            if not symlink_path.exists():
                # Use absolute path — relative would break across project moves
                symlink_path.symlink_to(master_storage_path.resolve())
                logger.success(
                    f"Created project-local symlink: {symlink_path} -> {master_storage_path}"
                )
            return symlink_path

        except Exception as exc_:
            logger.warning(f"Failed to create project-local symlink: {exc_}")
            return None

    def _ensure_project_symlink(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        paper_id: str = None,
        master_storage_path: Path = None,
    ) -> None:
        """Ensure project symlink exists for paper in master library."""
        try:
            if not paper_id or not master_storage_path:
                return

            project_lib_path = (
                self.config.path_manager.get_scholar_library_path() / self.project
            )
            project_lib_path.mkdir(parents=True, exist_ok=True)

            paper_info = {"title": title, "year": year, "authors": authors or []}
            readable_paths = self._call_path_manager_get_storage_paths(
                paper_info=paper_info, collection_name=self.project
            )
            readable_name = readable_paths["readable_name"]
            symlink_path = project_lib_path / readable_name
            relative_path = f"../MASTER/{paper_id}"

            if not symlink_path.exists():
                symlink_path.symlink_to(relative_path)
                logger.info(
                    f"Created project symlink: {readable_name} -> {relative_path}"
                )
        except Exception as exc_:
            logger.debug(f"Error creating project symlink: {exc_}")


# EOF
