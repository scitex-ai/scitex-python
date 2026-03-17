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
        (root / "pyproject.toml").write_text(_render(_PYPROJECT_TOML, ctx))
        (root / "LICENSE").write_text(_LICENSE)
        (root / "README.md").write_text(_render(_README_MD, ctx))

        # Symlink manifest.json at root -> _django/manifest.json
        manifest_content = _render(_MANIFEST_JSON, ctx)
        (django / "manifest.json").write_text(manifest_content)
        _symlink(root / "manifest.json", django / "manifest.json")

        # src/<app_name>/
        (src / "__init__.py").write_text(_render(_PKG_INIT, ctx))

        # _django/
        (django / "__init__.py").write_text(_render(_DJANGO_INIT, ctx))
        (django / "apps.py").write_text(_render(_APPS_PY, ctx))
        (django / "views.py").write_text(_render(_VIEWS_PY, ctx))
        (django / "urls.py").write_text(_render(_URLS_PY, ctx))

        # _django/handlers/
        (handlers / "__init__.py").write_text(_HANDLERS_INIT)
        (handlers / "core.py").write_text(_HANDLERS_CORE)

        # _django/frontend/src/
        (frontend_src / "main.tsx").write_text(_render(_MAIN_TSX, ctx))
        (frontend_src / "App.tsx").write_text(_render(_APP_TSX, ctx))
        (api_dir / "client.ts").write_text(_API_CLIENT_TS)

        # _editor/
        (editor / "__init__.py").write_text(_EDITOR_INIT)
        (editor / "core.py").write_text(_render(_EDITOR_CORE, ctx))

        # _cli/
        (cli / "__init__.py").write_text(_CLI_INIT)
        (cli / "gui.py").write_text(_render(_CLI_GUI, ctx))

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


