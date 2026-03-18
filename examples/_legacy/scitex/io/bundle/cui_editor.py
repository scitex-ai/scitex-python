#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-13
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/fig/cui_editor.py
"""
Demo: Programmatic Figure Editing (CUI)

Edit figure properties without launching GUI:
- Modify axis limits, labels, titles
- Change styles programmatically
- Save manual overrides to .manual.json

For interactive GUI editing, see gui_editors.py
"""

import json
from pathlib import Path

import scitex as stx
from scitex.dev.plt import PLOTTERS_STX


def create_sample_figure(output_dir: Path, plt, rng) -> Path:
    """Create a sample figure as .plot bundle for editing."""
    plotter = PLOTTERS_STX["stx_line"]
    fig, ax = plotter(plt, rng)

    bundle_path = output_dir / "editable_figure.plot"
    stx.io.save(fig, bundle_path, dpi=150)
    plt.close(fig)

    return bundle_path


def edit_figure_programmatically(bundle_path: Path, logger) -> None:
    """Demonstrate programmatic figure editing via spec manipulation."""

    # Find the JSON spec file in the bundle
    json_files = list(bundle_path.glob("*.json"))
    if not json_files:
        logger.error(f"No JSON spec found in {bundle_path}")
        return

    spec_file = json_files[0]
    logger.info(f"Loading spec from: {spec_file.name}")

    # Load current spec
    with open(spec_file, "r") as f:
        spec = json.load(f)

    # Display current state
    logger.info("Current spec structure:")
    for key in spec.keys():
        logger.info(f"  • {key}")

    # =========================================================================
    # Example 1: Modify axis limits
    # =========================================================================
    logger.info("\n--- Example 1: Modify axis limits ---")

    if "axes" in spec:
        axes = spec["axes"]
        if isinstance(axes, dict):
            # Single axes
            original_xlim = axes.get("xlim", "auto")
            original_ylim = axes.get("ylim", "auto")

            # Set new limits
            axes["xlim"] = [0, 8]  # Restrict x range
            axes["ylim"] = [-1.5, 1.5]  # Expand y range

            logger.info(f"  xlim: {original_xlim} → {axes['xlim']}")
            logger.info(f"  ylim: {original_ylim} → {axes['ylim']}")

    # =========================================================================
    # Example 2: Modify title and labels
    # =========================================================================
    logger.info("\n--- Example 2: Modify title and labels ---")

    if "axes" in spec:
        axes = spec["axes"]
        if isinstance(axes, dict):
            original_title = axes.get("title", "")
            original_xlabel = axes.get("xlabel", "")
            original_ylabel = axes.get("ylabel", "")

            axes["title"] = "Modified Title (Programmatic Edit)"
            axes["xlabel"] = "X Axis (edited)"
            axes["ylabel"] = "Y Axis (edited)"

            logger.info(f"  title: '{original_title}' → '{axes['title']}'")
            logger.info(f"  xlabel: '{original_xlabel}' → '{axes['xlabel']}'")
            logger.info(f"  ylabel: '{original_ylabel}' → '{axes['ylabel']}'")

    # =========================================================================
    # Example 3: Modify grid and style
    # =========================================================================
    logger.info("\n--- Example 3: Modify grid settings ---")

    if "axes" in spec:
        axes = spec["axes"]
        if isinstance(axes, dict):
            axes["grid"] = {"visible": True, "alpha": 0.3, "linestyle": "--"}
            logger.info(f"  grid: enabled with alpha=0.3, linestyle='--'")

    # =========================================================================
    # Save as manual override file
    # =========================================================================
    manual_file = spec_file.with_suffix(".manual.json")

    manual_data = {
        "base_file": spec_file.name,
        "description": "Programmatic edits from cui_editor.py",
        "overrides": {
            "axes": spec.get("axes", {}),
        },
    }

    with open(manual_file, "w") as f:
        json.dump(manual_data, f, indent=2)

    logger.success(f"Saved manual overrides to: {manual_file.name}")

    # Also save the modified spec back
    with open(spec_file, "w") as f:
        json.dump(spec, f, indent=2)

    logger.success(f"Updated spec file: {spec_file.name}")

    # =========================================================================
    # Show how to apply and re-render
    # =========================================================================
    logger.info("\n--- To re-render with changes ---")
    logger.info("Option 1: Load and re-save")
    logger.info(f"  >>> fig, ax = stx.io.load('{bundle_path}')")
    logger.info(f"  >>> stx.io.save(fig, '{bundle_path}')")
    logger.info("")
    logger.info("Option 2: Use GUI editor to preview")
    logger.info(f"  >>> stx.fig.edit('{bundle_path}')")


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrate programmatic figure editing."""
    out = Path(CONFIG.SDIR_OUT)
    rng = rng("cui_editor_demo")

    logger.info("=" * 60)
    logger.info("CUI Figure Editor Demo - Programmatic Editing")
    logger.info("=" * 60)

    # Create sample figure
    logger.info("\nStep 1: Creating sample figure...")
    bundle_path = create_sample_figure(out, plt, rng)
    logger.success(f"Bundle created: {bundle_path}")

    # List bundle contents
    logger.info("\nBundle contents:")
    for f in sorted(bundle_path.iterdir()):
        logger.info(f"  {f.name}")

    # Demonstrate programmatic editing
    logger.info("\nStep 2: Editing figure programmatically...")
    edit_figure_programmatically(bundle_path, logger)

    logger.info("\n" + "=" * 60)
    logger.success("CUI Editor Demo Complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

# EOF
