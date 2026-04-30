#!/usr/bin/env python3
# Timestamp: "2025-12-14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/fig/io/_bundle.py

"""
SciTeX Figure Bundle I/O - Figure-specific bundle operations.

Handles:
    - Figure specification validation
    - Panel composition and layout
    - Nested .plot bundle management
    - Export file handling
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

__all__ = [
    "validate_figure_spec",
    "load_figure_bundle",
    "save_figure_bundle",
    "FIGURE_SCHEMA_SPEC",
]

# Schema specification for .figure bundles
FIGURE_SCHEMA_SPEC = {
    "name": "scitex.canvas.figure",
    "version": "1.0.0",
    "required_fields": ["schema"],
    "optional_fields": ["figure", "panels", "notations"],
}


def validate_figure_spec(spec: Dict[str, Any]) -> List[str]:
    """Validate .figure-specific fields.

    Args:
        spec: The specification dictionary to validate.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []

    if "panels" in spec:
        panels = spec["panels"]
        if not isinstance(panels, list):
            errors.append("'panels' must be a list")
        else:
            for i, panel in enumerate(panels):
                if not isinstance(panel, dict):
                    errors.append(f"panels[{i}] must be a dictionary")
                    continue
                if "id" not in panel:
                    errors.append(f"panels[{i}].id is required")

    if "figure" in spec:
        figure = spec["figure"]
        if not isinstance(figure, dict):
            errors.append("'figure' must be a dictionary")

    return errors


def load_figure_bundle(bundle_dir: Path) -> Dict[str, Any]:
    """Load .figure bundle contents from directory.

    Supports both:
    - New format: spec.json + style.json (separate semantic/appearance)
    - Legacy format: {basename}.json (embedded styles)

    Args:
        bundle_dir: Path to the bundle directory.

    Returns:
        Dictionary with loaded bundle contents:
        - spec: Figure specification (semantic)
        - style: Figure style (appearance)
        - plots: Dict of nested plot bundles
        - basename: Base filename
    """
    result = {}
    bundle_dir = Path(bundle_dir)

    # Determine basename from directory name
    basename = bundle_dir.stem.replace(".figure", "")
    result["basename"] = basename

    # Try to load spec.json (new format) first
    spec_file = bundle_dir / "spec.json"
    if spec_file.exists():
        with open(spec_file) as f:
            result["spec"] = json.load(f)
    else:
        # Fallback to {basename}.json (legacy format)
        legacy_file = bundle_dir / f"{basename}.json"
        if legacy_file.exists():
            with open(legacy_file) as f:
                result["spec"] = json.load(f)
        else:
            # Try any .json file
            for f in bundle_dir.glob("*.json"):
                if not f.name.startswith(".") and f.name != "style.json":
                    with open(f) as fp:
                        result["spec"] = json.load(fp)
                    break
            else:
                result["spec"] = None

    # Load style.json if exists
    style_file = bundle_dir / "style.json"
    if style_file.exists():
        with open(style_file) as f:
            result["style"] = json.load(f)
    else:
        # Extract from embedded styles in spec (legacy)
        if result.get("spec"):
            figure = result["spec"].get("figure", {})
            if "styles" in figure:
                result["style"] = figure["styles"]
            else:
                result["style"] = {}
        else:
            result["style"] = {}

    # Load nested .plot bundles
    result["plots"] = {}

    # Load from .plot directories
    for plot_dir in bundle_dir.glob("*.plot"):
        plot_name = plot_dir.stem.replace(".plot", "")
        from scitex.io.bundle import load

        result["plots"][plot_name] = load(plot_dir)

    # Load from .plot.zip files
    for plot_zip in bundle_dir.glob("*.plot.zip"):
        if plot_zip.is_file():
            plot_name = plot_zip.stem.replace(".plot", "")
            from scitex.io.bundle import load

            result["plots"][plot_name] = load(plot_zip)

    return result


