#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/14_layout_edit_bbox_norm.py

"""
Example 14: Node Bounding Box Editing

Demonstrates:
- bbox_norm stores normalized coordinates (0-1)
- Programmatic layout adjustment
- Position/size modifications persist across save/load
"""

import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, names):
    """Remove existing bundles."""
    for name in names:
        path = out_dir / name
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_initial_plot(plt, out_dir):
    """Create initial plot bundle."""
    x = np.linspace(0, 10, 50)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(x, np.sin(x), linewidth=1.5)
    ax.set_title("Layout Demo")

    bundle_path = out_dir / "layout_edit.zip"
    sio.save(fig, bundle_path)
    plt.close(fig)

    return bundle_path


def log_bbox(bbox, logger, prefix=""):
    """Log bbox values."""
    logger.info(f"{prefix}x0: {bbox.x0:.3f}")
    logger.info(f"{prefix}y0: {bbox.y0:.3f}")
    logger.info(f"{prefix}x1: {bbox.x1:.3f}")
    logger.info(f"{prefix}y1: {bbox.y1:.3f}")
    logger.info(f"{prefix}width: {bbox.width:.3f} (computed)")
    logger.info(f"{prefix}height: {bbox.height:.3f} (computed)")


def inspect_initial_bbox(bundle_path, logger):
    """Inspect initial bbox values."""
    logger.info("\n" + "=" * 60)
    logger.info("INITIAL BOUNDING BOX")
    logger.info("=" * 60)

    bundle = FTS(bundle_path)
    logger.info("Initial bbox_norm:")
    log_bbox(bundle.node.bbox_norm, logger, "  ")

    return bundle


def modify_bbox(bundle, logger):
    """Modify bbox values."""
    logger.info("\n" + "=" * 60)
    logger.info("MODIFYING BOUNDING BOX")
    logger.info("=" * 60)

    bundle.node.bbox_norm.x0 = 0.1
    bundle.node.bbox_norm.y0 = 0.15
    bundle.node.bbox_norm.x1 = 0.9
    bundle.node.bbox_norm.y1 = 0.85

    logger.info("New bbox_norm values:")
    log_bbox(bundle.node.bbox_norm, logger, "  ")

    bundle.save()
    logger.info("\nChanges saved")


def verify_bbox(bundle_path, logger):
    """Verify bbox after reload."""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICATION (after reload)")
    logger.info("=" * 60)

    reloaded = FTS(bundle_path)
    logger.info("Reloaded bbox_norm:")
    log_bbox(reloaded.node.bbox_norm, logger, "  ")


def create_multi_node_layout(out_dir, logger):
    """Create container with positioned children."""
    logger.info("\n" + "=" * 60)
    logger.info("MULTI-NODE LAYOUT")
    logger.info("=" * 60)

    container = FTS(
        out_dir / "layout_container.zip",
        create=True,
        node_type="figure",
        name="Layout Container",
        size_mm={"width": 170, "height": 100},
    )

    child_layouts = [
        {"id": "panel_A", "x": 0.02, "y": 0.05, "w": 0.45, "h": 0.9},
        {"id": "panel_B", "x": 0.52, "y": 0.05, "w": 0.45, "h": 0.9},
    ]

    container.node.children = [c["id"] for c in child_layouts]
    container.save()

    logger.info("Container with child references:")
    logger.info(f"  Children: {container.node.children}")
    for layout in child_layouts:
        logger.info(
            f"  {layout['id']}: x={layout['x']:.2f}, y={layout['y']:.2f}, "
            f"w={layout['w']:.2f}, h={layout['h']:.2f}"
        )


def print_summary(logger):
    """Print key takeaways."""
    logger.info("\n" + "=" * 60)
    logger.info("Key takeaway:")
    logger.info("  - bbox_norm uses normalized coordinates (0-1)")
    logger.info("  - Changes persist after save/load")
    logger.info("  - Layout is stored in node.json")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate bbox_norm editing."""
    logger.info("Example 14: Node Bounding Box Editing")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, ["layout_edit.zip", "layout_container.zip"])

    bundle_path = create_initial_plot(plt, out_dir)
    bundle = inspect_initial_bbox(bundle_path, logger)
    modify_bbox(bundle, logger)
    verify_bbox(bundle_path, logger)
    create_multi_node_layout(out_dir, logger)
    print_summary(logger)

    logger.success("Example 14 completed!")


if __name__ == "__main__":
    main()

# EOF
