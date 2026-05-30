#!/usr/bin/env python3
"""
Installation guide and module dependency checking for SciTeX.

This module provides helpers to check module dependencies and show
helpful installation guides when dependencies are missing.
"""

import functools
import importlib
import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from ._optional_deps import PACKAGE_TO_EXTRA, check_optional_deps

F = TypeVar("F", bound=Callable[..., Any])

# Module name -> (required_packages, extra_name, description)
# Synced with pyproject.toml [project.optional-dependencies]
MODULE_REQUIREMENTS: Dict[str, Tuple[List[str], str, str]] = {
    "ai": (["openai", "anthropic"], "ai", "LLM APIs"),
    "audio": (["pyttsx3", "gtts"], "audio", "Text-to-Speech"),
    "benchmark": (["psutil"], "benchmark", "Performance Monitoring"),
    "bridge": (["matplotlib", "scipy"], "bridge", "External System Integration"),
    "browser": (["playwright"], "browser", "Web Automation"),
    "capture": (["mss", "PIL"], "capture", "Screenshot Capture"),
    "cli": (["click"], "cli", "Command Line Interface"),
    "cloud": (["matplotlib"], "cloud", "Cloud Service Integration"),
    "config": (["pyyaml"], "config", "Configuration Management"),
    "db": (["sqlalchemy"], "db", "Database"),
    "decorators": (["joblib"], "decorators", "Caching Utilities"),
    "devtools": (["joblib", "ruamel.yaml"], "devtools", "Development Tools"),
    "diagram": (["pyyaml"], "diagram", "Diagram Generation"),
    "dsp": (["scipy", "sounddevice"], "dsp", "Signal Processing"),
    "dt": (["matplotlib"], "dt", "Date/Time Utilities"),
    "gen": (["IPython", "h5py"], "gen", "General Utilities"),
    "git": (["git"], "git", "Git Operations"),
    "io": (["h5py", "openpyxl"], "io", "File I/O"),
    "linalg": (["scipy", "sympy"], "linalg", "Linear Algebra"),
    "logging": (["matplotlib"], "logging", "Enhanced Logging"),
    "msword": (["docx"], "msword", "MS Word"),
    "nn": (["torch"], "nn", "Neural Networks"),
    "parallel": (["tqdm"], "parallel", "Parallel Processing"),
    "path": (["git"], "path", "Path Utilities"),
    "pd": (["xarray"], "pd", "Pandas Utilities"),
    "plt": (["matplotlib", "seaborn"], "plt", "Plotting"),
    "repro": (["torch"], "repro", "Reproducibility"),
    "resource": (["psutil"], "resource", "Resource Monitoring"),
    "scholar": (["selenium", "bs4", "playwright"], "scholar", "Paper Management"),
    "session": (["matplotlib", "pyyaml"], "session", "Session Management"),
    "sh": (["matplotlib"], "sh", "Shell Utilities"),
    "stats": (["scipy", "statsmodels"], "stats", "Statistical Analysis"),
    "str": (["natsort"], "str", "String Utilities"),
    "tex": (["matplotlib"], "tex", "LaTeX Utilities"),
    "torch": (["torch"], "torch", "PyTorch Support"),
    "types": (["xarray"], "types", "Type Utilities"),
    "utils": (["h5py", "natsort"], "utils", "General Utilities"),
    "web": (["aiohttp", "bs4"], "web", "Web Utilities"),
    "writer": (["yq"], "writer", "Academic Writing"),
}


def check_module_deps(module_name: str) -> Dict[str, Any]:
    """
    Check if a module's dependencies are installed.

    Args:
        module_name: Name of the scitex module (e.g., 'audio', 'scholar')

    Returns:
        Dict with keys:
        - available: bool - whether all required deps are installed
        - missing: list - list of missing packages
        - install_cmd: str - command to install missing deps
        - extra: str - the installation extra name
    """
    if module_name not in MODULE_REQUIREMENTS:
        return {"available": True, "missing": [], "install_cmd": "", "extra": ""}

    required, extra, _desc = MODULE_REQUIREMENTS[module_name]
    available = check_optional_deps(*required)
    missing = [pkg for pkg, is_available in available.items() if not is_available]

    return {
        "available": len(missing) == 0,
        "missing": missing,
        "install_cmd": f"pip install scitex[{extra}]",
        "extra": extra,
    }


