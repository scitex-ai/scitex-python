#!/usr/bin/env python3
"""
SciTeX Package Entry Point

Allows running: python -m scitex [command]
"""

import sys

import scitex_logging as slogging

logger = slogging.getLogger(__name__)


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
        logger.error("SciTeX CLI missing dependencies:")
        for pkg, install in missing:
            logger.error(f"  - {pkg}: {install}")
        logger.error("\nOr install all CLI deps: pip install scitex[cli]")
        sys.exit(1)

    from click import ClickException

    try:
        try:
            from scitex.cli.main import cli
        except ClickException as error:
            # Construction/configuration refusal is a user-facing startup
            # error. Keep this boundary outside actual command execution.
            logger.error(error.format_message())
            sys.exit(error.exit_code)

        cli()
    except ImportError as e:
        logger.error(f"SciTeX CLI import error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
