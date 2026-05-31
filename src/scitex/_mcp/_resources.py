#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/_resources.py
"""Umbrella-only MCP documentation resources for AI agents.

Consolidates what used to live in the per-topic ``scitex._mcp_resources``
package (cheatsheet / session-tree / per-module docs / io-formats /
figrecipe / scholar library) into the single umbrella MCP entrypoint.
Static text lives in ``_resources_text``; this module only wires it onto
a FastMCP server.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from ._resources_text import (
    CHEATSHEET,
    FIGRECIPE_INTEGRATION,
    IO_FORMATS,
    MODULE_DOCS,
    SESSION_TREE,
)

__all__ = ["register_resources"]

SCITEX_BASE_DIR = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
SCITEX_SCHOLAR_DIR = SCITEX_BASE_DIR / "scholar"


def _get_scholar_dir() -> Path:
    """Get (creating if needed) the scholar data directory."""
    SCITEX_SCHOLAR_DIR.mkdir(parents=True, exist_ok=True)
    return SCITEX_SCHOLAR_DIR


def register_resources(mcp) -> None:
    """Register all umbrella MCP documentation resources."""

    @mcp.resource("scitex://cheatsheet")
    def cheatsheet() -> str:
        """Complete SciTeX quick reference for AI code generation."""
        return CHEATSHEET

    @mcp.resource("scitex://session-tree")
    def session_tree() -> str:
        """Explain the @stx.session output directory structure."""
        return SESSION_TREE

    @mcp.resource("scitex://module/io")
    def module_io() -> str:
        """stx.io module documentation - Universal File I/O."""
        return MODULE_DOCS["io"]

    @mcp.resource("scitex://module/plt")
    def module_plt() -> str:
        """stx.plt module documentation - Publication-ready figures."""
        return MODULE_DOCS["plt"]

    @mcp.resource("scitex://module/stats")
    def module_stats() -> str:
        """stx.stats module documentation - Statistical tests."""
        return MODULE_DOCS["stats"]

    @mcp.resource("scitex://module/scholar")
    def module_scholar() -> str:
        """stx.scholar module documentation - Literature management."""
        return MODULE_DOCS["scholar"]

    @mcp.resource("scitex://module/session")
    def module_session() -> str:
        """stx.session module documentation - Experiment tracking."""
        return MODULE_DOCS["session"]

    @mcp.resource("scitex://io-formats")
    def io_formats() -> str:
        """List all supported file formats for stx.io."""
        return IO_FORMATS

    @mcp.resource("scitex://plt-figrecipe")
    def figrecipe_integration() -> str:
        """stx.plt integration with FigRecipe for reproducible figures."""
        return FIGRECIPE_INTEGRATION

    @mcp.resource("scholar://library")
    def list_library_projects() -> str:
        """List all scholar library projects with paper counts."""
        library_dir = _get_scholar_dir() / "library"
        if not library_dir.exists():
            return json.dumps({"projects": [], "total": 0}, indent=2)
        projects = []
        for project_dir in library_dir.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith("."):
                pdf_count = len(list(project_dir.rglob("*.pdf")))
                metadata_count = len(list(project_dir.rglob("metadata.json")))
                projects.append(
                    {
                        "name": project_dir.name,
                        "pdf_count": pdf_count,
                        "paper_count": metadata_count,
                        "uri": f"scholar://library/{project_dir.name}",
                    }
                )
        return json.dumps(
            {
                "projects": projects,
                "total": len(projects),
                "library_path": str(library_dir),
            },
            indent=2,
        )

    @mcp.resource("scholar://library/{project}")
    def get_library_project(project: str) -> str:
        """Get papers in a specific library project."""
        library_dir = _get_scholar_dir() / "library" / project
        if not library_dir.exists():
            return json.dumps({"error": f"Project not found: {project}"}, indent=2)
        metadata_files = list(library_dir.rglob("metadata.json"))
        papers = []
        for meta_file in metadata_files[:100]:
            try:
                with open(meta_file) as f:
                    meta = json.load(f)
                pdf_exists = any(meta_file.parent.glob("*.pdf"))
                papers.append(
                    {
                        "id": meta_file.parent.name,
                        "title": meta.get("title"),
                        "doi": meta.get("doi"),
                        "authors": meta.get("authors", [])[:3],
                        "year": meta.get("year"),
                        "has_pdf": pdf_exists,
                    }
                )
            except Exception:
                pass
        return json.dumps(
            {"project": project, "paper_count": len(papers), "papers": papers},
            indent=2,
        )

    @mcp.resource("scholar://bibtex")
    def list_bibtex_files() -> str:
        """List recent BibTeX files in scholar directory."""
        scholar_dir = _get_scholar_dir()
        bib_files = []
        for bib_file in sorted(
            scholar_dir.rglob("*.bib"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:20]:
            mtime = datetime.fromtimestamp(bib_file.stat().st_mtime)
            bib_files.append(
                {
                    "name": bib_file.name,
                    "path": str(bib_file),
                    "modified": mtime.isoformat(),
                    "uri": f"scholar://bibtex/{bib_file.name}",
                }
            )
        return json.dumps(
            {"bibtex_files": bib_files, "total": len(bib_files)}, indent=2
        )

    @mcp.resource("scholar://bibtex/{filename}")
    def get_bibtex_file(filename: str) -> str:
        """Read a BibTeX file by name."""
        scholar_dir = _get_scholar_dir()
        bib_files = list(scholar_dir.rglob(filename))
        if not bib_files:
            return json.dumps({"error": f"BibTeX file not found: {filename}"}, indent=2)
        with open(bib_files[0]) as f:
            return f.read()


# EOF
