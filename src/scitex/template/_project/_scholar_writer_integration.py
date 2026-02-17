#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar-Writer Integration Module

Sets up the directory structure and symlinks for bibliography sharing
between scitex.scholar and scitex.writer components.

Structure:
    project/
    ├── scholar/
    │   └── bib_files/
    │       └── merged_scholar.bib      ← Scholar writes here
    └── 00_shared/  (or scitex/writer/00_shared/)
        └── bib_files/
            └── merged_scholar.bib      ← Symlink to scholar's file

This enables:
- Scholar to manage bibliography (search, enrich, deduplicate)
- Writer to use the bibliography for LaTeX compilation
- Single source of truth, no duplication
"""

import os
from pathlib import Path
from typing import Optional, Dict

from scitex.logging import getLogger

logger = getLogger(__name__)


def setup_scholar_writer_integration(
    project_path: Path,
    force: bool = False,
) -> Dict[str, any]:
    """
    Set up scholar-writer integration structure with symlinks.

    Handles two project layouts:
    1. Standalone writer (flat): 00_shared/ at project root
       Creates: scholar/bib_files/
       Symlink: 00_shared/bib_files/merged_scholar.bib

    2. Nested writer (scitex ecosystem): scitex/writer/00_shared/
       Creates: scitex/scholar/bib_files/
       Symlink: scitex/writer/00_shared/bib_files/merged_scholar.bib

    Parameters
    ----------
    project_path : Path
        Root path of the project
    force : bool
        If True, recreate symlinks even if they exist

    Returns
    -------
    dict
        Result with keys: success, layout, scholar_dir, symlink_created, errors
    """
    result = {
        "success": True,
        "layout": None,
        "scholar_dir": None,
        "symlink_created": False,
        "errors": [],
    }

    try:
        project_path = Path(project_path)

        # Detect project layout
        nested_writer_bib = project_path / "scitex" / "writer" / "00_shared" / "bib_files"
        standalone_writer_bib = project_path / "00_shared" / "bib_files"

        if nested_writer_bib.exists():
            result["layout"] = "nested"
            writer_bib_dir = nested_writer_bib
            scholar_bib_dir = project_path / "scitex" / "scholar" / "bib_files"
        elif standalone_writer_bib.exists():
            result["layout"] = "standalone"
            writer_bib_dir = standalone_writer_bib
            scholar_bib_dir = project_path / "scholar" / "bib_files"
        else:
            result["layout"] = "unknown"
            logger.debug("Writer bib_files not found, skipping scholar setup")
            return result

        # Create scholar structure
        scholar_bib_dir.mkdir(parents=True, exist_ok=True)
        result["scholar_dir"] = str(scholar_bib_dir)

        # Create placeholder merged_scholar.bib
        scholar_merged = scholar_bib_dir / "merged_scholar.bib"
        if not scholar_merged.exists():
            placeholder = _get_placeholder_content()
            scholar_merged.write_text(placeholder)
            logger.debug(f"Created: {scholar_merged}")

        # Create symlink from writer to scholar
        writer_scholar_link = writer_bib_dir / "merged_scholar.bib"
        should_create = (
            force
            or (not writer_scholar_link.exists() and not writer_scholar_link.is_symlink())
        )

        if should_create:
            # Remove existing if forcing
            if writer_scholar_link.exists() or writer_scholar_link.is_symlink():
                writer_scholar_link.unlink()

            relative_path = os.path.relpath(scholar_merged, writer_scholar_link.parent)
            writer_scholar_link.symlink_to(relative_path)
            result["symlink_created"] = True
            logger.debug(f"Created symlink: {writer_scholar_link} → {relative_path}")

        return result

    except Exception as e:
        logger.warning(f"Failed to setup scholar-writer structure: {e}")
        result["success"] = False
        result["errors"].append(str(e))
        return result


def _get_placeholder_content() -> str:
    """Return placeholder content for merged_scholar.bib."""
    return """% ============================================================
% SciTeX Scholar Bibliography
% ============================================================
% This file is automatically populated when you:
% 1. Upload BibTeX files through Scholar
% 2. Save papers from search results
% 3. Run bibliography merge
%
% Entries will appear below.
% ============================================================

"""


def ensure_integration(project_path: Path) -> bool:
    """
    Convenience function to ensure integration exists.

    Parameters
    ----------
    project_path : Path
        Root path of the project

    Returns
    -------
    bool
        True if integration is set up (or already exists)
    """
    result = setup_scholar_writer_integration(project_path, force=False)
    return result["success"]


__all__ = ["setup_scholar_writer_integration", "ensure_integration"]

# EOF
