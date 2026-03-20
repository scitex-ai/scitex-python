#!/usr/bin/env python3
"""Detect dependencies for each module by analyzing imports.

Usage:
    ./scripts/maintenance/detect-module-deps.py [module]
    ./scripts/maintenance/detect-module-deps.py io        # Check specific module
    ./scripts/maintenance/detect-module-deps.py --all     # Check all modules
    ./scripts/maintenance/detect-module-deps.py --all --missing-only
"""

import ast
import sys
from pathlib import Path

from stdlib_list import stdlib_list

# Get stdlib for current Python version
STDLIB = set(stdlib_list())

# Map import names to PyPI package names (common mismatches)
IMPORT_TO_PYPI = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "serial": "pyserial",
    "usb": "pyusb",
    "gi": "PyGObject",
    "wx": "wxPython",
    "skimage": "scikit-image",
    "Bio": "biopython",
    "OpenGL": "PyOpenGL",
    "git": "GitPython",
    "ruamel": "ruamel.yaml",
    "fitz": "PyMuPDF",
    "docx": "python-docx",
}

# Internal packages/modules to ignore
INTERNAL = {"scitex", "mngs"}

# Base dependencies (in core install, always available)
# NOTE: Keep this minimal - modules should declare their own deps for isolated testing
BASE_DEPS = {
    "numpy",
    "pandas",
    "pytest",
    "hypothesis",
}

# Known PyPI packages (to filter out internal function imports)
KNOWN_PYPI = {
    "PIL",
    "scipy",
    "tqdm",
    "psutil",
    "cv2",
    "sklearn",
    "yaml",
    "bs4",
    "git",
    "ruamel",
    "fitz",
    "docx",
    "h5py",
    "openpyxl",
    "xlrd",
    "lxml",
    "xarray",
    "zarr",
    "numcodecs",
    "piexif",
    "pypdf",
    "qrcode",
    "pdfplumber",
    "html2text",
    "markdown",
    "joblib",
    "plotly",
    "pymatreader",
    "natsort",
    "matplotlib",
    "mne",
    "optuna",
    "torch",
    "tensorflow",
    "jax",
    "seaborn",
    "flask",
    "dearpygui",
    "PyQt6",
    "PyQt5",
    "tkinter",
    "requests",
    "aiohttp",
    "selenium",
    "playwright",
    "pyautogui",
    "pynput",
    "soundfile",
    "sounddevice",
    "pyaudio",
    "pydub",
    "librosa",
    "catboost",
    "xgboost",
    "lightgbm",
    "pyarrow",
    "sympy",
    "networkx",
}


def extract_imports(filepath: Path) -> set[str]:
    """Extract top-level import names from a Python file."""
    try:
        tree = ast.parse(filepath.read_text())
    except SyntaxError:
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:  # Only absolute imports
                imports.add(node.module.split(".")[0])
    return imports


def get_module_imports(module: str, project_root: Path) -> dict[str, set[str]]:
    """Get imports from source and test files for a module."""
    src_dir = project_root / "src" / "scitex" / module
    test_dir = project_root / "tests" / "scitex" / module

    result = {"source": set(), "tests": set()}

    for d, key in [(src_dir, "source"), (test_dir, "tests")]:
        if d.exists():
            for py_file in d.rglob("*.py"):
                result[key] |= extract_imports(py_file)

    return result


def filter_external(imports: set[str]) -> set[str]:
    """Filter to only external (non-stdlib, non-internal) known packages."""
    external = set()
    for imp in imports:
        if imp in STDLIB or imp in INTERNAL:
            continue
        if imp.startswith("_"):
            continue
        if imp in BASE_DEPS:
            continue
        # Only include if it's a known PyPI package
        if imp in KNOWN_PYPI or imp in IMPORT_TO_PYPI:
            external.add(imp)
    return external


def to_pypi_name(import_name: str) -> str:
    """Convert import name to likely PyPI package name."""
    return IMPORT_TO_PYPI.get(import_name, import_name)


def load_pyproject_extras(project_root: Path) -> dict[str, set[str]]:
    """Load current extras from pyproject.toml."""
    import tomllib

    pyproject = project_root / "pyproject.toml"
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)

    extras = {}
    for name, deps in data.get("project", {}).get("optional-dependencies", {}).items():
        # Normalize package names for comparison
        extras[name] = {
            d.split("[")[0].split(">")[0].split("<")[0].split("=")[0].lower()
            for d in deps
        }
    return extras


def analyze_module(
    module: str, project_root: Path, current_extras: dict[str, set[str]]
) -> dict:
    """Analyze a single module's dependencies."""
    imports = get_module_imports(module, project_root)

    src_external = filter_external(imports["source"])
    test_external = filter_external(imports["tests"])
    all_external = src_external | test_external

    # Convert to PyPI names
    needed_pypi = {to_pypi_name(imp) for imp in all_external}

    # Get current deps for this module
    current_deps = current_extras.get(module, set())

    # Find missing (normalize for comparison)
    needed_lower = {p.lower() for p in needed_pypi}
    missing = needed_lower - current_deps

    return {
        "source_imports": sorted(src_external),
        "test_imports": sorted(test_external),
        "needed_pypi": sorted(needed_pypi),
        "current_deps": sorted(current_deps),
        "missing": sorted(missing),
        "extra_configured": sorted(current_deps - needed_lower),
    }


def main():
    project_root = Path(__file__).parent.parent.parent
    missing_only = "--missing-only" in sys.argv

    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    current_extras = load_pyproject_extras(project_root)

    if "--all" in sys.argv or (args and args[0] == "all"):
        modules = sorted(
            d.name
            for d in (project_root / "src" / "scitex").iterdir()
            if d.is_dir() and not d.name.startswith("_")
        )
    elif args:
        modules = args
    else:
        print(__doc__)
        sys.exit(1)

    all_missing = {}

    for module in modules:
        result = analyze_module(module, project_root, current_extras)

        if missing_only and not result["missing"]:
            continue

        print(f"\n{'=' * 60}")
        print(f"Module: {module}")
        print("=" * 60)

        if not missing_only:
            print(
                f"\nDetected external deps: {', '.join(result['needed_pypi']) or 'none'}"
            )
            print(
                f"Configured in [{module}]: {', '.join(result['current_deps']) or 'none'}"
            )

        if result["missing"]:
            print(f"\n⚠️  MISSING from pyproject.toml [{module}]:")
            for dep in result["missing"]:
                print(f'    "{dep}",')
            all_missing[module] = result["missing"]
        elif not missing_only:
            print("\n✅ All detected dependencies configured")

    if all_missing:
        print(f"\n{'=' * 60}")
        print("SUMMARY: Modules with missing dependencies")
        print("=" * 60)
        for mod, deps in all_missing.items():
            print(f"  [{mod}]: {', '.join(deps)}")


if __name__ == "__main__":
    main()
