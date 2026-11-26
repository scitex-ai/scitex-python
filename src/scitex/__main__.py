#!/usr/bin/env python3
"""
SciTeX Package Entry Point

Allows running: python -m scitex [command]
"""

import sys


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
        import scitex_logging as slogging

        lines = ["SciTeX CLI missing dependencies:"]
        lines += [f"  - {pkg}: {install}" for pkg, install in missing]
        lines.append("\nOr install all CLI deps: pip install scitex[cli]")
        slogging.getLogger(__name__).error("\n".join(lines))
        sys.exit(1)

    try:
        from scitex.cli.main import cli

        cli()
    except ImportError as e:
        import scitex_logging as slogging

        slogging.getLogger(__name__).error("SciTeX CLI import error: %s", e)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
