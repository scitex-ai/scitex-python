#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/15_zip_portability.py

"""
Example 15: ZIP Portability

Demonstrates:
- directory bundle or .zip archive format
- .zip archive format
- Both formats are fully interchangeable
"""

import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(bundle_path):
    """Remove existing bundle."""
    if bundle_path.exists():
        if bundle_path.is_dir():
            shutil.rmtree(bundle_path)
        else:
            bundle_path.unlink()


def create_directory_bundle(plt, out_dir, x, logger):
    """Create directory bundle."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: Create directory bundle or .zip archive")
    logger.info("=" * 60)

    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot(x, np.sin(x), "b-", linewidth=1.5, label="sin(x)")
    ax.plot(x, np.cos(x), "r--", linewidth=1.5, label="cos(x)")
    ax.legend()
    ax.set_title("Portable Plot")

    dir_bundle = out_dir / "portable_figure.zip"
    sio.save(fig, dir_bundle)
    plt.close(fig)

    bundle = FTS(dir_bundle)
    bundle.node.name = "Portable Figure"
    bundle.theme = {"mode": "light", "colors": {"primary": "#1f77b4"}}
    bundle.save()

    logger.info(f"  Created: {dir_bundle}")
    logger.info(f"  Is directory: {dir_bundle.is_dir()}")

    return dir_bundle


def create_zip_bundle(plt, out_dir, x, logger):
    """Create ZIP archive bundle."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Create .zip archive")
    logger.info("=" * 60)

    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot(x, np.sin(x), "b-", linewidth=1.5)
    ax.set_title("ZIP Bundle")

    zip_bundle = out_dir / "portable_figure.zip"
    sio.save(fig, zip_bundle, as_zip=True)
    plt.close(fig)

    logger.info(f"  Created: {zip_bundle}")
    logger.info(f"  Is file: {zip_bundle.is_file()}")
    logger.info(f"  Size: {zip_bundle.stat().st_size / 1024:.1f} KB")

    return zip_bundle


def load_both_formats(dir_bundle, zip_bundle, logger):
    """Load bundles from both formats."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Load from both formats")
    logger.info("=" * 60)

    dir_loaded = FTS(dir_bundle)
    zip_loaded = FTS(zip_bundle)

    logger.info(f"  Directory bundle: type={dir_loaded.bundle_type}")
    logger.info(f"  ZIP bundle: type={zip_loaded.bundle_type}")


def verify_content(dir_bundle, zip_bundle, logger):
    """Verify content of bundles."""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICATION")
    logger.info("=" * 60)

    logger.info("\nDirectory bundle structure:")
    for f in sorted(dir_bundle.rglob("*"))[:10]:
        if f.is_file():
            rel = f.relative_to(dir_bundle)
            logger.info(f"  {rel}")

    logger.info("\nZIP bundle (single file):")
    logger.info(f"  {zip_bundle.name} ({zip_bundle.stat().st_size / 1024:.1f} KB)")


def print_summary(logger):
    """Print format comparison summary."""
    logger.info("\n" + "=" * 60)
    logger.info("Format Comparison:")
    logger.info("  directory bundle:")
    logger.info("    - Human-readable files")
    logger.info("    - Easy to inspect/edit manually")
    logger.info("    - Good for development")
    logger.info("  .zip (archive):")
    logger.info("    - Single portable file")
    logger.info("    - Good for sharing/archiving")
    logger.info("    - Compressed storage")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate ZIP portability."""
    logger.info("Example 15: ZIP Portability")

    out_dir = CONFIG["SDIR_OUT"]
    x = np.linspace(0, 10, 50)

    dir_bundle = out_dir / "portable_figure.zip"
    zip_bundle = out_dir / "portable_figure.zip"

    cleanup_existing(dir_bundle)
    cleanup_existing(zip_bundle)

    dir_bundle = create_directory_bundle(plt, out_dir, x, logger)
    zip_bundle = create_zip_bundle(plt, out_dir, x, logger)
    load_both_formats(dir_bundle, zip_bundle, logger)
    verify_content(dir_bundle, zip_bundle, logger)
    print_summary(logger)

    logger.success("Example 15 completed!")


if __name__ == "__main__":
    main()

# EOF
