#!/usr/bin/env python3
# Timestamp: 2026-02-23
# File: src/scitex/template/_project/clone_module.py

"""Create a scitex module project template.

Clones from the scitex-template-cloud-module GitHub template repository.
Falls back to inline scaffold if the repo is not accessible.

Structure:
    <project_dir>/
    ├── module.py          # @stx.module decorated function
    ├── manifest.yaml      # Module metadata (label, icon, category)
    ├── requirements.txt   # Python dependencies
    ├── README.md          # Usage instructions
    └── tests/
        └── test_module.py # Basic smoke test
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from scitex.logging import getLogger

logger = getLogger(__name__)

TEMPLATE_REPO_URL = "https://github.com/ywatanabe1989/scitex-template-cloud-module.git"


def clone_module(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs,
) -> bool:
    """Create a module project template.

    Tries to clone from the GitHub template repo first.
    Falls back to inline scaffold if clone fails.

    Parameters
    ----------
    project_dir : str
        Path to project directory (will be created).
    git_strategy : str, optional
        Git initialization strategy.
    branch : str, optional
        Specific branch of the template repository to clone.
    tag : str, optional
        Specific tag/release of the template repository to clone.
    **kwargs
        Additional keyword arguments forwarded to clone_project.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    # Try git clone from template repo first
    try:
        from ._clone_project import clone_project

        return clone_project(
            project_dir,
            TEMPLATE_REPO_URL,
            "scitex-template-cloud-module",
            git_strategy,
            branch,
            tag,
        )
    except Exception as e:
        logger.warning(f"Git clone failed ({e}), using inline scaffold")

    # Fallback: generate files inline
    return _scaffold_inline(project_dir, git_strategy)


def _scaffold_inline(project_dir: str, git_strategy: Optional[str]) -> bool:
    """Generate module template files inline (fallback)."""
    try:
        project_path = Path(project_dir)
        project_path.mkdir(parents=True, exist_ok=True)

        (project_path / "module.py").write_text(_MODULE_PY)
        (project_path / "manifest.yaml").write_text(_MANIFEST_YAML)
        (project_path / "requirements.txt").write_text(_REQUIREMENTS_TXT)
        (project_path / "README.md").write_text(_README_MD)

        tests_dir = project_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").write_text("")
        (tests_dir / "test_module.py").write_text(_TEST_MODULE_PY)

        if git_strategy:
            from scitex.git import init_git_repo

            init_git_repo(str(project_path))

        logger.info(f"Created module template at {project_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to create module template: {e}")
        return False


# ---------------------------------------------------------------------------
# Inline template content (used when GitHub repo is not accessible)
# ---------------------------------------------------------------------------
_MODULE_PY = '''\
#!/usr/bin/env python3
"""Example SciTeX module — replace with your own logic."""

import scitex as stx


@stx.module(
    label="My Module",
    icon="fa-puzzle-piece",
    category="utility",
    description="A custom SciTeX module.",
)
def main(project=stx.module.INJECTED, plt=stx.module.INJECTED):
    """Main entry point for the module."""
    # --- Your module logic here ---

    stx.module.output("Hello from My Module!", title="Greeting")

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    stx.module.output(fig, title="Example Plot")

    return 0
'''

_MANIFEST_YAML = """\
# SciTeX Module Manifest
# See: https://scitex.ai/docs/modules

name: my-module
label: My Module
icon: fa-puzzle-piece
category: utility
description: A custom SciTeX module.
version: 0.1.0
min_scitex_version: "0.8.0"

dependencies:
  - numpy
  - matplotlib
"""

_REQUIREMENTS_TXT = """\
numpy
matplotlib
"""

_README_MD = """\
# My Module

A custom SciTeX workspace module.

## Quick Start

1. Write your module logic in `module.py`
2. Update `manifest.yaml` with your module's metadata
3. Import into SciTeX: **Module Maker** > **Import from GitHub**

## Structure

| File | Purpose |
|------|---------|
| `module.py` | Main module code with `@stx.module` decorator |
| `manifest.yaml` | Module metadata (name, icon, category, version) |
| `requirements.txt` | Python package dependencies |
| `tests/test_module.py` | Basic smoke tests |

## Import into SciTeX

1. Push this repo to GitHub
2. In SciTeX, go to **Module Maker** tab
3. Click **Import from GitHub**
4. Paste your repository URL

## License

MIT
"""

_TEST_MODULE_PY = '''\
#!/usr/bin/env python3
"""Basic tests for the module."""


def test_module_has_decorator():
    """module.py should have @stx.module decorator."""
    from pathlib import Path

    source = (Path(__file__).parent.parent / "module.py").read_text()
    assert "@stx.module" in source


def test_manifest_exists():
    """manifest.yaml should exist."""
    from pathlib import Path

    manifest = Path(__file__).parent.parent / "manifest.yaml"
    assert manifest.exists()
'''


def main(args: list = None) -> None:
    """Command-line interface for clone_module."""
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m scitex clone_module <project-dir>")
        print("")
        print("Creates a SciTeX module template project.")
        sys.exit(1)

    success = clone_module(args[0])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# EOF
