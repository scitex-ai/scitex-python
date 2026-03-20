#!/usr/bin/env python3
"""
Utility for handling optional dependencies with helpful error messages.

SciTeX uses module-oriented optional dependencies. Install what you need:
    pip install scitex[audio]       # Audio/TTS module
    pip install scitex[scholar]     # Paper management
    pip install scitex[stats]       # Statistical analysis
    pip install scitex[io]          # File I/O operations
    pip install scitex[all]         # Everything

Multiple modules:
    pip install scitex[audio,scholar,stats]
"""

import importlib
from typing import Any, Callable, Dict, List, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

# Mapping of package imports to their installation extras
# Format: import_name -> (pip_package, install_extra)
PACKAGE_TO_EXTRA: Dict[str, tuple] = {
    # AI Module
    "openai": ("openai", "ai"),
    "anthropic": ("anthropic", "ai"),
    "google.generativeai": ("google-genai", "ai"),
    "groq": ("groq", "ai"),
    # Audio Module
    "pyttsx3": ("pyttsx3", "audio"),
    "gtts": ("gTTS", "audio"),
    "pydub": ("pydub", "audio"),
    "elevenlabs": ("elevenlabs", "audio"),
    # Benchmark/Resource Module
    "psutil": ("psutil", "benchmark"),
    # Browser/Capture Module
    "playwright": ("playwright", "browser"),
    "mss": ("mss", "capture"),
    # CLI Module
    "click": ("click", "cli"),
    # MCP Module (Model Context Protocol)
    "mcp": ("mcp", "mcp"),
    # DB Module
    "sqlalchemy": ("sqlalchemy", "db"),
    "psycopg2": ("psycopg2-binary", "db"),
    # DSP Module
    "sounddevice": ("sounddevice", "dsp"),
    # Gen Module
    "IPython": ("ipython", "gen"),
    "pyperclip": ("pyperclip", "gen"),
    "readchar": ("readchar", "gen"),
    # Git Module
    "git": ("GitPython", "git"),
    # IO Module
    "h5py": ("h5py", "io"),
    "openpyxl": ("openpyxl", "io"),
    "xlrd": ("xlrd", "io"),
    "ruamel": ("ruamel.yaml", "io"),
    "xarray": ("xarray", "io"),
    "zarr": ("zarr", "io"),
    "PIL": ("Pillow", "io"),
    "piexif": ("piexif", "io"),
    "pypdf": ("pypdf", "io"),
    "qrcode": ("qrcode[pil]", "io"),
    # PyPDF2 removed — use "pypdf" (line above) instead
    "fitz": ("PyMuPDF", "io"),
    "pdfplumber": ("pdfplumber", "io"),
    "docx": ("python-docx", "io"),
    "html2text": ("html2text", "io"),
    "plotly": ("plotly", "io"),
    "pymatreader": ("pymatreader", "io"),
    # Linalg Module
    "sympy": ("sympy", "linalg"),
    "geom_median": ("geom_median", "linalg"),
    # MSWord Module
    "pypandoc": ("pypandoc", "msword"),
    # NN Module
    "torch": ("torch", "nn"),
    "torchaudio": ("torchaudio", "nn"),
    "torchsummary": ("torchsummary", "nn"),
    "julius": ("julius", "nn"),
    # PLT Module
    "matplotlib": ("matplotlib", "plt"),
    "seaborn": ("seaborn", "plt"),
    "termplotlib": ("termplotlib", "plt"),
    # Scholar Module
    "selenium": ("selenium", "scholar"),
    "bs4": ("beautifulsoup4", "scholar"),
    "crawl4ai": ("crawl4ai", "scholar"),
    "scholarly": ("scholarly", "scholar"),
    "pymed": ("pymed", "scholar"),
    "pytesseract": ("pytesseract", "scholar"),
    "bibtexparser": ("bibtexparser", "scholar"),
    "feedparser": ("feedparser", "scholar"),
    "httpx": ("httpx", "scholar"),
    "tenacity": ("tenacity", "scholar"),
    "pydantic": ("pydantic", "scholar"),
    "watchdog": ("watchdog", "scholar"),
    # Stats Module
    "scipy": ("scipy", "stats"),
    "statsmodels": ("statsmodels", "stats"),
    # Web Module
    "aiohttp": ("aiohttp", "web"),
    "requests": ("requests", "web"),
    "readability": ("readability-lxml", "web"),
    # Writer Module
    "yq": ("yq", "writer"),
    # DL Module (convenience group)
    "torchvision": ("torchvision", "dl"),
    "transformers": ("transformers", "dl"),
    "accelerate": ("accelerate", "dl"),
    "bitsandbytes": ("bitsandbytes", "dl"),
    "fairscale": ("fairscale", "dl"),
    "einops": ("einops", "dl"),
    # ML Module (convenience group)
    "sklearn": ("scikit-learn", "ml"),
    "skimage": ("scikit-image", "ml"),
    "imblearn": ("imbalanced-learn", "ml"),
    "umap": ("umap-learn", "ml"),
    "sktime": ("sktime", "ml"),
    "catboost": ("catboost", "ml"),
    "optuna": ("optuna", "ml"),
    "cv2": ("opencv-python", "ml"),
    # Jupyter Module
    "jupyterlab": ("jupyterlab", "jupyter"),
    "ipykernel": ("ipykernel", "jupyter"),
    "ipdb": ("ipdb", "jupyter"),
    "papermill": ("papermill", "jupyter"),
    "jupytext": ("jupytext", "jupyter"),
    # Neuro Module
    "mne": ("mne", "neuro"),
    "obspy": ("obspy", "neuro"),
    "pyedflib": ("pyedflib", "neuro"),
    "pybids": ("pybids", "neuro"),
    "tensorpac": ("tensorpac", "neuro"),
    "ripple_detection": ("ripple_detection", "neuro"),
    # Webdev Module
    "fastapi": ("fastapi", "webdev"),
    "flask": ("flask", "webdev"),
    "streamlit": ("streamlit", "webdev"),
    "celery": ("celery", "webdev"),
    # GUI Module
    "dearpygui": ("dearpygui", "gui"),
    "PyQt6": ("PyQt6", "gui"),
}

