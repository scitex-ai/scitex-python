#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/07_bundle_structure.py

"""
Example 07: FTS Bundle Structure

Demonstrates:
- Understanding FTS bundle directory structure
- Inspecting node.json, theme.json, encoding.json
- Understanding canonical vs export files
"""

import json
import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, name):
    """Remove existing bundle."""
    path = out_dir / name
    if path.exists():
        shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_plot(plt, out_dir):
    """Create and save plot as FTS bundle."""
    x = np.linspace(0, 10, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)")
    ax.legend()
    ax.set_title("Inspection Demo")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    sio.save(fig, out_dir / "inspectable.zip")
    plt.close(fig)


def configure_bundle(out_dir):
    """Load and configure bundle."""
    bundle = FTS(out_dir / "inspectable.zip")
    bundle.node.name = "Inspection Demo"
    bundle.theme = {
        "mode": "light",
        "figure_title": {"text": "Demo Figure", "number": 1},
    }
    bundle.save()
    return bundle


def list_bundle_structure(bundle, logger):
    """List all files in bundle."""
    logger.info("\n📁 BUNDLE STRUCTURE:")
    for f in sorted(bundle.path.rglob("*")):
        if f.is_file():
            rel = f.relative_to(bundle.path)
            size = f.stat().st_size
            logger.info(f"  {rel} ({size} bytes)")


def inspect_node_json(bundle, logger):
    """Inspect node.json file."""
    node_path = bundle.path / "node.json"
    if node_path.exists():
        with open(node_path) as f:
            node = json.load(f)
        logger.info("\nnode.json:")
        logger.info(f"  id: {node.get('id', 'N/A')[:12]}...")
        logger.info(f"  type: {node.get('type')}")
        logger.info(f"  name: {node.get('name')}")
        logger.info(f"  size_mm: {node.get('size_mm')}")


def inspect_encoding_json(bundle, logger):
    """Inspect encoding.json file."""
    encoding_path = bundle.path / "encoding.json"
    if encoding_path.exists():
        with open(encoding_path) as f:
            encoding = json.load(f)
        logger.info("\nencoding.json (data→visual mapping):")
        logger.info(f"  traces: {len(encoding.get('traces', []))}")


def inspect_theme_json(bundle, logger):
    """Inspect theme.json file."""
    theme_path = bundle.path / "theme.json"
    if theme_path.exists():
        with open(theme_path) as f:
            theme = json.load(f)
        logger.info("\ntheme.json (aesthetics):")
        logger.info(f"  mode: {theme.get('mode')}")
        logger.info(f"  figure_title: {theme.get('figure_title', {}).get('text')}")


def inspect_data_files(bundle, logger):
    """List data directory contents."""
    logger.info("\n📊 DATA FILES:")
    data_dir = bundle.path / "data"
    if data_dir.exists():
        for f in data_dir.iterdir():
            logger.info(f"  {f.name}")
    else:
        logger.info("  (no data directory)")


def inspect_export_files(bundle, logger):
    """List exports directory contents."""
    logger.info("\n📤 EXPORT FILES (derived):")
    exports_dir = bundle.path / "exports"
    if exports_dir.exists():
        for f in exports_dir.iterdir():
            logger.info(f"  {f.name}")
    else:
        logger.info("  (no exports directory)")


def print_summary(logger):
    """Print file categories summary."""
    logger.info("\n" + "=" * 60)
    logger.info("File categories:")
    logger.info("  CANONICAL: node.json, encoding.json, theme.json, data/*")
    logger.info("  EXPORT: exports/* (derived outputs)")


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Inspect FTS bundle structure."""
    logger.info("Example 07: FTS Bundle Structure")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, "inspectable.zip")

    create_plot(plt, out_dir)
    bundle = configure_bundle(out_dir)

    logger.info(f"\nBundle path: {bundle.path}")
    logger.info("=" * 60)

    list_bundle_structure(bundle, logger)

    logger.info("\n📄 CANONICAL FILES (source of truth):")
    inspect_node_json(bundle, logger)
    inspect_encoding_json(bundle, logger)
    inspect_theme_json(bundle, logger)

    inspect_data_files(bundle, logger)
    inspect_export_files(bundle, logger)

    print_summary(logger)

    logger.success("Example 07 completed!")


if __name__ == "__main__":
    main()

# EOF
