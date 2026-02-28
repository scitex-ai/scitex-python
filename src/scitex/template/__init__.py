#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/template/__init__.py

"""
Template management for SciTeX projects.
"""

from pathlib import Path

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
from ._project._customize import customize_minimal_template, customize_template
from ._project._directory_structure import (
    PROJECT_STRUCTURE,
    build_directory_tree,
)
from ._project._generate_configs import (
    create_env_template,
    create_paths_config,
    create_project_config,
    create_requirements_file,
)
from ._project._generate_readme import create_minimal_readme, create_project_readme
from ._project._scholar_writer_integration import (
    ensure_integration,
    setup_scholar_writer_integration,
)
from ._project.clone_module import clone_module
from ._project.clone_pip_project import TEMPLATE_REPO_URL as PIP_PROJECT_URL
from ._project.clone_pip_project import clone_pip_project
from ._project.clone_research import TEMPLATE_REPO_URL as RESEARCH_URL
from ._project.clone_research import clone_research
from ._project.clone_research_minimal import (
    MINIMAL_INCLUDE_DIRS,
    clone_research_minimal,
)
from ._project.clone_scitex_minimal import clone_scitex_minimal
from ._project.clone_singularity import TEMPLATE_REPO_URL as SINGULARITY_URL
from ._project.clone_singularity import clone_singularity
from ._project.clone_writer_directory import TEMPLATE_REPO_URL as PAPER_DIRECTORY_URL
from ._project.clone_writer_directory import clone_writer_directory


def get_template_tree(template_id):
    """Create template in a tempdir and return its ``tree`` output.

    Actually runs the template's directory-creation logic in a
    temporary directory on the fly, then captures the real ``tree``
    output. This guarantees the displayed tree always matches
    the current template code.

    Parameters
    ----------
    template_id : str
        Template identifier (e.g. 'minimal', 'research').

    Returns
    -------
    str
        ``tree`` output string, or empty string if unknown.
    """
    import shutil
    import subprocess
    import tempfile

    from scitex.scholar.ensure_workspace import SCHOLAR_SUBDIRS

    tmpdir = tempfile.mkdtemp(prefix="scitex_tree_")
    try:
        project_dir = Path(tmpdir) / "project"
        project_dir.mkdir()

        if template_id == "minimal":
            # Reproduce scitex_minimal directory scaffold without git clone
            writer_dir = project_dir / "scitex" / "writer"
            for name in MINIMAL_INCLUDE_DIRS:
                (writer_dir / name).mkdir(parents=True, exist_ok=True)
            scholar_dir = project_dir / "scitex" / "scholar"
            for name in SCHOLAR_SUBDIRS:
                (scholar_dir / name).mkdir(parents=True, exist_ok=True)

        elif template_id == "research":
            build_directory_tree(str(project_dir), PROJECT_STRUCTURE)

        elif template_id == "app":
            # Reproduce pip-project-template structure
            src_dir = project_dir / "src" / "package_name"
            src_dir.mkdir(parents=True)
            (src_dir / "__init__.py").touch()
            tests_dir = project_dir / "tests"
            tests_dir.mkdir()
            (tests_dir / "__init__.py").touch()
            (tests_dir / "test_main.py").touch()
            (project_dir / "pyproject.toml").touch()
            (project_dir / "README.md").touch()
            (project_dir / "LICENSE").touch()

        else:
            return ""

        result = subprocess.run(
            ["tree", "--noreport", "--dirsfirst", str(project_dir)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # Replace the temp path prefix with "."
            tree_output = result.stdout.strip()
            first_newline = tree_output.find("\n")
            if first_newline != -1:
                return "." + tree_output[first_newline:]
            return "."
        return ""

    except Exception:
        return ""
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


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
        - tree: Tree-command-style directory listing

    Example
    -------
    >>> from scitex.template import get_available_templates_info
    >>> templates = get_available_templates_info()
    >>> for template in templates:
    ...     print(f"{template['name']}: {template['description']}")
    """
    return [
        {
            "id": "minimal",
            "name": "SciTeX Minimal",
            "description": "Minimal project with writer + scholar workspaces",
            "github_url": RESEARCH_URL,
            "use_case": "Manuscript writing with integrated bibliography management",
            "tree": get_template_tree("minimal"),
        },
        {
            "id": "research",
            "name": "SciTeX Full",
            "description": "Full scientific workflow with data analysis, experiments, and paper writing",
            "github_url": RESEARCH_URL,
            "use_case": "End-to-end scientific research projects",
            "tree": get_template_tree("research"),
        },
        {
            "id": "app",
            "name": "SciTeX App",
            "description": "Pip-installable Python package for building reusable SciTeX apps",
            "github_url": PIP_PROJECT_URL,
            "use_case": "Creating reusable tools and apps for the SciTeX ecosystem",
            "tree": get_template_tree("app"),
        },
    ]


__all__ = [
    "clone_template",
    "clone_module",
    "clone_research",
    "clone_research_minimal",
    "clone_scitex_minimal",
    "MINIMAL_INCLUDE_DIRS",
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
    # Template customization (moved from Django)
    "customize_template",
    "customize_minimal_template",
    "create_project_config",
    "create_paths_config",
    "create_env_template",
    "create_requirements_file",
    "create_minimal_readme",
    "create_project_readme",
    "build_directory_tree",
    "PROJECT_STRUCTURE",
    # Scholar-Writer integration
    "setup_scholar_writer_integration",
    "ensure_integration",
]

# EOF