# ── Template Strings ─────────────────────────────────────────────────
_PYPROJECT_TOML = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{app_name}"
version = "0.1.0"
description = "A SciTeX app"
readme = "README.md"
license = "AGPL-3.0"
requires-python = ">=3.10"
dependencies = [
    "scitex-app>=0.1.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
editor = ["django>=4.2"]
desktop = ["django>=4.2", "pywebview>=4.0"]

[project.scripts]
{app_name} = "{app_name}._cli:main"

[project.entry-points."scitex_modules"]
{app_name} = "{app_name}._django"

[tool.hatch.build.targets.wheel]
packages = ["src/{app_name}"]
exclude = [
    "src/{app_name}/_django/frontend/node_modules",
    "src/{app_name}/_django/frontend/src",
]
"""

_LICENSE = """\
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007

See https://www.gnu.org/licenses/agpl-3.0.html
"""

_README_MD = """\
# {app_label}

A SciTeX app.

## Quick Start

```bash
pip install -e ".[dev,editor]"
```

## Structure

| Directory | Purpose |
|-----------|---------|
| `src/{app_name}/_django/` | Django integration (views, handlers, manifest) |
| `src/{app_name}/_editor/` | Core app logic (no Django dependency) |
| `src/{app_name}/_cli/` | CLI and standalone GUI launcher |
| `src/{app_name}/_django/frontend/` | React frontend source |

## Integration

Add to Django `INSTALLED_APPS`:

```python
INSTALLED_APPS = [..., "{app_name}._django", ...]
```

Add URL pattern:

```python
path("{app_name}/", include("{app_name}._django.urls")),
```
"""

_MANIFEST_JSON = """\
{
  "name": "{app_name}",
  "slug": "{app_name}",
  "label": "{app_label}",
  "version": "0.1.0",
  "icon": "fas fa-puzzle-piece",
  "subtitle": "A SciTeX app",
  "description": "",
  "author": "",
  "license": "AGPL-3.0",
  "standalone": true,
  "frontend_type": "react"
}
"""

_PKG_INIT = '''\
#!/usr/bin/env python3
"""{app_label} -- A SciTeX app."""

__version__ = "0.1.0"
'''

_DJANGO_INIT = '''\
#!/usr/bin/env python3
"""{app_label} Django integration.

Usage (integrated):
    INSTALLED_APPS = [..., "{app_name}._django", ...]
    path("{app_name}/", include("{app_name}._django.urls")),
"""

default_app_config = "{app_name}._django.apps.{app_class}Config"

__all__ = ["default_app_config"]
'''

_APPS_PY = """\
#!/usr/bin/env python3
from scitex_app._django import ScitexAppConfig


class {app_class}Config(ScitexAppConfig):
    name = "{app_name}._django"
    label = "{app_name}"
    verbose_name = "{app_label}"
"""

_VIEWS_PY = '''\
#!/usr/bin/env python3
"""Views for {app_label}."""

from pathlib import Path

from scitex_app._django import scitex_api_dispatch, scitex_editor_page

from .handlers import HANDLERS

editor_page = scitex_editor_page(
    static_dir=Path(__file__).resolve().parent / "static" / "{app_name}",
)

api_dispatch = scitex_api_dispatch(
    handlers=HANDLERS,
    no_editor_endpoints={{"ping", "status"}},
)
'''

_URLS_PY = '''\
#!/usr/bin/env python3
"""URL patterns for {app_label}."""

from scitex_app._django import scitex_urlpatterns

from . import views

app_name = "{app_name}"

urlpatterns = scitex_urlpatterns(views)
'''

_HANDLERS_INIT = '''\
#!/usr/bin/env python3
"""Handler package for API dispatch."""

from .core import handle_ping, handle_status

HANDLERS = {
    "ping": handle_ping,
    "status": handle_status,
}

__all__ = ["HANDLERS"]
'''

_HANDLERS_CORE = '''\
#!/usr/bin/env python3
"""Core handlers: ping, status."""

from django.http import JsonResponse


def handle_ping(request, editor):
    """Health-check endpoint."""
    return JsonResponse({"status": "ok"})


def handle_status(request, editor):
    """App status endpoint."""
    return JsonResponse({
        "status": "ok",
        "editor_loaded": editor is not None,
    })
'''

_MAIN_TSX = """\
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const root = createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""

_APP_TSX = """\
import React from "react";

export default function App() {
  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>{app_label}</h1>
      <p>Your SciTeX app is running.</p>
    </div>
  );
}
"""

_API_CLIENT_TS = """\
const BASE = window.location.pathname.replace(/\\/$/, "");

export async function apiGet(endpoint: string): Promise<any> {
  const resp = await fetch(`${BASE}/${endpoint}`);
  if (!resp.ok) throw new Error(`API ${endpoint}: ${resp.status}`);
  return resp.json();
}

export async function apiPost(endpoint: string, body?: any): Promise<any> {
  const resp = await fetch(`${BASE}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!resp.ok) throw new Error(`API ${endpoint}: ${resp.status}`);
  return resp.json();
}
"""

_EDITOR_INIT = '''\
#!/usr/bin/env python3
"""Core app logic (no Django dependency)."""

from .core import Editor

__all__ = ["Editor"]
'''

_EDITOR_CORE = '''\
#!/usr/bin/env python3
"""Core editor/logic for {app_label}.

Keep all business logic here -- Django handlers should be thin wrappers.
"""


class Editor:
    """Main editor class for {app_label}."""

    def __init__(self):
        self._data = {}

    def ping(self) -> dict:
        return {{"status": "ok"}}
'''

_CLI_INIT = '''\
#!/usr/bin/env python3
"""CLI entry point."""

from .gui import main

__all__ = ["main"]
'''

_CLI_GUI = '''\
#!/usr/bin/env python3
"""Standalone GUI launcher for {app_label}."""

import sys


def main(args=None):
    """Launch {app_label} standalone."""
    if args is None:
        args = sys.argv[1:]

    print("{app_label} standalone launcher")
    print("Run with Django: python -m django runserver")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


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