def save_figure_bundle(data: Dict[str, Any], dir_path: Path) -> None:
    """Save .figure bundle contents to directory.

    Structure:
        figure.figure/
            spec.json              # Figure-level specification
            style.json             # Figure-level style (optional)
            exports/               # Figure-level exports
                figure.png
                figure.svg
                figure_hitmap.png
                figure_overview.png
            cache/                 # Figure-level cache
                geometry_px.json   # Combined geometry for all panels
                render_manifest.json
            panels/                # Nested panel bundles (or *.plot at root)
                A.plot/
                B.plot/
            README.md

    Args:
        data: Bundle data dictionary.
        dir_path: Path to the bundle directory.
    """
    import logging

    logger = logging.getLogger("scitex")

    # Get basename from directory name (e.g., "Figure1" from "Figure1.figure")
    basename = dir_path.stem.replace(".figure", "")

    # Create directories
    exports_dir = dir_path / "exports"
    cache_dir = dir_path / "cache"
    exports_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Split spec into spec.json (semantic) and style.json (appearance)
    spec = data.get("spec", {})
    style = data.get("style", {})

    # Extract style from spec.figure.styles if not provided separately
    figure_data = spec.get("figure", {})
    if not style and "styles" in figure_data:
        style = figure_data.get("styles", {})

    # Build clean spec (semantic data only)
    clean_spec = {
        "schema": spec.get(
            "schema", {"name": "scitex.canvas.figure", "version": "1.0.0"}
        ),
        "figure": {
            "id": figure_data.get("id", "figure"),
            "title": figure_data.get("title", ""),
            "caption": figure_data.get("caption", ""),
        },
        "panels": spec.get("panels", []),
    }
    if "notations" in spec:
        clean_spec["notations"] = spec["notations"]

    # Build style (appearance data)
    figure_style = {
        "schema": {"name": "scitex.canvas.style", "version": "1.0.0"},
        "size": style.get("size", {"width_mm": 180, "height_mm": 120}),
        "background": style.get("background", "#ffffff"),
        "theme": style.get("theme", {"mode": "light"}),
        "panel_labels": style.get(
            "panel_labels",
            {
                "visible": True,
                "fontsize": 12,
                "fontweight": "bold",
                "position": "top-left",
            },
        ),
    }

    # Save spec.json (semantic)
    spec_file = dir_path / "spec.json"
    with open(spec_file, "w") as f:
        json.dump(clean_spec, f, indent=2)

    # Save style.json (appearance)
    style_file = dir_path / "style.json"
    with open(style_file, "w") as f:
        json.dump(figure_style, f, indent=2)

    # Also save as {basename}.json for backward compatibility (full spec with embedded style)
    compat_spec = dict(clean_spec)
    compat_spec["figure"]["styles"] = {
        "size": figure_style["size"],
        "background": figure_style["background"],
    }
    compat_spec_file = dir_path / f"{basename}.json"
    with open(compat_spec_file, "w") as f:
        json.dump(compat_spec, f, indent=2)

    # Save exports to exports/ directory
    _save_figure_exports(data, exports_dir, spec, basename)

    # Copy nested .plot bundles directly (preserving all files)
    if "plots" in data:
        _copy_nested_plot_bundles(data["plots"], dir_path)

    # Generate composed figure in exports/ (Figure1.png, Figure1.svg)
    try:
        _generate_composed_figure(dir_path, spec, basename)
    except Exception as e:
        logger.debug(f"Could not generate composed figure: {e}")

    # Generate figure overview in exports/
    try:
        _generate_figure_overview(dir_path, spec, data, basename)
    except Exception as e:
        logger.debug(f"Could not generate figure overview: {e}")

    # Generate figure-level geometry cache
    try:
        _generate_figure_geometry_cache(dir_path, spec, basename)
    except Exception as e:
        logger.debug(f"Could not generate figure geometry cache: {e}")

    # Generate README.md
    try:
        _generate_figure_readme(dir_path, spec, data, basename)
    except Exception as e:
        logger.debug(f"Could not generate figure README: {e}")


def _save_figure_exports(
    data: Dict[str, Any], exports_dir: Path, spec: Dict, basename: str
) -> None:
    """Save figure-level export files to exports/ directory.

    Args:
        data: Bundle data containing PNG/SVG/PDF bytes or paths.
        exports_dir: Path to exports/ directory.
        spec: Figure specification.
        basename: Base filename for exports.
    """
    for fmt in ["png", "svg", "pdf"]:
        if fmt not in data:
            continue

        out_file = exports_dir / f"{basename}.{fmt}"
        export_data = data[fmt]

        if isinstance(export_data, bytes):
            with open(out_file, "wb") as f:
                f.write(export_data)
        elif isinstance(export_data, (str, Path)) and Path(export_data).exists():
            shutil.copy(export_data, out_file)

        # Embed metadata into PNG and PDF files
        if out_file.exists() and spec:
            try:
                _embed_metadata_in_export(out_file, spec, fmt)
            except Exception as e:
                import logging

                logging.getLogger("scitex").debug(
                    f"Could not embed metadata in {out_file}: {e}"
                )


