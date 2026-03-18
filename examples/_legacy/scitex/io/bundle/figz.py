#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-20
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/figz.py
"""
FTS bundle demonstration with various plot types.

Demonstrates:
1. Creating FTS bundles using scitex.io.save() (kind=plot)
2. Creating composite figures using add_child() (kind=figure)
3. Self-contained bundles with embedded children
4. Bundle structure: canonical/, payload/, artifacts/, children/

Uses PLOTTERS registry from scitex.dev.plt for all plot types.
"""

import shutil

import scitex as stx
import scitex.io as sio
from scitex.io.bundle import FTS
from scitex.dev.plt import PLOTTERS_STX, PLOTTERS_MPL


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """FTS bundle demonstration."""
    logger.info("Starting FTS bundle demo with various plot types")

    sdir = CONFIG["SDIR_OUT"]
    rng = rng("fts_demo")

    # Clean up existing bundles
    panel_names = ["panel_line", "panel_bar", "panel_scatter", "panel_histogram",
                   "panel_errorbar", "panel_boxplot", "panel_contour", "panel_heatmap",
                   "panel_fill", "panel_barh", "panel_violin",
                   "Figure1", "Figure2"]
    for name in panel_names:
        for ext in [".zip"]:
            path = sdir / f"{name}{ext}"
            if path.exists():
                shutil.rmtree(path) if path.is_dir() else path.unlink()

    # -------------------------------------------------------------------------
    # Part 1: Create individual FTS bundles with various plot types (kind=plot)
    # -------------------------------------------------------------------------
    logger.info("Creating plot bundles (kind=plot)")

    # Select a variety of plot types from registries
    plot_configs = [
        (PLOTTERS_STX["stx_line"], "panel_line", "A"),
        (PLOTTERS_STX["stx_bar"], "panel_bar", "B"),
        (PLOTTERS_STX["stx_scatter"], "panel_scatter", "C"),
        (PLOTTERS_MPL["mpl_hist"], "panel_histogram", "D"),
        (PLOTTERS_STX["stx_errorbar"], "panel_errorbar", "E"),
        (PLOTTERS_STX["stx_boxplot"], "panel_boxplot", "F"),
        (PLOTTERS_STX["stx_contour"], "panel_contour", "G"),
        (PLOTTERS_STX["stx_heatmap"], "panel_heatmap", "H"),
        (PLOTTERS_STX["stx_fill_between"], "panel_fill", "I"),
        (PLOTTERS_MPL["mpl_barh"], "panel_barh", "J"),
        (PLOTTERS_STX["stx_violin"], "panel_violin", "K"),
    ]

    panels = {}
    for plot_func, name, panel_id in plot_configs:
        try:
            fig, ax = plot_func(plt, rng)
            panel_path = sdir / f"{name}.zip"
            sio.save(fig, panel_path, dpi=150)
            plt.close(fig)
            panels[panel_id] = panel_path
            logger.info(f"  Created {name}.zip (Panel {panel_id})")
        except Exception as e:
            logger.warning(f"  Failed {name}: {e}")

    logger.success(f"Created {len(panels)} panel bundles")

    # -------------------------------------------------------------------------
    # Part 2: Create composite figure using add_child() (kind=figure)
    # -------------------------------------------------------------------------
    logger.info("Creating Figure1 (3 panels embedded)")

    container = FTS(
        sdir / "Figure1.zip",
        create=True,
        kind="figure",  # Composite kind - can have children
        name="Figure 1",
        size_mm={"width": 180, "height": 60},
    )

    # Add children with positions using add_child()
    # This embeds the child bundles into the children/ directory
    if "A" in panels:
        container.add_child(panels["A"], row=0, col=0, label="A")
    if "B" in panels:
        container.add_child(panels["B"], row=0, col=1, label="B")
    if "C" in panels:
        container.add_child(panels["C"], row=0, col=2, label="C")

    container.theme = {
        "mode": "light",
        "figure_title": {
            "text": "Multi-Panel Figure",
            "prefix": "Figure",
            "number": 1,
        },
    }
    container.save(render=False)  # Fast save without rendering

    logger.info(f"Container created with {len(container.node.children)} embedded children")

    # Reload and verify
    loaded = FTS(sdir / "Figure1.zip")
    logger.info(f"Loaded figure: {loaded.node.name}, kind={loaded.node.kind}")
    logger.info(f"Children: {loaded.node.children}")

    # Load embedded children
    children = loaded.load_children()
    logger.info(f"Loaded {len(children)} embedded children from ZIP")

    logger.success("Figure1.zip created and verified")

    # -------------------------------------------------------------------------
    # Part 3: Create larger composite figure with custom configuration
    # -------------------------------------------------------------------------
    logger.info("Creating Figure2 (6 panels, 2x3 grid)")

    container2 = FTS(
        sdir / "Figure2.zip",
        create=True,
        kind="figure",
        name="Comprehensive Plot Type Demo",
        size_mm={"width": 180, "height": 120},
    )

    # Add panels D-I in 2x3 grid using add_child()
    panel_ids = ["D", "E", "F", "G", "H", "I"]
    for i, panel_id in enumerate(panel_ids):
        if panel_id in panels:
            row = i // 3
            col = i % 3
            container2.add_child(panels[panel_id], row=row, col=col, label=panel_id)

    container2.theme = {
        "mode": "light",
        "figure_title": {
            "text": "Comprehensive Plot Type Demo",
            "prefix": "Figure",
            "number": 2,
        },
        "caption": {
            "text": "Demonstration of various plot types.",
            "panels": [
                {"label": k, "description": f"Panel {k}"}
                for k in panel_ids if k in panels
            ],
        },
    }
    container2.save(render=False)

    logger.success("Figure2.zip created with embedded children")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    logger.info("=" * 50)
    logger.info("Bundle Demo Summary:")
    logger.info(f"  Output: {sdir}")
    logger.info(f"  Panels (kind=plot): {len(panels)}")
    logger.info("  Figures (kind=figure): 2")
    logger.info("  Bundle structure: canonical/, payload/, artifacts/, children/")
    logger.success("Demo completed")

    return 0


if __name__ == "__main__":
    main()

# EOF
