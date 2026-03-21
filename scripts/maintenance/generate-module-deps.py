#!/usr/bin/env python3
"""Generate pyproject.toml extras from import analysis.

Scans all modules and generates the optional-dependencies section
based on actual imports in source and test code.

Usage:
    ./scripts/maintenance/generate-module-deps.py              # Print to stdout
    ./scripts/maintenance/generate-module-deps.py --update     # Update pyproject.toml
"""

import ast
import re
import sys
from pathlib import Path

from stdlib_list import stdlib_list

PROJECT_ROOT = Path(__file__).parent.parent.parent
STDLIB = set(stdlib_list())

# Import name -> PyPI package name mapping
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

# Internal packages to ignore
INTERNAL = {"scitex", "mngs"}

# Base dependencies (in core install, don't add to extras)
BASE_DEPS = {
    "numpy",
    "pandas",
    "scipy",
    "tqdm",
    "psutil",
    "pyyaml",  # Very common, should be base
    "matplotlib",  # Very common, should be base
}

# Test-only dependencies (don't add to module extras)
TEST_ONLY = {
    "pytest",
    "hypothesis",
    "pytest_cov",
    "pytest_mock",
}

# Known PyPI packages (whitelist to avoid false positives)
KNOWN_PYPI = {
    "aiohttp",
    "bs4",
    "catboost",
    "cv2",
    "dearpygui",
    "docx",
    "fitz",
    "flask",
    "git",
    "h5py",
    "html2text",
    "jax",
    "joblib",
    "librosa",
    "lightgbm",
    "lxml",
    "markdown",
    "matplotlib",
    "mne",
    "natsort",
    "networkx",
    "numcodecs",
    "openpyxl",
    "optuna",
    "pdfplumber",
    "piexif",
    "PIL",
    "playwright",
    "plotly",
    "pyarrow",
    "pyaudio",
    "pyautogui",
    "pydub",
    "pymatreader",
    "pynput",
    "pypdf",
    "PyQt5",
    "PyQt6",
    "qrcode",
    "requests",
    "ruamel",
    "seaborn",
    "selenium",
    "sklearn",
    "skimage",
    "sounddevice",
    "soundfile",
    "sympy",
    "tensorflow",
    "torch",
    "xarray",
    "xgboost",
    "xlrd",
    "yaml",
    "zarr",
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
            if node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
    return imports


def get_module_deps(module: str) -> set[str]:
    """Get external dependencies for a module."""
    src_dir = PROJECT_ROOT / "src" / "scitex" / module
    test_dir = PROJECT_ROOT / "tests" / "scitex" / module

    all_imports = set()
    for d in [src_dir, test_dir]:
        if d.exists():
            for py_file in d.rglob("*.py"):
                all_imports |= extract_imports(py_file)

    # Filter to external, known packages
    external = set()
    for imp in all_imports:
        if imp in STDLIB or imp in INTERNAL or imp in BASE_DEPS or imp in TEST_ONLY:
            continue
        if imp.startswith("_"):
            continue
        if imp in KNOWN_PYPI or imp in IMPORT_TO_PYPI:
            pypi_name = IMPORT_TO_PYPI.get(imp, imp)
            external.add(pypi_name)

    return external


def generate_extras_toml() -> str:
    """Generate the optional-dependencies section."""
    modules = sorted(
        d.name
        for d in (PROJECT_ROOT / "src" / "scitex").iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    lines = ["[project.optional-dependencies]", ""]

    for module in modules:
        deps = get_module_deps(module)
        if deps:
            lines.append(f"# {module.upper()} Module")
            lines.append(f"# Use: pip install scitex[{module}]")
            lines.append(f"{module} = [")
            for dep in sorted(deps):
                lines.append(f'    "{dep}",')
            lines.append("]")
            lines.append("")

    return "\n".join(lines)


def main():
    update = "--update" in sys.argv

    toml_content = generate_extras_toml()

    if update:
        # Read existing pyproject.toml
        pyproject = PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text()

        # Find and replace the optional-dependencies section
        pattern = r"\[project\.optional-dependencies\].*?(?=\n\[|\Z)"
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, toml_content, content, flags=re.DOTALL)
            pyproject.write_text(new_content)
            print(f"Updated {pyproject}")
        else:
            print("Could not find [project.optional-dependencies] section")
            sys.exit(1)
    else:
        print(toml_content)
        print("\n# Run with --update to apply changes to pyproject.toml")


if __name__ == "__main__":
    main()
