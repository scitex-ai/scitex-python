#!/usr/bin/env python3
# Timestamp: 2026-02-08
# File: src/scitex/template/_project/_clone_template.py

"""
Unified template cloning dispatcher.

Single entry point for all template cloning operations.
Django, MCP, and CLI all delegate to this function.
"""

from __future__ import annotations

from typing import Any, Optional

from .clone_app import clone_app
from .clone_module import clone_module
from .clone_pip_project import clone_pip_project
from .clone_research import clone_research
from .clone_research_minimal import clone_research_minimal
from .clone_scitex_minimal import clone_scitex_minimal
from .clone_singularity import clone_singularity
from .clone_writer_directory import clone_writer_directory

TEMPLATES = {
    "research": clone_research,
    "research_minimal": clone_research_minimal,
    "scitex_minimal": clone_scitex_minimal,
    "pip_project": clone_pip_project,
    "singularity": clone_singularity,
    "paper_directory": clone_writer_directory,
    "module": clone_module,
    "scitex_app": clone_app,
}

ALIASES = {
    "minimal": "scitex_minimal",
    "pip-project": "pip_project",
    "paper": "paper_directory",
    "stx-module": "module",
    "app": "scitex_app",
}


def clone_template(
    template_id: str,
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs: Any,
) -> bool:
    """
    Clone a project template by ID.

    Unified dispatcher that resolves template IDs (including aliases)
    and delegates to the appropriate clone function.

    Parameters
    ----------
    template_id : str
        Template identifier. Canonical IDs: research, research_minimal,
        scitex_minimal, pip_project, singularity, paper_directory,
        module, scitex_app.
        Aliases: minimal (->scitex_minimal), pip-project, paper,
        stx-module, app (->scitex_app).
    project_dir : str
        Path to project directory (will be created).
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', 'origin', None).
    branch : str, optional
        Specific branch to clone.
    tag : str, optional
        Specific tag to clone.
    **kwargs
        Additional keyword arguments forwarded to the clone function
        (e.g. ``include_dirs`` for research_minimal).

    Returns
    -------
    bool
        True if successful, False otherwise.

    Raises
    ------
    ValueError
        If template_id is unknown.
    """
    resolved_id = ALIASES.get(template_id, template_id)
    func = TEMPLATES.get(resolved_id)
    if not func:
        raise ValueError(
            f"Unknown template: {template_id}. Available: {list(TEMPLATES)}"
        )
    return func(
        project_dir=project_dir,
        git_strategy=git_strategy,
        branch=branch,
        tag=tag,
        **kwargs,
    )


def get_template_ids():
    """Return list of all canonical template IDs."""
    return list(TEMPLATES.keys())


def get_all_template_ids():
    """Return list of all template IDs including aliases."""
    return list(TEMPLATES.keys()) + list(ALIASES.keys())


__all__ = [
    "clone_template",
    "TEMPLATES",
    "ALIASES",
    "get_template_ids",
    "get_all_template_ids",
]

# EOF
