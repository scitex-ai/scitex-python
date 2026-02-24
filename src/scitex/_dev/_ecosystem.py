#!/usr/bin/env python3
# Timestamp: 2026-02-03
# File: scitex/_dev/_ecosystem.py

"""SciTeX ecosystem package registry."""

from pathlib import Path
from typing import Dict, List, Optional, TypedDict


class PackageInfo(TypedDict, total=False):
    """Package information structure."""

    local_path: str
    pypi_name: str
    github_repo: str
    import_name: str


# Ordered dict - order matters for display
ECOSYSTEM: Dict[str, PackageInfo] = {
    "scitex": {
        "local_path": "~/proj/scitex-python",
        "pypi_name": "scitex",
        "github_repo": "ywatanabe1989/scitex-python",
        "import_name": "scitex",
    },
    "scitex-cloud": {
        "local_path": "~/proj/scitex-cloud",
        "pypi_name": "scitex-cloud",
        "github_repo": "ywatanabe1989/scitex-cloud",
        "import_name": "scitex_cloud",
    },
    "figrecipe": {
        "local_path": "~/proj/figrecipe",
        "pypi_name": "figrecipe",
        "github_repo": "ywatanabe1989/figrecipe",
        "import_name": "figrecipe",
    },
    "scitex-plt": {
        "local_path": "~/proj/scitex-plt",
        "pypi_name": "scitex-plt",
        "github_repo": "ywatanabe1989/scitex-plt",
        "import_name": "scitex_plt",
    },
    "openalex-local": {
        "local_path": "~/proj/openalex-local",
        "pypi_name": "openalex-local",
        "github_repo": "ywatanabe1989/openalex-local",
        "import_name": "openalex_local",
    },
    "crossref-local": {
        "local_path": "~/proj/crossref-local",
        "pypi_name": "crossref-local",
        "github_repo": "ywatanabe1989/crossref-local",
        "import_name": "crossref_local",
    },
    "scitex-writer": {
        "local_path": "~/proj/scitex-writer",
        "pypi_name": "scitex-writer",
        "github_repo": "ywatanabe1989/scitex-writer",
        "import_name": "scitex_writer",
    },
    "scitex-linter": {
        "local_path": "~/proj/scitex-linter",
        "pypi_name": "scitex-linter",
        "github_repo": "ywatanabe1989/scitex-linter",
        "import_name": "scitex_linter",
    },
    "scitex-dataset": {
        "local_path": "~/proj/scitex-dataset",
        "pypi_name": "scitex-dataset",
        "github_repo": "ywatanabe1989/scitex-dataset",
        "import_name": "scitex_dataset",
    },
    "socialia": {
        "local_path": "~/proj/socialia",
        "pypi_name": "socialia",
        "github_repo": "ywatanabe1989/socialia",
        "import_name": "socialia",
    },
    "automated-research-demo": {
        "local_path": "~/proj/automated-research-demo",
        "pypi_name": "automated-research-demo",
        "github_repo": "ywatanabe1989/automated-research-demo",
        "import_name": "automated_research_demo",
    },
    "scitex-research-template": {
        "local_path": "~/proj/scitex-research-template",
        "pypi_name": "scitex-research-template",
        "github_repo": "ywatanabe1989/scitex-research-template",
        "import_name": "scitex_research_template",
    },
    "pip-project-template": {
        "local_path": "~/proj/pip-project-template",
        "pypi_name": "pip-project-template",
        "github_repo": "ywatanabe1989/pip-project-template",
        "import_name": "pip_project_template",
    },
    "scitex-container": {
        "local_path": "~/proj/scitex-container",
        "pypi_name": "scitex-container",
        "github_repo": "ywatanabe1989/scitex-container",
        "import_name": "scitex_container",
    },
    "singularity-template": {
        "local_path": "~/proj/singularity-template",
        "pypi_name": "singularity-template",
        "github_repo": "ywatanabe1989/singularity-template",
        "import_name": "singularity_template",
    },
}


def get_local_path(package: str) -> Optional[Path]:
    """Get expanded local path for a package."""
    if package not in ECOSYSTEM:
        return None
    return Path(ECOSYSTEM[package]["local_path"]).expanduser()


def get_all_packages() -> List[str]:
    """Get list of all ecosystem package names."""
    return list(ECOSYSTEM.keys())


# EOF
