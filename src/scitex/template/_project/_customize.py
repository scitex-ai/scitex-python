#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/template/_project/_customize.py
"""Customize cloned templates with project-specific metadata.

After a template is cloned, these functions replace placeholder values
(title, author, description) with actual project metadata.

All functions accept a plain metadata dict — no Django dependencies.
"""

from pathlib import Path
from typing import Dict

from scitex.logging import getLogger

logger = getLogger(__name__)

__all__ = ["customize_template", "customize_minimal_template"]


def _project_meta(metadata: Dict) -> Dict:
    """Normalise metadata keys to a standard set with defaults."""
    return {
        "name": metadata.get("name", "Untitled Project"),
        "description": metadata.get("description", ""),
        "owner": metadata.get("owner", ""),
        "owner_full_name": metadata.get("owner_full_name", ""),
        "id": metadata.get("id", ""),
        "created_at": metadata.get("created_at", ""),
        "progress": metadata.get("progress", 0),
        "hypotheses": metadata.get("hypotheses", ""),
    }


def customize_template(
    project_dir: str,
    metadata: Dict,
    template_type: str = "research",
) -> None:
    """Customise a cloned template with project-specific information.

    Replaces placeholder text in README.md, title.tex, and authors.tex.

    Parameters
    ----------
    project_dir : str
        Path to the project directory.
    metadata : dict
        Project metadata. Expected keys: ``name``, ``description``,
        ``owner`` (username), ``owner_full_name``.
    template_type : str
        Template type hint (currently unused, reserved for future).
    """
    path = Path(project_dir)
    meta = _project_meta(metadata)

    _update_readme(path, meta)
    _update_title_tex(path, meta)
    _update_authors_tex(path, meta)

    logger.info(f"Customized template for project: {meta['name']}")


def customize_minimal_template(
    project_dir: str,
    metadata: Dict,
) -> None:
    """Customise a minimal (scitex-writer) template with project metadata.

    Writes ``title.tex`` and ``authors.tex`` under ``00_shared/``
    (direct clone) or ``scitex/writer/00_shared/`` (nested layout).

    Parameters
    ----------
    project_dir : str
        Path to the project directory.
    metadata : dict
        Project metadata.
    """
    path = Path(project_dir)
    meta = _project_meta(metadata)

    # Try direct clone path first, then nested layout
    for title_file in [
        path / "00_shared" / "title.tex",
        path / "scitex" / "writer" / "00_shared" / "title.tex",
    ]:
        if title_file.exists():
            title_file.write_text(
                f"%% -*- coding: utf-8 -*-\n\\title{{{meta['name']}}}\n\n%%%% EOF\n"
            )
            break

    author_name = meta["owner_full_name"] or meta["owner"]
    if author_name:
        for author_file in [
            path / "00_shared" / "authors.tex",
            path / "scitex" / "writer" / "00_shared" / "authors.tex",
        ]:
            if author_file.exists():
                author_file.write_text(
                    f"%% -*- coding: utf-8 -*-\n"
                    f"\\author[1]{{{author_name}\\corref{{cor1}}}}\n\n"
                    f"\\address[1]{{Institution, Department, City, Country}}\n\n"
                    f"\\cortext[cor1]{{Corresponding author.}}\n\n"
                    f"%%%% EOF\n"
                )
                break

    logger.info(f"Customized minimal template for project: {meta['name']}")


# ---- Internal helpers -------------------------------------------------------


def _update_readme(path: Path, meta: Dict) -> None:
    """Replace placeholder text in README.md."""
    readme = path / "README.md"
    if not readme.exists():
        return

    content = readme.read_text()
    content = content.replace("# SciTeX Example Research Project", f"# {meta['name']}")
    content = content.replace(
        "This is an example research project",
        meta["description"] or "Research project created with SciTeX Cloud",
    )
    readme.write_text(content)


def _update_title_tex(path: Path, meta: Dict) -> None:
    """Write project name to title.tex if found."""
    for candidate in [
        path / "00_shared" / "title.tex",
        path / "paper" / "manuscript" / "src" / "title.tex",
        path / "scitex" / "writer" / "00_shared" / "title.tex",
    ]:
        if candidate.exists():
            candidate.write_text(f"\\title{{{meta['name']}}}")
            return


def _update_authors_tex(path: Path, meta: Dict) -> None:
    """Write author name to authors.tex if found."""
    author_name = meta["owner_full_name"] or meta["owner"]
    if not author_name:
        return

    for candidate in [
        path / "00_shared" / "authors.tex",
        path / "paper" / "manuscript" / "src" / "authors.tex",
        path / "scitex" / "writer" / "00_shared" / "authors.tex",
    ]:
        if candidate.exists():
            candidate.write_text(f"\\author{{{author_name}}}")
            return


# EOF
