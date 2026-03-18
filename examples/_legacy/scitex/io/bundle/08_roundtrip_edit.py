#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/08_roundtrip_edit.py

"""
Example 08: Round-Trip Edit

Demonstrates:
- Load existing FTS bundle
- Modify node, encoding, or theme
- Save changes back to bundle
- Verify changes persisted
"""

import hashlib
import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def file_hash(path):
    """Compute MD5 hash of a file."""
    if not path.exists():
        return None
    return hashlib.md5(path.read_bytes()).hexdigest()[:12]


def cleanup_existing(out_dir, name):
    """Remove existing bundle."""
    path = out_dir / name
    if path.exists():
        shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_initial_bundle(plt, bundle_path, logger):
    """Create initial bundle with plot."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: Create initial bundle")
    logger.info("=" * 60)

    x = np.linspace(0, 10, 50)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(x, np.sin(x), linewidth=1.5, label="sin(x)")
    ax.plot(x, np.cos(x), linewidth=1.5, label="cos(x)")
    ax.legend()
    ax.set_title("Original")

    sio.save(fig, bundle_path)
    plt.close(fig)

    bundle = FTS(bundle_path)
    bundle.node.name = "Round-Trip Demo"
    bundle.theme = {"mode": "light", "colors": {"primary": "#1f77b4"}}
    bundle.save()

    return bundle


def record_hashes(bundle_path):
    """Record hashes for all JSON files."""
    return {
        "node.json": file_hash(bundle_path / "node.json"),
        "encoding.json": file_hash(bundle_path / "encoding.json"),
        "theme.json": file_hash(bundle_path / "theme.json"),
    }


def edit_theme(bundle_path, logger):
    """Edit theme in bundle."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Edit theme (change mode to dark)")
    logger.info("=" * 60)

    bundle = FTS(bundle_path)
    original_mode = bundle.theme.mode

    bundle.theme = {
        "mode": "dark",
        "colors": {"primary": "#ff7f0e", "background": "#1a1a1a"},
    }
    bundle.save()

    logger.info(f"  Changed mode: {original_mode} -> dark")
    logger.info("  Changed colors.primary: #1f77b4 -> #ff7f0e")


def edit_node_name(bundle_path, logger):
    """Edit node name in bundle."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Edit node name")
    logger.info("=" * 60)

    bundle = FTS(bundle_path)
    original_name = bundle.node.name
    bundle.node.name = "Updated Demo"
    bundle.save()

    logger.info(f"  Changed name: {original_name} -> Updated Demo")


def print_change_report(initial_hashes, final_hashes, logger):
    """Print change report comparing initial and final hashes."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: Change Report")
    logger.info("=" * 60)

    logger.info(f"\n{'File':<20} {'Initial':<14} {'Final':<14} {'Status':<10}")
    logger.info("-" * 60)

    for name in initial_hashes:
        initial = initial_hashes[name]
        final = final_hashes[name]
        if initial == final:
            status = "UNCHANGED"
        elif initial is None:
            status = "NEW"
        elif final is None:
            status = "DELETED"
        else:
            status = "CHANGED"
        logger.info(f"{name:<20} {initial or 'N/A':<14} {final or 'N/A':<14} {status:<10}")


def verify_data_integrity(bundle_path, logger):
    """Verify final bundle data integrity."""
    logger.info("\n" + "-" * 40)
    logger.info("Data integrity check:")
    final_bundle = FTS(bundle_path)
    logger.info(f"  node.name: {final_bundle.node.name}")
    logger.info(f"  theme.mode: {final_bundle.theme.mode}")


def print_summary(logger):
    """Print summary of changes."""
    logger.info("\n" + "=" * 60)
    logger.info("Summary:")
    logger.info("  - node.json: CHANGED (updated name)")
    logger.info("  - encoding.json: UNCHANGED (not modified)")
    logger.info("  - theme.json: CHANGED (updated mode and colors)")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate round-trip editing of FTS bundles."""
    logger.info("Example 08: Round-Trip Edit Demo")

    out_dir = CONFIG["SDIR_OUT"]
    bundle_path = out_dir / "roundtrip_demo.zip"

    cleanup_existing(out_dir, "roundtrip_demo.zip")

    create_initial_bundle(plt, bundle_path, logger)
    initial_hashes = record_hashes(bundle_path)

    logger.info("\nInitial file hashes:")
    for name, h in initial_hashes.items():
        logger.info(f"  {name}: {h}")

    edit_theme(bundle_path, logger)
    edit_node_name(bundle_path, logger)

    final_hashes = record_hashes(bundle_path)

    print_change_report(initial_hashes, final_hashes, logger)
    verify_data_integrity(bundle_path, logger)
    print_summary(logger)

    logger.success("Example 08 completed!")


if __name__ == "__main__":
    main()

# EOF
