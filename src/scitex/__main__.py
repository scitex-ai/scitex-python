#!/usr/bin/env python3
"""
SciTeX Package Entry Point

Allows running: python -m scitex [command]
"""

import importlib
import sys

from scitex_logging import getLogger

_log = getLogger(__name__)


def _check_cli_dependencies():
    """Check CLI dependencies and return missing ones."""
    missing = []
    try:
        importlib.import_module("click")
    except ImportError:
        missing.append(("click", "pip install click"))
    return missing


def main():
    """Main entry point for scitex CLI"""
    # Check dependencies first
    missing = _check_cli_dependencies()
    if missing:
        _log.error("SciTeX CLI missing dependencies:")
        for pkg, install in missing:
            _log.error(f"  - {pkg}: {install}")
        _log.error("\nOr install all CLI deps: pip install scitex[cli]")
        sys.exit(1)

    try:
        from scitex.cli.main import cli

        cli()
    except ImportError as e:
        _log.error(f"SciTeX CLI import error: {e}")
        _log.exception("Unable to load the SciTeX CLI")
        sys.exit(1)


if __name__ == "__main__":
    main()
