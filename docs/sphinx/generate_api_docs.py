#!/usr/bin/env python3
# noqa: STX-S001 — build utility, not a research script
"""Generate API documentation stubs for all SciTeX public modules.

Discovers modules automatically from the package directory.
Generates both modules/*.rst stubs and updates modules/index.rst toctree.

Usage:
    python generate_api_docs.py           # Generate missing stubs only
    python generate_api_docs.py --force   # Regenerate all stubs
"""

import sys
from pathlib import Path

# Template for module RST stub (minimal — Sphinx autodoc fills in the rest)
MODULE_TEMPLATE = """{title}
{underline}

.. automodule:: scitex.{module_name}
   :members:
   :undoc-members:
   :show-inheritance:
"""

# Modules to skip (internal, private, or aliases)
SKIP_MODULES = {
    "_dev",
    "_docs",
    "_mcp_resources",
    "_mcp_tools",
    "__pycache__",
    ".claude",
    "fig",  # alias for plt
    "ml",  # alias for ai
    "dt",  # alias for datetime
    "reproduce",  # alias for repro
    "verify",  # alias for clew
    "fts",  # internal bundle schemas
    "errors",  # deprecated, use logging
    "units",  # internal
}

# Module categories for the index (ordered)
MODULE_CATEGORIES = {
    "Core": [
        "session",
        "io",
        "config",
        "logging",
        "repro",
        "clew",
    ],
    "Science & Analysis": [
        "stats",
        "plt",
        "dsp",
        "diagram",
        "canvas",
    ],
    "Literature & Writing": [
        "scholar",
        "writer",
        "linter",
        "notebook",
    ],
    "Machine Learning": [
        "ai",
        "nn",
        "torch",
        "cv",
        "benchmark",
    ],
    "Data & I/O": [
        "pd",
        "db",
        "dataset",
        "schema",
    ],
    "Infrastructure": [
        "app",
        "cloud",
        "container",
        "tunnel",
        "cli",
        "browser",
        "capture",
        "audio",
        "notify",
        "social",
    ],
    "Utilities": [
        "gen",
        "template",
        "decorators",
        "introspect",
        "str",
        "dict",
        "path",
        "os",
        "sh",
        "git",
        "parallel",
        "linalg",
        "datetime",
        "types",
        "rng",
        "context",
        "resource",
        "utils",
        "etc",
        "web",
        "msword",
        "tex",
        "bridge",
        "compat",
        "module",
        "gists",
        "media",
        "security",
        "ui",
        "usage",
        "dev",
        "audit",
    ],
}


def discover_modules(src_dir: Path) -> list[str]:
    """Discover all public submodule directories."""
    modules = []
    for child in sorted(src_dir.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith("_") or name in SKIP_MODULES:
            continue
        if (child / "__init__.py").exists():
            modules.append(name)
    return modules


def generate_stub(module_name: str, output_path: Path, force: bool = False):
    """Generate a single RST stub file."""
    if output_path.exists() and not force:
        return False

    title = f"{module_name} Module (``stx.{module_name}``)"
    underline = "=" * len(title)

    content = MODULE_TEMPLATE.format(
        title=title,
        underline=underline,
        module_name=module_name,
    )

    output_path.write_text(content)
    return True


def generate_index(modules_dir: Path, all_modules: list[str]):
    """Generate modules/index.rst with all modules in categorized toctrees."""
    # Collect categorized and uncategorized modules
    categorized = set()
    for mods in MODULE_CATEGORIES.values():
        categorized.update(mods)

    uncategorized = [m for m in all_modules if m not in categorized]

    # Build index content
    lines = [
        "Module Overview",
        "===============",
        "",
        "SciTeX is organized into focused modules.",
        "All modules are accessible via ``import scitex as stx`` followed by ``stx.<module>``.",
        "",
    ]

    for category, mods in MODULE_CATEGORIES.items():
        # Only include modules that actually exist
        existing = [m for m in mods if m in all_modules]
        if not existing:
            continue

        lines.append(f".. toctree::")
        lines.append(f"   :maxdepth: 2")
        lines.append(f"   :caption: {category}")
        lines.append(f"")
        for m in existing:
            lines.append(f"   {m}")
        lines.append("")

    if uncategorized:
        lines.append(".. toctree::")
        lines.append("   :maxdepth: 2")
        lines.append("   :caption: Other")
        lines.append("")
        for m in sorted(uncategorized):
            lines.append(f"   {m}")
        lines.append("")

    (modules_dir / "index.rst").write_text("\n".join(lines))


def main():
    force = "--force" in sys.argv

    # Paths
    script_dir = Path(__file__).parent
    src_dir = script_dir.parent.parent / "src" / "scitex"
    modules_dir = script_dir / "modules"
    modules_dir.mkdir(exist_ok=True)

    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}")
        sys.exit(1)

    # Discover all public modules
    all_modules = discover_modules(src_dir)
    print(f"Discovered {len(all_modules)} public modules")

    # Generate stubs
    created = 0
    skipped = 0
    for module_name in all_modules:
        output_path = modules_dir / f"{module_name}.rst"
        if generate_stub(module_name, output_path, force=force):
            created += 1
            print(f"  Created: {module_name}.rst")
        else:
            skipped += 1

    # Generate index
    generate_index(modules_dir, all_modules)
    print(f"  Updated: index.rst")

    print(f"\nDone: {created} created, {skipped} existing (skipped)")
    print(f"Total modules documented: {len(all_modules)}")


if __name__ == "__main__":
    main()