def require_module(module_name: str) -> None:
    """
    Check module dependencies and raise helpful error if missing.

    Call this at the top of a module's __init__.py to provide
    clear guidance when dependencies aren't installed.

    Args:
        module_name: Name of the scitex module

    Raises:
        ImportError: With helpful installation instructions

    Example:
        # In scitex/audio/__init__.py:
        from scitex._install_guide import require_module
        require_module("audio")  # Raises helpful error if deps missing
    """
    result = check_module_deps(module_name)

    if not result["available"]:
        if module_name in MODULE_REQUIREMENTS:
            _, extra, desc = MODULE_REQUIREMENTS[module_name]
        else:
            extra, desc = "all", module_name

        missing_str = ", ".join(result["missing"])
        raise ImportError(
            f"\n"
            f"{'=' * 70}\n"
            f"scitex.{module_name} - {desc}\n"
            f"{'=' * 70}\n"
            f"\n"
            f"This module requires dependencies that are not installed:\n"
            f"  Missing: {missing_str}\n"
            f"\n"
            f"To use this module, install with:\n"
            f"\n"
            f"    {result['install_cmd']}\n"
            f"\n"
            f"Or install all optional dependencies:\n"
            f"\n"
            f"    pip install scitex[all]\n"
            f"\n"
            f"{'=' * 70}\n"
        )


def warn_module_deps(module_name: str) -> List[str]:
    """
    Check module dependencies and print warning if missing (non-blocking).

    Unlike require_module(), this doesn't raise an error, just warns.

    Args:
        module_name: Name of the scitex module

    Returns:
        List of missing package names
    """
    result = check_module_deps(module_name)

    if not result["available"]:
        if module_name in MODULE_REQUIREMENTS:
            _, extra, desc = MODULE_REQUIREMENTS[module_name]
        else:
            extra, desc = "all", module_name

        missing_str = ", ".join(result["missing"])
        warnings.warn(
            f"\nscitex.{module_name} ({desc}): Some features unavailable.\n"
            f"Missing: {missing_str}\n"
            f"Install with: {result['install_cmd']}\n",
            ImportWarning,
            stacklevel=2,
        )

    return result["missing"]


def requires(*packages: str, extra: Optional[str] = None):
    """
    Decorator that checks dependencies before function execution.

    Args:
        *packages: Required package names
        extra: Installation extra name (auto-detected if not provided)

    Example:
        @requires("torch", "torchvision", extra="dl")
        def train_model(data):
            import torch
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            missing = []
            for pkg in packages:
                try:
                    importlib.import_module(pkg)
                except ImportError:
                    missing.append(pkg)

            if missing:
                install_extra = extra
                if install_extra is None:
                    pkg_info = PACKAGE_TO_EXTRA.get(missing[0])
                    install_extra = pkg_info[1] if pkg_info else "all"

                missing_str = ", ".join(missing)
                raise ImportError(
                    f"\n"
                    f"Function '{func.__name__}' requires: {missing_str}\n"
                    f"Install with: pip install scitex[{install_extra}]\n"
                )

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def show_install_guide(module_name: Optional[str] = None) -> None:
    """
    Print installation guide for scitex modules.

    Args:
        module_name: Specific module to show guide for, or None for all

    Example:
        >>> from scitex._install_guide import show_install_guide
        >>> show_install_guide("audio")
        >>> show_install_guide()  # Shows all modules
    """
    print("\n" + "=" * 70)
    print("SciTeX Installation Guide")
    print("=" * 70)

    if module_name:
        if module_name in MODULE_REQUIREMENTS:
            required, extra, desc = MODULE_REQUIREMENTS[module_name]
            result = check_module_deps(module_name)
            status = "Installed" if result["available"] else "Not installed"

            print(f"\n{module_name} - {desc}")
            print(f"  Status: {status}")
            print(f"  Install: pip install scitex[{extra}]")
            if not result["available"]:
                print(f"  Missing: {', '.join(result['missing'])}")
        else:
            print(f"\nModule '{module_name}' not found.")
    else:
        print("\nModule-oriented installation (install only what you need):\n")

        for mod_name, (required, extra, desc) in sorted(MODULE_REQUIREMENTS.items()):
            result = check_module_deps(mod_name)
            status = "[ok]" if result["available"] else "[--]"
            print(f"  {status} {mod_name:12} pip install scitex[{extra}]")

        print("\nConvenience groups:\n")
        print("  pip install scitex[science]  # scipy, matplotlib, scikit-learn")
        print("  pip install scitex[dl]       # PyTorch, transformers")
        print("  pip install scitex[all]      # Everything")

    print("\n" + "=" * 70 + "\n")


# EOF
