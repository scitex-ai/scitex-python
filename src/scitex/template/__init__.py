#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/template/__init__.py

"""
Template management for SciTeX projects.
"""

from scitex.git import (
    create_child_git,
    find_parent_git,
    init_git_repo,
    remove_child_git,
)

from ._code._code_templates import (
    CODE_TEMPLATES,
    get_all_templates,
    get_code_template,
    list_code_templates,
)
from ._project._clone_template import clone_template
from ._project.clone_pip_project import TEMPLATE_REPO_URL as PIP_PROJECT_URL
from ._project.clone_pip_project import clone_pip_project
from ._project.clone_research import TEMPLATE_REPO_URL as RESEARCH_URL
from ._project.clone_research import clone_research
from ._project.clone_research_minimal import clone_research_minimal
from ._project.clone_singularity import TEMPLATE_REPO_URL as SINGULARITY_URL
from ._project.clone_singularity import clone_singularity
from ._project.clone_writer_directory import TEMPLATE_REPO_URL as PAPER_DIRECTORY_URL
from ._project.clone_writer_directory import clone_writer_directory
from ._project._scholar_writer_integration import (
    setup_scholar_writer_integration,
    ensure_integration,
)


def get_available_templates_info():
    """
    Get information about all available SciTeX project templates.

    Returns
    -------
    list[dict]
        List of template information dictionaries, each containing:
        - id: Template identifier (used in code)
        - name: Human-readable template name
        - description: Template description
        - github_url: GitHub repository URL
        - use_case: When to use this template

    Example
    -------
    >>> from scitex.template import get_available_templates_info
    >>> templates = get_available_templates_info()
    >>> for template in templates:
    ...     print(f"{template['name']}: {template['description']}")
    """
    return [
        {
            "id": "research_minimal",
            "name": "Research Minimal",
            "description": "Minimal SciTeX structure with writer, scholar, visualizer, and console",
            "github_url": RESEARCH_URL,
            "branch": "minimal",
            "use_case": "Focused research workflow with essential SciTeX modules only",
            "features": [
                "scitex/writer/ - LaTeX manuscript writing",
                "scitex/scholar/ - Bibliography management",
                "scitex/visualizer/ - Figure creation",
                "scitex/console/ - Code execution",
                "scitex/management/ - Project management",
            ],
        },
        {
            "id": "research",
            "name": "Research Project (Full)",
            "description": "Full scientific workflow structure for research projects",
            "github_url": RESEARCH_URL,
            "use_case": "Scientific research with data analysis, experiments, and paper writing",
            "features": [
                "scripts/ - Analysis and preprocessing scripts",
                "data/ - Raw and processed data management",
                "docs/ - Manuscripts, notes, and references",
                "results/ - Analysis outputs and reports",
                "config/ - Project configuration files",
            ],
        },
        {
            "id": "pip_project",
            "name": "Python Package",
            "description": "Pip-installable Python package template",
            "github_url": PIP_PROJECT_URL,
            "use_case": "Creating distributable Python packages for PyPI",
            "features": [
                "src/ - Package source code",
                "tests/ - Unit and integration tests",
                "docs/ - Sphinx documentation",
                "setup.py - Package configuration",
                "CI/CD - GitHub Actions workflows",
            ],
        },
        {
            "id": "singularity",
            "name": "Singularity Container",
            "description": "Container-based project with Singularity",
            "github_url": SINGULARITY_URL,
            "use_case": "Reproducible computational environments with containers",
            "features": [
                "Singularity definition files",
                "Container build scripts",
                "Environment specifications",
                "Deployment configuration",
            ],
        },
        {
            "id": "paper_directory",
            "name": "Paper Directory",
            "description": "Academic paper writing template with scitex-writer",
            "github_url": PAPER_DIRECTORY_URL,
            "use_case": "Writing academic papers with LaTeX and BibTeX management",
            "features": [
                "LaTeX document structure",
                "BibTeX bibliography management",
                "Figure and table organization",
                "Manuscript tracking",
            ],
        },
    ]


__all__ = [
    "clone_template",
    "clone_research",
    "clone_research_minimal",
    "clone_pip_project",
    "clone_singularity",
    "clone_writer_directory",
    "get_available_templates_info",
    "get_code_template",
    "list_code_templates",
    "get_all_templates",
    "CODE_TEMPLATES",
    "init_git_repo",
    "find_parent_git",
    "create_child_git",
    "remove_child_git",
    # Scholar-Writer integration
    "setup_scholar_writer_integration",
    "ensure_integration",
]

# EOF