def _save_exports(
    data: Dict[str, Any], dir_path: Path, spec: Dict, basename: str = "figure"
) -> None:
    """Save export files (PNG, SVG, PDF) with embedded metadata. (Legacy - root level)"""
    for fmt in ["png", "svg", "pdf"]:
        if fmt not in data:
            continue

        out_file = dir_path / f"{basename}.{fmt}"
        export_data = data[fmt]

        if isinstance(export_data, bytes):
            with open(out_file, "wb") as f:
                f.write(export_data)
        elif isinstance(export_data, (str, Path)) and Path(export_data).exists():
            shutil.copy(export_data, out_file)

        # Embed metadata into PNG and PDF files
        if out_file.exists() and spec:
            try:
                _embed_metadata_in_export(out_file, spec, fmt)
            except Exception as e:
                import logging

                logging.getLogger("scitex").debug(
                    f"Could not embed metadata in {out_file}: {e}"
                )


def _copy_nested_plot_bundles(plots: Dict[str, Any], dir_path: Path) -> None:
    """Copy nested .plot bundles directly, preserving all files.

    Args:
        plots: Dict mapping panel IDs to either:
            - source_path: Path to existing .plot directory or .plot.zip
            - bundle_data: Dict with spec/data (will use save_bundle)
        dir_path: Target figure directory.
    """
    for panel_id, plot_source in plots.items():
        if isinstance(plot_source, (str, Path)):
            # Direct copy from source path
            source_path = Path(plot_source)

            if source_path.is_dir() and str(source_path).endswith(".plot"):
                # Source is .plot directory - copy as directory
                target_path = dir_path / f"{panel_id}.plot"
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.copytree(source_path, target_path)

            elif source_path.is_file() and str(source_path).endswith(".plot.zip"):
                # Source is .plot.zip file - copy as zip file (preserving zip format)
                target_path = dir_path / f"{panel_id}.plot.zip"
                if target_path.exists():
                    target_path.unlink()
                shutil.copy2(source_path, target_path)

            elif source_path.exists():
                # Unknown format - try to copy as directory
                target_path = dir_path / f"{panel_id}.plot"
                if source_path.is_dir():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)

        elif isinstance(plot_source, dict):
            # Check if it has source_path for direct copy
            if "source_path" in plot_source:
                source_path = Path(plot_source["source_path"])
                if source_path.is_file() and str(source_path).endswith(".plot.zip"):
                    # .plot.zip file
                    target_path = dir_path / f"{panel_id}.plot.zip"
                    if target_path.exists():
                        target_path.unlink()
                    shutil.copy2(source_path, target_path)
                elif source_path.exists() and source_path.is_dir():
                    # .plot directory
                    target_path = dir_path / f"{panel_id}.plot"
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
            else:
                # Fallback to save (will lose images)
                from scitex.io.bundle import BundleType, save

                target_path = dir_path / f"{panel_id}.plot"
                save(plot_source, target_path, bundle_type=BundleType.PLOT)


