#!/usr/bin/env python3
# Timestamp: 2026-03-17
# File: src/scitex/template/_project/_app_templates.py

"""Inline template strings for the SciTeX app scaffold.

Split out from clone_app.py to keep that file under 300 lines.
"""

PYPROJECT_TOML = """\
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

LICENSE = """\
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007

See https://www.gnu.org/licenses/agpl-3.0.html
"""

README_MD = """\
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

MANIFEST_JSON = """\
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
  "frontend_type": "react",
  "bridge": {{
    "entry": "src/bridge/bridge-init.ts",
    "source_root": "src"
  }}
}
"""

PKG_INIT = '''\
#!/usr/bin/env python3
"""{app_label} -- A SciTeX app."""

__version__ = "0.1.0"
'''

DJANGO_INIT = '''\
#!/usr/bin/env python3
"""{app_label} Django integration.

Usage (integrated):
    INSTALLED_APPS = [..., "{app_name}._django", ...]
    path("{app_name}/", include("{app_name}._django.urls")),
"""

default_app_config = "{app_name}._django.apps.{app_class}Config"

__all__ = ["default_app_config"]
'''

APPS_PY = """\
#!/usr/bin/env python3
from scitex_app._django import ScitexAppConfig


class {app_class}Config(ScitexAppConfig):
    name = "{app_name}._django"
    label = "{app_name}"
    verbose_name = "{app_label}"
"""

VIEWS_PY = '''\
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

URLS_PY = '''\
#!/usr/bin/env python3
"""URL patterns for {app_label}."""

from scitex_app._django import scitex_urlpatterns

from . import views

app_name = "{app_name}"

urlpatterns = scitex_urlpatterns(views)
'''

HANDLERS_INIT = '''\
#!/usr/bin/env python3
"""Handler package for API dispatch."""

from .core import handle_ping, handle_status

HANDLERS = {
    "ping": handle_ping,
    "status": handle_status,
}

__all__ = ["HANDLERS"]
'''

HANDLERS_CORE = '''\
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

MAIN_TSX = """\
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

APP_TSX = """\
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

API_CLIENT_TS = """\
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

EDITOR_INIT = '''\
#!/usr/bin/env python3
"""Core app logic (no Django dependency)."""

from .core import Editor

__all__ = ["Editor"]
'''

EDITOR_CORE = '''\
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

CLI_INIT = '''\
#!/usr/bin/env python3
"""CLI entry point."""

from .gui import main

__all__ = ["main"]
'''

CLI_GUI = '''\
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

BRIDGE_INIT_TS = """\
/**
 * {app_label} bridge init — entry point for mounting into scitex-cloud workspace.
 */
import "scitex-ui/css/app.css";

import {{ mountApp, unmountApp }} from "./MountPoint";

const MOUNT_ID = "app-mount";

function init(): void {{
  const mount = document.getElementById(MOUNT_ID);
  if (!mount) return;

  const isEmbedded = mount.dataset.embedded === "true";
  const workingDir = mount.dataset.workingDir;

  if (isEmbedded) {{
    mountApp({{
      container: mount,
      workingDir,
      darkMode: document.body.classList.contains("dark-theme"),
    }});
  }}
}}

if (document.readyState === "loading") {{
  document.addEventListener("DOMContentLoaded", init);
}} else {{
  init();
}}
"""

BRIDGE_MOUNT_POINT_TS = """\
/**
 * {app_label} mount point — React root + fetch override.
 */
import React from "react";
import {{
  installFetchOverride,
  mountReactApp,
  unmountReactApp,
}} from "scitex-ui/react/app/bridge";
import type {{ BridgeConfig, BridgeMountOptions }} from "scitex-ui/react/app/bridge";
import App from "../App";

const BRIDGE_CONFIG: BridgeConfig = {{
  slug: "{app_name}",
  mountId: "app-mount",
  apiPaths: ["/ping", "/status"],
  fileExtensions: [],
}};

export function mountApp(options: BridgeMountOptions): void {{
  installFetchOverride(BRIDGE_CONFIG);
  mountReactApp(
    options.container,
    React.createElement(App, {{
      apiBaseUrl: `/apps/${{BRIDGE_CONFIG.slug}}/${{BRIDGE_CONFIG.slug}}`,
      workingDir: options.workingDir,
      darkMode: options.darkMode,
    }}),
  );
}}

export function unmountApp(): void {{
  unmountReactApp();
}}
"""

BRIDGE_EVENT_BUS_TS = """\
/**
 * {app_label} event bus — typed wrapper around generic bridge events.
 */
import {{ emitBridgeEvent, onBridgeEvent }} from "scitex-ui/react/app/bridge";

const SLUG = "{app_name}";

export function emitEvent(name: string, detail: unknown): void {{
  emitBridgeEvent(SLUG, name, detail);
}}

export function onEvent(
  name: string,
  handler: (detail: unknown) => void,
): () => void {{
  return onBridgeEvent(SLUG, name, handler);
}}
"""

BRIDGE_INDEX_TS = """\
/** {app_label} bridge — barrel export. */
export {{ mountApp, unmountApp }} from "./MountPoint";
export {{ emitEvent, onEvent }} from "./EventBus";
"""

# EOF
