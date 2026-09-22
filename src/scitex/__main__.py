#!/usr/bin/env python3
"""
SciTeX Package Entry Point

Allows running: python -m scitex [command]
"""

import sys

import scitex_logging as slogging

log = slogging.getLogger(__name__)


def _check_cli_dependencies():
    """Check CLI dependencies and return missing ones."""
    missing = []
    try:
        import click
    except ImportError:
        missing.append(("click", "pip install click"))
    return missing


def main():
    """Main entry point for scitex CLI"""
    # Check dependencies first
    missing = _check_cli_dependencies()
    if missing:
        log.error("SciTeX CLI missing dependencies:")
        for pkg, install in missing:
            log.error(f"  - {pkg}: {install}")
        log.error("Or install all CLI deps: pip install scitex[cli]")
        sys.exit(1)

    try:
        from scitex.cli.main import cli

        cli()
    except ImportError as e:
        log.error(f"SciTeX CLI import error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
