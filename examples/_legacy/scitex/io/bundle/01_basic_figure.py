#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/01_basic_figure.py

"""
Example 01: Basic FTS Bundle Creation

Demonstrates:
- Creating a new FTS figure bundle (.zip or directory)
- Setting figure name and size
- Saving as ZIP (.zip) or directory
"""

import shutil

import scitex as stx
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, names):
    """Remove existing bundles."""
    for name in names:
        path = out_dir / name
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_bundle(path, name, size_mm):
    """Create and save FTS bundle."""
    bundle = FTS(
        path,
        create=True,
        node_type="figure",
        name=name,
        size_mm=size_mm,
    )
    bundle.save()
    return bundle


def log_bundle_info(logger, bundle, prefix=""):
    """Log bundle details."""
    logger.info(f"{prefix}Bundle ID: {bundle.node.id}")
    logger.info(f"{prefix}Name: {bundle.node.name}")
    logger.info(f"{prefix}Size: {bundle.node.size_mm}")
    logger.info(f"{prefix}Type: {bundle.bundle_type}")


@stx.session(verbose=False, agg=True)
def main(CONFIG=INJECTED, logger=INJECTED):
    """Create a basic FTS figure bundle."""
    logger.info("Example 01: Basic FTS Bundle Creation")

    out_dir = CONFIG["SDIR_OUT"]
    size_mm = {"width": 170, "height": 120}

    cleanup_existing(out_dir, ["my_figure.zip", "my_figure"])

    # Create ZIP bundle
    zip_bundle = create_bundle(out_dir / "my_figure.zip", "My First Figure", size_mm)
    logger.info(f"Saved as ZIP: {zip_bundle.path}")
    log_bundle_info(logger, zip_bundle, "  ")

    # Create directory bundle
    dir_bundle = create_bundle(out_dir / "my_figure", "My First Figure", size_mm)
    logger.info(f"Saved as directory: {dir_bundle.path}")

    # Reload and verify
    reloaded = FTS(out_dir / "my_figure.zip")
    logger.info(f"Reloaded ID: {reloaded.node.id}")
    logger.info(f"Children: {reloaded.node.children}")

    logger.success("Example 01 completed!")


if __name__ == "__main__":
    main()

# EOF