# Backwards compatibility: simple mapping
DEPENDENCY_GROUPS: Dict[str, str] = {
    module: info[1] for module, info in PACKAGE_TO_EXTRA.items()
}


def optional_import(
    module_name: str, package_name: Optional[str] = None, raise_error: bool = True
) -> Optional[Any]:
    """
    Import an optional dependency with helpful error message.

    Args:
        module_name: Name of the module to import (e.g., 'torch')
        package_name: Name of the package to install if different from module
        raise_error: If True, raise ImportError. If False, return None.

    Returns
    -------
        The imported module, or None if raise_error=False and import fails

    Examples
    --------
        >>> torch = optional_import('torch')
        >>> torch = optional_import('torch', raise_error=False)  # Returns None if not installed
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        if not raise_error:
            return None

        pkg_info = PACKAGE_TO_EXTRA.get(module_name)
        if pkg_info:
            pip_pkg, extra = pkg_info
        else:
            pip_pkg = package_name or module_name
            extra = "all"

        error_msg = (
            f"\n{'=' * 70}\n"
            f"Optional dependency '{pip_pkg}' is not installed.\n\n"
            f"To use this feature, install it with:\n"
            f"  pip install scitex[{extra}]\n\n"
            f"Or install all optional dependencies:\n"
            f"  pip install scitex[all]\n"
            f"{'=' * 70}\n"
        )
        raise ImportError(error_msg)


def check_optional_deps(*module_names: str) -> Dict[str, bool]:
    """
    Check which optional dependencies are available.

    Args:
        *module_names: Names of modules to check

    Returns
    -------
        Dictionary mapping module names to availability (True/False)

    Example:
        >>> available = check_optional_deps('torch', 'transformers')
        >>> if available['torch']:
        ...     import torch
    """
    result = {}
    for name in module_names:
        try:
            importlib.import_module(name)
            result[name] = True
        except ImportError:
            result[name] = False
    return result


def get_install_command(module_name: str) -> str:
    """
    Get the pip install command for a module.

    Args:
        module_name: Name of the module

    Returns
    -------
        pip install command string

    Example:
        >>> get_install_command('torch')
        'pip install scitex[nn]'
    """
    pkg_info = PACKAGE_TO_EXTRA.get(module_name)
    if pkg_info:
        return f"pip install scitex[{pkg_info[1]}]"
    return "pip install scitex[all]"


def list_available_extras() -> List[str]:
    """
    List all available installation extras.

    Returns
    -------
        List of extra names (e.g., ['audio', 'scholar', 'stats', ...])
    """
    extras = set(info[1] for info in PACKAGE_TO_EXTRA.values())
    # Add convenience groups
    extras.update(
        ["science", "dl", "ml", "jupyter", "neuro", "webdev", "gui", "dev", "all"]
    )
    return sorted(extras)


# Convenience functions for common checks
def has_deep_learning() -> bool:
    """Check if deep learning dependencies are available."""
    return check_optional_deps("torch")["torch"]


def has_transformers() -> bool:
    """Check if transformers is available."""
    return check_optional_deps("transformers")["transformers"]


def has_scholar() -> bool:
    """Check if scholar dependencies are available."""
    deps = check_optional_deps("selenium", "bs4")
    return all(deps.values())


def has_jupyter() -> bool:
    """Check if Jupyter dependencies are available."""
    return check_optional_deps("IPython")["IPython"]


def has_audio() -> bool:
    """Check if audio/TTS dependencies are available."""
    deps = check_optional_deps("pyttsx3", "gtts")
    return any(deps.values())


def has_stats() -> bool:
    """Check if stats dependencies are available."""
    return check_optional_deps("scipy", "statsmodels") == {
        "scipy": True,
        "statsmodels": True,
    }


def has_io() -> bool:
    """Check if IO dependencies are available."""
    return check_optional_deps("h5py")["h5py"]


def has_plotting() -> bool:
    """Check if plotting dependencies are available."""
    return check_optional_deps("matplotlib")["matplotlib"]


def has_mcp() -> bool:
    """Check if MCP (Model Context Protocol) dependencies are available."""
    return check_optional_deps("mcp")["mcp"]


def check_mcp_deps(server_name: str = "scitex") -> None:
    """
    Check MCP dependencies and exit with helpful message if missing.

    Use at the start of MCP server main() functions for graceful handling.

    Args:
        server_name: Name of the MCP server for error messages
    """
    import sys

    try:
        import mcp  # noqa: F401
    except ImportError:
        print(f"{'=' * 60}")
        print(f"MCP Server '{server_name}' requires the 'mcp' package.")
        print()
        print("Install with:")
        print("  pip install mcp")
        print()
        print("Or install scitex with MCP support:")
        print("  pip install scitex[mcp]")
        print(f"{'=' * 60}")
        sys.exit(1)


# EOF