def _generate_figure_overview(
    dir_path: Path, spec: Dict, data: Dict, basename: str
) -> None:
    """Generate overview image for figure bundle showing panels with hitmaps, overlays, and bboxes.

    Args:
        dir_path: Bundle directory path.
        spec: Bundle specification.
        data: Bundle data dictionary.
        basename: Base filename for bundle files.
    """
    import tempfile
    import warnings
    import zipfile

    import matplotlib.gridspec as gridspec
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    # Find all panel bundles (both .plot directories and .plot.zip files)
    panel_dirs = []
    temp_dirs_to_cleanup = []

    for item in dir_path.iterdir():
        if item.is_dir() and str(item).endswith(".plot"):
            panel_dirs.append(item)
        elif item.is_file() and str(item).endswith(".plot.zip"):
            # Extract .plot.zip to temp directory for overview generation
            temp_dir = tempfile.mkdtemp(prefix=f"scitex_overview_{item.stem}_")
            temp_dirs_to_cleanup.append(temp_dir)
            with zipfile.ZipFile(item, "r") as zf:
                zf.extractall(temp_dir)
            # Find the extracted .plot directory
            extracted = Path(temp_dir)
            for subitem in extracted.iterdir():
                if subitem.is_dir() and str(subitem).endswith(".plot"):
                    panel_dirs.append(subitem)
                    break
            else:
                # Use temp dir directly if no .plot subfolder
                panel_dirs.append(extracted)

    panel_dirs = sorted(panel_dirs, key=lambda x: x.name)
    n_panels = len(panel_dirs)

    if n_panels == 0:
        return

    # Create figure with 2 rows per panel:
    # Row 1: Plot | Hitmap | Overlay
    # Row 2: Bboxes | (empty) | (empty)
    fig_width = 15
    fig_height = 6 * n_panels + 1
    fig = plt.figure(figsize=(fig_width, fig_height), facecolor="white")

    # Title
    title = spec.get("figure", {}).get("title", basename)
    fig.suptitle(f"Figure Overview: {title}", fontsize=14, fontweight="bold", y=0.99)

    # Create gridspec - 2 rows per panel, 3 columns
    gs = gridspec.GridSpec(
        n_panels * 2,
        3,
        figure=fig,
        hspace=0.3,
        wspace=0.15,
        height_ratios=[1, 1] * n_panels,
    )

    # Add each panel
    for idx, panel_dir in enumerate(panel_dirs):
        panel_id = panel_dir.stem.replace(".plot", "")
        row_base = idx * 2  # Two rows per panel

        # Find PNG in panel directory (check exports/ first for layered format, then root)
        png_files = list(panel_dir.glob("exports/*.png"))
        if not png_files:
            png_files = list(panel_dir.glob("*.png"))
        main_pngs = [
            f
            for f in png_files
            if "_hitmap" not in f.name and "_overview" not in f.name
        ]

        # Find hitmap PNG
        hitmap_files = list(panel_dir.glob("exports/*_hitmap.png"))
        if not hitmap_files:
            hitmap_files = list(panel_dir.glob("*_hitmap.png"))

        # Load geometry for bboxes
        geometry_data = {}
        geometry_path = panel_dir / "cache" / "geometry_px.json"
        if geometry_path.exists():
            with open(geometry_path) as f:
                geometry_data = json.load(f)

        # === Row 1: Plot | Hitmap | Overlay ===
        # Left subplot: main image
        ax_main = fig.add_subplot(gs[row_base, 0])
        ax_main.set_title(f"Panel {panel_id}", fontweight="bold", fontsize=11)

        main_img = None
        if main_pngs:
            main_img = Image.open(main_pngs[0])
            ax_main.imshow(main_img)
        else:
            ax_main.text(
                0.5,
                0.5,
                "No image",
                ha="center",
                va="center",
                transform=ax_main.transAxes,
            )
        ax_main.axis("off")

        # Middle subplot: hitmap
        ax_hitmap = fig.add_subplot(gs[row_base, 1])
        ax_hitmap.set_title(f"Hitmap {panel_id}", fontweight="bold", fontsize=11)

        hitmap_img = None
        if hitmap_files:
            hitmap_img = Image.open(hitmap_files[0])
            ax_hitmap.imshow(hitmap_img)
        else:
            ax_hitmap.text(
                0.5,
                0.5,
                "No hitmap",
                ha="center",
                va="center",
                transform=ax_hitmap.transAxes,
            )
        ax_hitmap.axis("off")

        # Right subplot: overlay
        ax_overlay = fig.add_subplot(gs[row_base, 2])
        ax_overlay.set_title(f"Overlay {panel_id}", fontweight="bold", fontsize=11)

        if main_img is not None:
            ax_overlay.imshow(main_img)
            if hitmap_img is not None:
                hitmap_rgba = hitmap_img.convert("RGBA")
                hitmap_array = np.array(hitmap_rgba)
                # Create semi-transparent overlay
                hitmap_array[:, :, 3] = (hitmap_array[:, :, 3] * 0.5).astype(np.uint8)
                ax_overlay.imshow(hitmap_array, alpha=0.5)
        else:
            ax_overlay.text(
                0.5,
                0.5,
                "No overlay",
                ha="center",
                va="center",
                transform=ax_overlay.transAxes,
            )
        ax_overlay.axis("off")

        # === Row 2: Bboxes ===
        ax_bboxes = fig.add_subplot(gs[row_base + 1, 0])
        ax_bboxes.set_title(f"Bboxes {panel_id}", fontweight="bold", fontsize=11)

        if main_img is not None:
            ax_bboxes.imshow(main_img)
            # Draw bboxes from geometry
            _draw_bboxes_from_geometry(ax_bboxes, geometry_data)
        else:
            ax_bboxes.text(
                0.5,
                0.5,
                "No image",
                ha="center",
                va="center",
                transform=ax_bboxes.transAxes,
            )
        ax_bboxes.axis("off")

        # Info panel
        ax_info = fig.add_subplot(gs[row_base + 1, 1:])
        ax_info.set_title(f"Info {panel_id}", fontweight="bold", fontsize=11)
        ax_info.axis("off")

        # Show spec/style summary
        spec_path = panel_dir / "spec.json"
        style_path = panel_dir / "style.json"
        info_text = ""

        if spec_path.exists():
            with open(spec_path) as f:
                spec_data = json.load(f)
            info_text += f"Axes: {len(spec_data.get('axes', []))}\n"
            info_text += f"Traces: {len(spec_data.get('traces', []))}\n"

        if style_path.exists():
            with open(style_path) as f:
                style_data = json.load(f)
            size = style_data.get("size", {})
            info_text += f"Size: {size.get('width_mm', 0):.1f} × {size.get('height_mm', 0):.1f} mm\n"
            info_text += f"Theme: {style_data.get('theme', {}).get('mode', 'light')}\n"

        manifest_path = panel_dir / "cache" / "render_manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest_data = json.load(f)
            info_text += f"DPI: {manifest_data.get('dpi', 300)}\n"
            render_px = manifest_data.get("render_px", [0, 0])
            info_text += f"Pixels: {render_px[0]} × {render_px[1]}\n"

        ax_info.text(
            0.02,
            0.98,
            info_text,
            transform=ax_info.transAxes,
            fontsize=10,
            fontfamily="monospace",
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    # Save overview to exports/ directory
    exports_dir = dir_path / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    overview_path = exports_dir / f"{basename}_overview.png"
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*tight_layout.*")
        fig.savefig(overview_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Cleanup temp directories
    for temp_dir in temp_dirs_to_cleanup:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


def _draw_bboxes_from_geometry(ax, geometry_data: Dict) -> None:
    """Draw bboxes from geometry data on an axes.

    Args:
        ax: Matplotlib axes.
        geometry_data: Geometry data dictionary.
    """

    colors = ["red", "blue", "green", "orange", "purple", "cyan"]
    selectable = geometry_data.get("selectable_regions", {})

    for ax_idx, ax_region in enumerate(selectable.get("axes", [])):
        color = colors[ax_idx % len(colors)]

        # Title bbox
        if "title" in ax_region:
            bbox = ax_region["title"].get("bbox_px", [])
            if len(bbox) == 4:
                _draw_single_bbox(ax, bbox, color, "title")

        # xlabel bbox
        if "xlabel" in ax_region:
            bbox = ax_region["xlabel"].get("bbox_px", [])
            if len(bbox) == 4:
                _draw_single_bbox(ax, bbox, color, "xlabel")

        # ylabel bbox
        if "ylabel" in ax_region:
            bbox = ax_region["ylabel"].get("bbox_px", [])
            if len(bbox) == 4:
                _draw_single_bbox(ax, bbox, color, "ylabel")

        # xaxis spine
        if "xaxis" in ax_region and "spine" in ax_region["xaxis"]:
            bbox = ax_region["xaxis"]["spine"].get("bbox_px", [])
            if len(bbox) == 4:
                _draw_single_bbox(ax, bbox, "gray", "xaxis", lw=1)

        # yaxis spine
        if "yaxis" in ax_region and "spine" in ax_region["yaxis"]:
            bbox = ax_region["yaxis"]["spine"].get("bbox_px", [])
            if len(bbox) == 4:
                _draw_single_bbox(ax, bbox, "gray", "yaxis", lw=1)

        # legend bbox
        if "legend" in ax_region:
            bbox = ax_region["legend"].get("bbox_px", [])
            if len(bbox) == 4:
                _draw_single_bbox(ax, bbox, "magenta", "legend")


def _draw_single_bbox(ax, bbox: List, color: str, label: str, lw: int = 2) -> None:
    """Draw a single bbox rectangle on axes.

    Args:
        ax: Matplotlib axes.
        bbox: [x0, y0, x1, y1] bounding box (corner coordinates).
        color: Rectangle color.
        label: Label text.
        lw: Line width.
    """
    import matplotlib.patches as patches

    # bbox is [x0, y0, x1, y1] format
    x0, y0, x1, y1 = bbox
    width = x1 - x0
    height = y1 - y0
    rect = patches.Rectangle(
        (x0, y0), width, height, linewidth=lw, edgecolor=color, facecolor="none"
    )
    ax.add_patch(rect)
    # Add label
    ax.text(x0 + 2, y0 + height / 2, label, fontsize=6, color=color, fontweight="bold")


def _generate_composed_figure(dir_path: Path, spec: Dict, basename: str) -> None:
    """Generate composed figure from panel images.

    Composes all panel PNG images into a single figure based on the layout
    specified in the figz spec.

    Args:
        dir_path: Bundle directory path.
        spec: Bundle specification with panel layout.
        basename: Base filename for exports.
    """

    from PIL import Image

    exports_dir = dir_path / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    # Load style from style.json if exists, else from spec
    style_file = dir_path / "style.json"
    if style_file.exists():
        with open(style_file) as f:
            style = json.load(f)
        size = style.get("size", {})
        background = style.get("background", "#ffffff")
    else:
        # Fallback to embedded styles in spec
        figure = spec.get("figure", {})
        styles = figure.get("styles", {})
        size = styles.get("size", {})
        background = styles.get("background", "#ffffff")

    fig_width_mm = size.get("width_mm", 180)
    fig_height_mm = size.get("height_mm", 120)

    # Use 300 DPI for composition
    dpi = 300
    mm_to_inch = 1 / 25.4
    fig_width_px = int(fig_width_mm * mm_to_inch * dpi)
    fig_height_px = int(fig_height_mm * mm_to_inch * dpi)

    # Create canvas
    canvas = Image.new("RGB", (fig_width_px, fig_height_px), background)

    # Get panels from spec
    panels = spec.get("panels", [])

    for panel in panels:
        panel_id = panel.get("id", "")
        plot_ref = panel.get("plot", "")

        # Find the panel's plot bundle
        if plot_ref.endswith(".plot"):
            panel_dir = dir_path / plot_ref
        else:
            panel_dir = dir_path / f"{panel_id}.plot"

        if not panel_dir.exists():
            continue

        # Find panel PNG in exports/
        panel_png = None
        exports_subdir = panel_dir / "exports"
        if exports_subdir.exists():
            for png_file in exports_subdir.glob("*.png"):
                if "_hitmap" not in png_file.name and "_overview" not in png_file.name:
                    panel_png = png_file
                    break

        # Fallback: look in panel root
        if not panel_png:
            for png_file in panel_dir.glob("*.png"):
                if "_hitmap" not in png_file.name and "_overview" not in png_file.name:
                    panel_png = png_file
                    break

        if not panel_png or not panel_png.exists():
            continue

        # Load panel image
        panel_img = Image.open(panel_png)

        # Get panel position and size from spec
        pos = panel.get("position", {})
        panel_size = panel.get("size", {})

        x_mm = pos.get("x_mm", 0)
        y_mm = pos.get("y_mm", 0)
        width_mm = panel_size.get("width_mm", 80)
        height_mm = panel_size.get("height_mm", 68)

        # Convert to pixels
        x_px = int(x_mm * mm_to_inch * dpi)
        y_px = int(y_mm * mm_to_inch * dpi)
        target_width = int(width_mm * mm_to_inch * dpi)
        target_height = int(height_mm * mm_to_inch * dpi)

        # Resize panel to fit
        panel_img = panel_img.resize(
            (target_width, target_height), Image.Resampling.LANCZOS
        )

        # Convert to RGB if necessary (for transparent PNGs)
        if panel_img.mode == "RGBA":
            # Create white background
            bg = Image.new("RGB", panel_img.size, background)
            bg.paste(panel_img, mask=panel_img.split()[3])
            panel_img = bg
        elif panel_img.mode != "RGB":
            panel_img = panel_img.convert("RGB")

        # Paste onto canvas
        canvas.paste(panel_img, (x_px, y_px))

    # Save composed figure
    png_path = exports_dir / f"{basename}.png"
    canvas.save(png_path, "PNG", dpi=(dpi, dpi))

    # Also save as SVG (embed PNG in SVG for now)
    svg_path = exports_dir / f"{basename}.svg"
    svg_width_in = fig_width_mm * mm_to_inch
    svg_height_in = fig_height_mm * mm_to_inch

    # Create simple SVG wrapper with embedded image
    import base64

    with open(png_path, "rb") as f:
        png_b64 = base64.b64encode(f.read()).decode("utf-8")

    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{fig_width_px}" height="{fig_height_px}"
     viewBox="0 0 {fig_width_px} {fig_height_px}">
  <image width="{fig_width_px}" height="{fig_height_px}"
         xlink:href="data:image/png;base64,{png_b64}"/>
</svg>"""

    with open(svg_path, "w") as f:
        f.write(svg_content)


def _generate_figure_geometry_cache(dir_path: Path, spec: Dict, basename: str) -> None:
    """Generate figure-level geometry cache combining all panel geometries.

    Creates:
        cache/geometry_px.json - Combined geometry for all panels
        cache/render_manifest.json - Figure-level render metadata

    Args:
        dir_path: Bundle directory path.
        spec: Bundle specification.
        basename: Base filename for bundle files.
    """
    import tempfile
    import zipfile
    from datetime import datetime

    cache_dir = dir_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Collect geometry from all panel bundles
    combined_geometry = {
        "figure_id": basename,
        "panels": {},
        "generated_at": datetime.now().isoformat(),
    }

    # Find all panel bundles (both .plot directories and .plot.zip files)
    panel_sources = []
    temp_dirs_to_cleanup = []

    for item in dir_path.iterdir():
        if item.is_dir() and str(item).endswith(".plot"):
            panel_sources.append((item.stem.replace(".plot", ""), item))
        elif item.is_file() and str(item).endswith(".plot.zip"):
            # Extract .plot.zip to temp directory
            temp_dir = tempfile.mkdtemp(prefix=f"scitex_geom_{item.stem}_")
            temp_dirs_to_cleanup.append(temp_dir)
            with zipfile.ZipFile(item, "r") as zf:
                zf.extractall(temp_dir)
            extracted = Path(temp_dir)
            for subitem in extracted.iterdir():
                if subitem.is_dir() and str(subitem).endswith(".plot"):
                    panel_sources.append((item.stem, subitem))
                    break
            else:
                panel_sources.append((item.stem, extracted))

    panel_sources = sorted(panel_sources, key=lambda x: x[0])

    for panel_id, panel_dir in panel_sources:
        # Load panel geometry
        panel_geometry_path = panel_dir / "cache" / "geometry_px.json"
        if panel_geometry_path.exists():
            with open(panel_geometry_path) as f:
                panel_geometry = json.load(f)
            combined_geometry["panels"][panel_id] = panel_geometry

    # Add panel positions from spec
    panels_spec = spec.get("panels", [])
    for panel in panels_spec:
        panel_id = panel.get("id")
        if panel_id and panel_id in combined_geometry["panels"]:
            combined_geometry["panels"][panel_id]["position_mm"] = panel.get(
                "position", {}
            )
            combined_geometry["panels"][panel_id]["size_mm"] = panel.get("size", {})

    # Save combined geometry
    geometry_path = cache_dir / "geometry_px.json"
    with open(geometry_path, "w") as f:
        json.dump(combined_geometry, f, indent=2)

    # Generate render manifest
    figure_styles = spec.get("figure", {}).get("styles", {})
    size = figure_styles.get("size", {})

    manifest = {
        "figure_id": basename,
        "generated_at": datetime.now().isoformat(),
        "size_mm": [size.get("width_mm", 0), size.get("height_mm", 0)],
        "panels_count": len(panel_sources),
        "schema": spec.get("schema", {}),
    }

    manifest_path = cache_dir / "render_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Cleanup temp directories
    for temp_dir in temp_dirs_to_cleanup:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


def _embed_metadata_in_export(file_path: Path, spec: Dict[str, Any], fmt: str) -> None:
    """Embed bundle spec metadata into exported image files."""
    from scitex.io._metadata import embed_metadata

    embed_data = {
        "scitex_bundle": True,
        "schema": spec.get("schema", {}),
    }

    for key in ["figure", "panels", "notations"]:
        if key in spec:
            embed_data[key] = spec[key]

    if fmt in ("png", "pdf"):
        embed_metadata(str(file_path), embed_data)


def _generate_figure_readme(
    dir_path: Path, spec: Dict, data: Dict, basename: str
) -> None:
    """Generate a dynamic README.md for figure bundle.

    Args:
        dir_path: Bundle directory path.
        spec: Bundle specification.
        data: Bundle data dictionary.
        basename: Base filename for bundle files.
    """
    from datetime import datetime

    # Extract figure info
    figure = spec.get("figure", {})
    title = figure.get("title", basename)
    caption = figure.get("caption", "")

    # Load style from style.json if exists, else from spec.figure.styles
    style_file = dir_path / "style.json"
    if style_file.exists():
        with open(style_file) as f:
            style = json.load(f)
        size = style.get("size", {})
        background = style.get("background", "#ffffff")
    else:
        styles = figure.get("styles", {})
        size = styles.get("size", {})
        background = styles.get("background", "#ffffff")

    width_mm = size.get("width_mm", 0)
    height_mm = size.get("height_mm", 0)

    # Count panels
    panels = spec.get("panels", [])
    n_panels = len(panels)

    # Find panel directories
    panel_dirs = sorted(dir_path.glob("*.plot"))

    # Build panel table
    panel_rows = ""
    for panel in panels:
        panel_id = panel.get("id", "?")
        label = panel.get("label", panel_id)
        plot_ref = panel.get("plot", "")
        pos = panel.get("position", {})
        panel_size = panel.get("size", {})
        panel_rows += f"| {label} | {plot_ref} | ({pos.get('x_mm', 0)}, {pos.get('y_mm', 0)}) | {panel_size.get('width_mm', 0)} × {panel_size.get('height_mm', 0)} mm |\n"

    # Build panel directory list
    panel_dir_list = ""
    for pd in panel_dirs:
        panel_dir_list += f"│   ├── {pd.name}/\n"

    readme_content = f"""# {basename}.figure

> SciTeX Figure Bundle - Auto-generated README

## Overview

![Figure Overview](exports/{basename}_overview.png)

## Bundle Structure

```
{basename}.figure/
├── spec.json              # Figure specification (semantic: what to draw)
├── style.json             # Figure style (appearance: how it looks)
├── {basename}.json        # Combined spec+style
├── exports/               # Figure-level exports
│   ├── {basename}.png          # Rendered figure (raster)
│   ├── {basename}.svg          # Rendered figure (vector)
│   └── {basename}_overview.png # Visual summary with hitmaps
├── cache/                 # Figure-level cache (regenerable)
│   ├── geometry_px.json        # Combined geometry for all panels
│   └── render_manifest.json    # Render metadata
{panel_dir_list}└── README.md              # This file
```

## Figure Information

| Property | Value |
|----------|-------|
| Title | {title or "(none)"} |
| Panels | {n_panels} |
| Size | {width_mm:.1f} × {height_mm:.1f} mm |
| Background | `{background}` |

{f"**Caption**: {caption}" if caption else ""}

## Panel Layout

| Label | Plot Bundle | Position (x, y) | Size |
|-------|-------------|-----------------|------|
{panel_rows}

## Nested Bundles

Each panel is stored as a separate `.plot` bundle containing:
- `spec.json` - What to plot (data, axes, traces)
- `style.json` - How it looks (colors, fonts, theme)
- `exports/` - Rendered images (PNG, SVG, hitmap)
- `cache/` - Computed geometry (regenerable)

## Usage

### Python

```python
import scitex as stx

# Load the figure bundle
bundle = stx.load("{dir_path}")

# Access components
spec = bundle["spec"]       # Figure layout
plots = bundle["plots"]     # Dict of panel bundles

# Access specific panel
panel_a = plots["A"]        # Get panel A's plot bundle
```

### Editing

Edit `spec.json` to change semantic content:
- Panel positions and sizes
- Figure title and caption
- Panel layout

Edit `style.json` to change appearance:
- Figure size (width_mm, height_mm)
- Background color
- Panel label styling
- Theme (light/dark)

Edit individual `*.plot/spec.json` and `*.plot/style.json` to change:
- Plot data and axes (spec.json)
- Trace specifications (spec.json)
- Colors, fonts, theme (style.json)

---

*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Schema: {spec.get("schema", {}).get("name", "scitex.canvas.figure")} v{spec.get("schema", {}).get("version", "1.0.0")}*
"""

    readme_path = dir_path / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)


# EOF
