#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/04_text_and_shapes.py

"""
Example 04: FTS Node Types

Demonstrates:
- Creating bundles with different node types (text, shape, figure)
- Setting node properties (name, bbox_norm, size_mm)
- Container bundles with children
"""

import scitex as stx
from scitex import INJECTED
from scitex.io.bundle import FTS


def create_text_node(out_dir, logger):
    """Create text node bundle."""
    text_bundle = FTS(
        out_dir / "title_text.zip",
        create=True,
        node_type="text",
        name="Main Title",
    )
    text_bundle.node.bbox_norm.x0 = 0.1
    text_bundle.node.bbox_norm.y0 = 0.02
    text_bundle.node.bbox_norm.x1 = 0.9
    text_bundle.node.bbox_norm.y1 = 0.07
    text_bundle.save()

    logger.info(f"Text node saved: {text_bundle.path}")
    logger.info(
        f"  BBox: x0={text_bundle.node.bbox_norm.x0:.2f}, "
        f"y0={text_bundle.node.bbox_norm.y0:.2f}, "
        f"x1={text_bundle.node.bbox_norm.x1:.2f}, "
        f"y1={text_bundle.node.bbox_norm.y1:.2f}"
    )


def create_shape_node(out_dir, logger):
    """Create shape node bundle."""
    shape_bundle = FTS(
        out_dir / "arrow_shape.zip",
        create=True,
        node_type="shape",
        name="Arrow Annotation",
    )
    shape_bundle.node.bbox_norm.x0 = 0.3
    shape_bundle.node.bbox_norm.y0 = 0.4
    shape_bundle.node.bbox_norm.x1 = 0.5
    shape_bundle.node.bbox_norm.y1 = 0.45
    shape_bundle.save()

    logger.info(f"Shape node saved: {shape_bundle.path}")


def create_figure_container(out_dir, logger):
    """Create figure container bundle."""
    figure_bundle = FTS(
        out_dir / "annotated_figure.zip",
        create=True,
        node_type="figure",
        name="Annotated Figure",
        size_mm={"width": 170, "height": 100},
    )
    figure_bundle.node.children = ["title_text", "arrow_shape"]
    figure_bundle.save()

    logger.info(f"Figure saved: {figure_bundle.path}")
    logger.info(f"Children: {figure_bundle.node.children}")


def verify_bundles(out_dir, logger):
    """Reload and verify all bundles."""
    logger.info("\nReloading bundles...")
    for name in ["title_text.zip", "arrow_shape.zip", "annotated_figure.zip"]:
        bundle = FTS(out_dir / name)
        logger.info(f"  {name}: kind={bundle.node.kind}, name={bundle.node.name}")


@stx.session(verbose=False, agg=True)
def main(CONFIG=INJECTED, logger=INJECTED):
    """Create bundles with different node types."""
    logger.info("Example 04: FTS Node Types")

    out_dir = CONFIG["SDIR_OUT"]

    logger.info("Creating text node...")
    create_text_node(out_dir, logger)

    logger.info("Creating shape node...")
    create_shape_node(out_dir, logger)

    logger.info("Creating figure container...")
    create_figure_container(out_dir, logger)

    verify_bundles(out_dir, logger)

    logger.success("Example 04 completed!")


if __name__ == "__main__":
    main()

# EOF
