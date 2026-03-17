#!/usr/bin/env python3
# Timestamp: 2026-03-17
# File: src/scitex/template/_project/clone_app.py

"""Create a SciTeX app project template.

Generates a complete app skeleton with Django integration, React frontend
scaffold, core editor logic, and CLI launcher -- matching the scitex-app
protocol contract (ScitexAppConfig, scitex_api_dispatch, scitex_urlpatterns).

Structure:
    <project_dir>/
    ├── src/<app_name>/
    │   ├── __init__.py
    │   ├── _django/
    │   │   ├── __init__.py
    │   │   ├── apps.py
    │   │   ├── views.py
    │   │   ├── urls.py
    │   │   ├── handlers/
    │   │   │   ├── __init__.py
    │   │   │   └── core.py
    │   │   ├── manifest.json
    │   │   └── frontend/
    │   │       └── src/
    │   │           ├── App.tsx
    │   │           ├── main.tsx
    │   │           └── api/
    │   │               └── client.ts
    │   ├── _editor/
    │   │   ├── __init__.py
    │   │   └── core.py
    │   └── _cli/
    │       ├── __init__.py
    │       └── gui.py
    ├── pyproject.toml
    ├── manifest.json  (symlink)
    ├── LICENSE
    └── README.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from scitex.logging import getLogger

from . import _app_templates as T

logger = getLogger(__name__)


def clone_app(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs,
) -> bool:
    """Create a SciTeX app project from an inline template.

    Parameters
    ----------
    project_dir : str
        Path to project directory (will be created).
        The directory basename is used as the app name.
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', None).
    branch : str, optional
        Unused (kept for API compatibility with clone_template).
    tag : str, optional
        Unused (kept for API compatibility with clone_template).
    **kwargs
        Additional keyword arguments (ignored).

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    return _scaffold_inline(project_dir, git_strategy)


def _scaffold_inline(project_dir: str, git_strategy: Optional[str]) -> bool:
    """Generate all template files inline."""
    try:
        root = Path(project_dir)
        app_name = root.name.replace("-", "_")
        app_class = _to_class_name(app_name)
        app_label = _to_human_label(app_name)

        ctx = {"app_name": app_name, "app_class": app_class, "app_label": app_label}

        src = root / "src" / app_name
        django = src / "_django"
        handlers = django / "handlers"
        frontend_src = django / "frontend" / "src"
        api_dir = frontend_src / "api"
        editor = src / "_editor"
        cli = src / "_cli"

        for d in [handlers, api_dir, editor, cli]:
            d.mkdir(parents=True, exist_ok=True)

        # Top-level files
        (root / "pyproject.toml").write_text(_render(T.PYPROJECT_TOML, ctx))
        (root / "LICENSE").write_text(T.LICENSE)
        (root / "README.md").write_text(_render(T.README_MD, ctx))

        # Symlink manifest.json at root -> _django/manifest.json
        (django / "manifest.json").write_text(_render(T.MANIFEST_JSON, ctx))
        _symlink(root / "manifest.json", django / "manifest.json")

        # src/<app_name>/
        (src / "__init__.py").write_text(_render(T.PKG_INIT, ctx))

        # _django/
        (django / "__init__.py").write_text(_render(T.DJANGO_INIT, ctx))
        (django / "apps.py").write_text(_render(T.APPS_PY, ctx))
        (django / "views.py").write_text(_render(T.VIEWS_PY, ctx))
        (django / "urls.py").write_text(_render(T.URLS_PY, ctx))

        # _django/handlers/
        (handlers / "__init__.py").write_text(T.HANDLERS_INIT)
        (handlers / "core.py").write_text(T.HANDLERS_CORE)

        # _django/frontend/src/
        (frontend_src / "main.tsx").write_text(_render(T.MAIN_TSX, ctx))
        (frontend_src / "App.tsx").write_text(_render(T.APP_TSX, ctx))
        (api_dir / "client.ts").write_text(T.API_CLIENT_TS)

        # Bridge files
        bridge_dir = frontend_src / "bridge"
        bridge_dir.mkdir(parents=True, exist_ok=True)
        (bridge_dir / "bridge-init.ts").write_text(_render(T.BRIDGE_INIT_TS, ctx))
        (bridge_dir / "MountPoint.ts").write_text(_render(T.BRIDGE_MOUNT_POINT_TS, ctx))
        (bridge_dir / "EventBus.ts").write_text(_render(T.BRIDGE_EVENT_BUS_TS, ctx))
        (bridge_dir / "index.ts").write_text(_render(T.BRIDGE_INDEX_TS, ctx))

        # _editor/
        (editor / "__init__.py").write_text(T.EDITOR_INIT)
        (editor / "core.py").write_text(_render(T.EDITOR_CORE, ctx))

        # _cli/
        (cli / "__init__.py").write_text(T.CLI_INIT)
        (cli / "gui.py").write_text(_render(T.CLI_GUI, ctx))

        if git_strategy:
            from scitex.git import init_git_repo

            init_git_repo(str(root))

        logger.info("Created SciTeX app template at %s", root)
        return True

    except Exception as e:
        logger.error("Failed to create app template: %s", e)
        return False


# ── Helpers ──────────────────────────────────────────────────────────
def _render(template: str, ctx: dict) -> str:
    return (
        template.replace("{app_name}", ctx["app_name"])
        .replace("{app_class}", ctx["app_class"])
        .replace("{app_label}", ctx["app_label"])
    )


def _to_class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def _to_human_label(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("_"))


def _symlink(link: Path, target: Path) -> None:
    rel = os.path.relpath(target, link.parent)
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(rel)


def main(args: list = None) -> None:
    """Command-line interface for clone_app."""
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m scitex clone_app <project-dir>")
        print("")
        print("Creates a SciTeX app template project.")
        sys.exit(1)

    success = clone_app(args[0])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# EOF
