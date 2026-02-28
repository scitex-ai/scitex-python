#!/usr/bin/env python3
# Timestamp: "2025-12-14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/io/_layered_bundle.py

"""
Layered .plot Bundle I/O - New schema with spec/style/geometry separation.

Bundle structure:
    plot.plot/
        spec.json           # Semantic: WHAT to plot (canonical)
        style.json          # Appearance: HOW it looks (canonical)
        data.csv            # Raw data (immutable)
        exports/
            overview.png    # Preview image
            overview.svg    # Vector preview
            hitmap.png      # Hit testing image
        cache/
            geometry_px.json    # Derived: WHERE in pixels (regenerable)
            render_manifest.json # Render metadata (dpi, hashes)

Design Principles:
- spec.json + style.json = source of truth (edit these)
- cache/* = derived, can be deleted and regenerated
- Canonical units: ratio (0-1) for axes bbox, mm for panel size
"""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.plt.styles import get_default_dpi, get_preview_dpi
from scitex.schema import (
    PLOT_GEOMETRY_VERSION,
    PLOT_SPEC_VERSION,
    PLOT_STYLE_VERSION,
    AxesLabels,
    AxesLimits,
    AxesSpecItem,
    BboxPx,
    BboxRatio,
    DataSourceSpec,
    FontSpec,
    LegendSpec,
    PlotGeometry,
    PlotSpec,
    PlotStyle,
    RenderedArtist,
    RenderedAxes,
    RenderManifest,
    SizeSpec,
    ThemeSpec,
    TraceSpec,
    TraceStyleSpec,
)

logger = logging.getLogger()

__all__ = [
    "save_layered_plot_bundle",
    "load_layered_plot_bundle",
    "merge_layered_bundle",
    "is_layered_bundle",
]


def is_layered_bundle(bundle_dir: Path) -> bool:
    """Check if a bundle uses the new layered format."""
    return (bundle_dir / "spec.json").exists()


def save_layered_plot_bundle(  # noqa: C901
    fig,
    bundle_dir: Path,
    basename: str = "plot",
    dpi: Optional[int] = None,
    csv_df=None,
) -> None:
    """
    Save matplotlib figure as layered .plot bundle.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to save.
    bundle_dir : Path
        Output directory (e.g., plot.plot).
    basename : str
        Base filename for exports.
    dpi : int, optional
        DPI for raster exports. If None, uses get_default_dpi() from config.
    csv_df : DataFrame, optional
        Data to embed as CSV.
    """
    # Resolve DPI from config if not specified
    if dpi is None:
        dpi = get_default_dpi()
    import tempfile
    import warnings

    import numpy as np
    from PIL import Image as PILImage

    bundle_dir = Path(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    exports_dir = bundle_dir / "exports"
    cache_dir = bundle_dir / "cache"
    exports_dir.mkdir(exist_ok=True)
    cache_dir.mkdir(exist_ok=True)

    # Extract figure dimensions
    fig_width_inch, fig_height_inch = fig.get_size_inches()

    # === Build PlotSpec (semantic) ===
    axes_items = []
    traces = []
    extracted_data = {}

    for ax_idx, ax in enumerate(fig.axes):
        bbox = ax.get_position()
        ax_id = f"ax{ax_idx}"

        # Create axes item
        ax_item = AxesSpecItem(
            id=ax_id,
            bbox=BboxRatio(
                x0=round(bbox.x0, 4),
                y0=round(bbox.y0, 4),
                width=round(bbox.width, 4),
                height=round(bbox.height, 4),
                space="panel",
            ),
            limits=AxesLimits(
                x=list(ax.get_xlim()),
                y=list(ax.get_ylim()),
            ),
            labels=AxesLabels(
                xlabel=ax.get_xlabel() or None,
                ylabel=ax.get_ylabel() or None,
                title=ax.get_title() or None,
            ),
        )
        axes_items.append(ax_item)

        # Extract traces from lines
        for line_idx, line in enumerate(ax.get_lines()):
            label = line.get_label()
            if label is None or label.startswith("_"):
                label = f"series_{line_idx}"

            trace_id = f"{ax_id}-line-{line_idx}"
            xdata, ydata = line.get_data()

            if len(xdata) > 0:
                x_col = f"{ax_id}_trace-{trace_id}_x"
                y_col = f"{ax_id}_trace-{trace_id}_y"
                extracted_data[x_col] = np.array(xdata)
                extracted_data[y_col] = np.array(ydata)

                trace = TraceSpec(
                    id=trace_id,
                    type="line",
                    axes_index=ax_idx,
                    x_col=x_col,
                    y_col=y_col,
                    label=label,
                )
                traces.append(trace)

    # Handle CSV data - prefer extracted data (captures all matplotlib artists)
    csv_hash = None
    if extracted_data:
        # Use extracted data from matplotlib artists (captures axhline, etc.)
        import pandas as pd

        max_len = max(len(v) for v in extracted_data.values())
        padded = {}
        for k, v in extracted_data.items():
            # Convert to float for NaN padding compatibility
            v_float = np.array(v, dtype=float)
            if len(v_float) < max_len:
                padded[k] = np.pad(
                    v_float, (0, max_len - len(v_float)), constant_values=np.nan
                )
            else:
                padded[k] = v_float
        csv_df = pd.DataFrame(padded)
        csv_str = csv_df.to_csv(index=False)
        csv_hash = f"sha256:{hashlib.sha256(csv_str.encode()).hexdigest()[:16]}"
    elif csv_df is not None:
        # Fallback to provided CSV if no extracted data
        csv_str = csv_df.to_csv(index=False)
        csv_hash = f"sha256:{hashlib.sha256(csv_str.encode()).hexdigest()[:16]}"

    # Create spec
    spec = PlotSpec(
        plot_id=basename,
        data=DataSourceSpec(
            csv=f"{basename}.csv",
            format="wide",
            hash=csv_hash,
        ),
        axes=axes_items,
        traces=traces,
    )

    # === Build PlotStyle (appearance) ===
    # Detect theme from figure
    theme_mode = "light"
    if hasattr(fig, "_scitex_theme"):
        theme_mode = fig._scitex_theme

    trace_styles = []
    for ax_idx, ax in enumerate(fig.axes):
        for line_idx, line in enumerate(ax.get_lines()):
            label = line.get_label()
            if label and not label.startswith("_"):
                # Get line color
                import matplotlib.colors as mcolors

                color = line.get_color()
                if isinstance(color, (list, tuple)):
                    color = mcolors.to_hex(color)

                trace_id = f"ax{ax_idx}-line-{line_idx}"
                trace_styles.append(
                    TraceStyleSpec(
                        trace_id=trace_id,
                        color=color,
                        linewidth=line.get_linewidth(),
                        alpha=line.get_alpha(),
                    )
                )

    # Extract legend configuration from first axes with legend
    legend_spec = LegendSpec(visible=True, location="best")
    for ax in fig.axes:
        legend = ax.get_legend()
        if legend is not None:
            # Extract legend location
            # matplotlib legend._loc can be int or string
            loc = legend._loc
            loc_map = {
                0: "best",
                1: "upper right",
                2: "upper left",
                3: "lower left",
                4: "lower right",
                5: "right",
                6: "center left",
                7: "center right",
                8: "lower center",
                9: "upper center",
                10: "center",
            }
            if isinstance(loc, int):
                location = loc_map.get(loc, "best")
            else:
                location = str(loc) if loc else "best"

            # If location is "best", determine actual position from rendered bbox
            if location == "best":
                try:
                    # Get the actual rendered position
                    bbox = legend.get_window_extent(fig.canvas.get_renderer())
                    ax_bbox = ax.get_position()
                    fig_width, fig_height = fig.get_size_inches() * fig.dpi

                    # Calculate legend center relative to axes
                    legend_center_x = (bbox.x0 + bbox.x1) / 2
                    legend_center_y = (bbox.y0 + bbox.y1) / 2
                    ax_center_x = (ax_bbox.x0 + ax_bbox.x1) / 2 * fig_width
                    ax_center_y = (ax_bbox.y0 + ax_bbox.y1) / 2 * fig_height

                    # Determine quadrant
                    is_right = legend_center_x > ax_center_x
                    is_upper = legend_center_y > ax_center_y

                    if is_upper and is_right:
                        location = "upper right"
                    elif is_upper and not is_right:
                        location = "upper left"
                    elif not is_upper and is_right:
                        location = "lower right"
                    else:
                        location = "lower left"
                except Exception:
                    pass  # Keep "best" if we can't determine

            # Extract other legend properties
            legend_spec = LegendSpec(
                visible=legend.get_visible(),
                location=location,
                frameon=legend.get_frame_on(),
                fontsize=legend._fontsize if hasattr(legend, "_fontsize") else None,
                ncols=legend._ncols if hasattr(legend, "_ncols") else 1,
                title=legend.get_title().get_text() if legend.get_title() else None,
            )
            break  # Use first legend found

    style = PlotStyle(
        theme=ThemeSpec(
            mode=theme_mode,
            colors={
                "background": "transparent",
                "axes_bg": "white" if theme_mode == "light" else "transparent",
                "text": "black" if theme_mode == "light" else "#e8e8e8",
                "spine": "black" if theme_mode == "light" else "#e8e8e8",
                "tick": "black" if theme_mode == "light" else "#e8e8e8",
            },
        ),
        size=SizeSpec(
            width_mm=round(fig_width_inch * 25.4, 1),
            height_mm=round(fig_height_inch * 25.4, 1),
        ),
        font=FontSpec(family="sans-serif", size_pt=8.0),
        traces=trace_styles,
        legend=legend_spec,
    )

    # === Save exports and track coordinate transformations ===
    #
    # Cropping Pipeline:
    #
    #   ┌──────────────────────────────┐
    #   │  original_figure_size_px     │  ← matplotlib figure canvas
    #   │  ┌────────────────────────┐  │     (where bbox_px are measured)
    #   │  │ tight_bbox             │  │
    #   │  │  ┌──────────────────┐  │  │
    #   │  │  │ final_image_px   │  │  │  ← exported PNG (what user sees)
    #   │  │  └──────────────────┘  │  │
    #   │  └────────────────────────┘  │
    #   └──────────────────────────────┘
    #
    # To convert: final_coord = original_coord - total_crop_offset
    #
    # IMPORTANT: Use fig.dpi for coordinate calculations, NOT export dpi
    # extract_selectable_regions uses fig.dpi for all bbox calculations
    fig_dpi = fig.dpi

    # Ensure renderer is ready
    fig.canvas.draw()

    # Scale factor: export_dpi / fig_dpi (to scale from display coords to export PNG coords)
    dpi_scale = dpi / fig_dpi

    with tempfile.TemporaryDirectory():
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*tight_layout.*")

            # Save PNG at full figure size (crop function will handle tight cropping)
            # This ensures coordinate transformations are accurate
            png_path = exports_dir / f"{basename}.png"
            fig.savefig(png_path, dpi=dpi, format="png", transparent=True)

            # Save SVG with tight bbox (separate concern, no coord issues)
            svg_path = exports_dir / f"{basename}.svg"
            fig.savefig(svg_path, bbox_inches="tight", format="svg")

            # Generate hitmap
            from scitex.plt.utils._hitmap import (
                HITMAP_AXES_COLOR,
                HITMAP_BACKGROUND_COLOR,
                apply_hitmap_colors,
                extract_path_data,
                extract_selectable_regions,
                restore_original_colors,
            )

            original_props, color_map, groups = apply_hitmap_colors(fig)

            # Store and set hitmap colors for hitmap generation
            saved_fig_facecolor = fig.patch.get_facecolor()
            saved_ax_facecolors = []
            for ax in fig.axes:
                saved_ax_facecolors.append(ax.get_facecolor())
                ax.set_facecolor(HITMAP_BACKGROUND_COLOR)
                for spine in ax.spines.values():
                    spine.set_color(HITMAP_AXES_COLOR)

            fig.patch.set_facecolor(HITMAP_BACKGROUND_COLOR)

            # Save hitmap at full figure size (will crop with same box as main PNG)
            hitmap_path = exports_dir / f"{basename}_hitmap.png"
            fig.savefig(
                hitmap_path, dpi=dpi, format="png", facecolor=HITMAP_BACKGROUND_COLOR
            )

            # Restore colors
            restore_original_colors(original_props)
            fig.patch.set_facecolor(saved_fig_facecolor)
            for i, ax in enumerate(fig.axes):
                ax.set_facecolor(saved_ax_facecolors[i])

            # Apply additional margin cropping (removes transparent edges)
            margin_crop_box = None
            try:
                from figrecipe import crop

                _, margin_crop_box = crop(
                    str(png_path),
                    output_path=str(png_path),
                    overwrite=True,
                    margin_px=12,
                    verbose=False,
                    return_offset=True,
                )

                crop(
                    str(hitmap_path),
                    output_path=str(hitmap_path),
                    overwrite=True,
                    crop_box=(
                        margin_crop_box["left"],
                        margin_crop_box["upper"],
                        margin_crop_box["right"],
                        margin_crop_box["lower"],
                    ),
                    verbose=False,
                )
            except Exception as e:
                logger.debug(f"Crop failed: {e}")

    # === Coordinate transformation pipeline ===
    #
    # Strategy: Since we save at full figure size (no bbox_inches='tight'),
    # the crop function's crop_box IS the total offset from original figure to final PNG.
    #
    # We extract coordinates at export DPI so they match the saved PNG directly.

    # Temporarily set fig.dpi to export DPI for coordinate extraction
    saved_fig_dpi = fig.dpi
    fig.set_dpi(dpi)
    fig.canvas.draw()  # Redraw at new DPI

    # crop_box is the total offset from full figure to final PNG
    # (crop_box['left'], crop_box['upper']) = top-left corner of crop region
    total_offset_left = margin_crop_box["left"] if margin_crop_box else 0
    total_offset_upper = margin_crop_box["upper"] if margin_crop_box else 0

    # === Build PlotGeometry (cache) ===
    # Extract at export DPI so coords are in full figure space (matches saved PNG before crop)
    path_data = extract_path_data(fig)
    selectable_regions = extract_selectable_regions(fig)

    # Restore original DPI
    fig.set_dpi(saved_fig_dpi)

    # Get final image size (what user sees)
    with PILImage.open(png_path) as img:
        final_image_size_px = list(img.size)

    # Adjust coordinates: subtract total offset (both tight_bbox and margin_crop)
    # No DPI scaling needed since we extracted at export DPI
    selectable_regions = _adjust_coords_for_offset(
        selectable_regions, total_offset_left, total_offset_upper
    )
    path_data = _adjust_path_data_for_offset(
        path_data, total_offset_left, total_offset_upper
    )

    rendered_axes = []
    for ax_idx, ax_data in enumerate(path_data.get("axes", [])):
        bbox_data = ax_data.get("bbox_px", {})
        rendered_axes.append(
            RenderedAxes(
                id=f"ax{ax_idx}",
                xlim=ax_data.get("xlim", [0, 1]),
                ylim=ax_data.get("ylim", [0, 1]),
                bbox_px=BboxPx(
                    x0=bbox_data.get("x0", 0),
                    y0=bbox_data.get("y0", 0),
                    width=bbox_data.get(
                        "width", bbox_data.get("x1", 0) - bbox_data.get("x0", 0)
                    ),
                    height=bbox_data.get(
                        "height", bbox_data.get("y1", 0) - bbox_data.get("y0", 0)
                    ),
                ),
            )
        )

    rendered_artists = []
    for artist in path_data.get("artists", []):
        bbox_data = artist.get("bbox_px", {})
        rendered_artists.append(
            RenderedArtist(
                id=str(artist.get("id", "")),
                type=artist.get("type", "unknown"),
                axes_index=artist.get("axes_index", 0),
                bbox_px=(
                    BboxPx(
                        x0=bbox_data.get("x0", 0),
                        y0=bbox_data.get("y0", 0),
                        width=bbox_data.get(
                            "width", bbox_data.get("x1", 0) - bbox_data.get("x0", 0)
                        ),
                        height=bbox_data.get(
                            "height", bbox_data.get("y1", 0) - bbox_data.get("y0", 0)
                        ),
                    )
                    if bbox_data
                    else None
                ),
                path_px=artist.get("path_px"),
            )
        )

    geometry = PlotGeometry(
        source_hash=csv_hash or "",
        figure_px=final_image_size_px,  # Final cropped image size
        dpi=dpi,  # Export DPI (stored for consumers)
        axes=rendered_axes,
        artists=rendered_artists,
        hit_regions={
            "strategy": "hybrid",
            "hit_map": f"{basename}_hitmap.png",
            "color_map": {str(k): v for k, v in color_map.items()},
            "groups": groups,
            # Store DPI info for consumers that need to retrieve from data
            "fig_dpi": fig_dpi,  # Original matplotlib fig.dpi
            "export_dpi": dpi,  # Export DPI used for PNG
            "dpi_scale": dpi_scale,  # export_dpi / fig_dpi
        },
        selectable_regions=selectable_regions,
        # Note: crop_box is now None because all coordinates are already adjusted
        # to final_image space (no further transformation needed by consumers)
        crop_box=None,
    )

    # === Save all JSON files ===
    # spec.json
    spec_path = bundle_dir / "spec.json"
    with open(spec_path, "w") as f:
        json.dump(
            {
                "schema": {"name": "scitex.plt.spec", "version": PLOT_SPEC_VERSION},
                **asdict(spec),
            },
            f,
            indent=2,
            default=str,
        )

    # style.json
    style_path = bundle_dir / "style.json"
    with open(style_path, "w") as f:
        json.dump(
            {
                "schema": {"name": "scitex.plt.style", "version": PLOT_STYLE_VERSION},
                **asdict(style),
            },
            f,
            indent=2,
            default=str,
        )

    # cache/geometry_px.json
    geometry_path = cache_dir / "geometry_px.json"
    with open(geometry_path, "w") as f:
        json.dump(
            {
                "schema": {
                    "name": "scitex.plt.geometry",
                    "version": PLOT_GEOMETRY_VERSION,
                },
                "_comment": "CACHE - can be deleted and regenerated from spec + style",
                **asdict(geometry),
            },
            f,
            indent=2,
            default=str,
        )

    # cache/render_manifest.json
    spec_hash = hashlib.sha256(open(spec_path, "rb").read()).hexdigest()[:16]
    style_hash = hashlib.sha256(open(style_path, "rb").read()).hexdigest()[:16]
    manifest = RenderManifest(
        source_hash=f"{spec_hash}:{style_hash}",
        panel_size_mm=[
            round(fig_width_inch * 25.4, 1),
            round(fig_height_inch * 25.4, 1),
        ],
        dpi=dpi,
        render_px=final_image_size_px,
        overview_png=f"exports/{basename}.png",
        overview_svg=f"exports/{basename}.svg",
        hitmap_png=f"exports/{basename}_hitmap.png",
    )
    manifest_path = cache_dir / "render_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(
            {
                "schema": {
                    "name": "scitex.plt.render_manifest",
                    "version": PLOT_GEOMETRY_VERSION,
                },
                **asdict(manifest),
            },
            f,
            indent=2,
            default=str,
        )

    # Save CSV
    if csv_df is not None:
        csv_path = bundle_dir / f"{basename}.csv"
        csv_df.to_csv(csv_path, index=False)

    # Generate overview showing main image and hitmap side by side
    _generate_plot_overview(exports_dir, basename)

    # Generate dynamic README.md
    _generate_plot_readme(bundle_dir, basename, spec, style, geometry, manifest)

    logger.debug(f"Saved layered plot bundle: {bundle_dir}")


def _generate_plot_overview(exports_dir: Path, basename: str) -> None:  # noqa: C901
    """Generate comprehensive overview with plot, hitmap, overlay, bboxes, and JSON info.

    Args
    ----
        exports_dir: Path to exports directory.
        basename: Base filename for the bundle.
    """
    import warnings

    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    bundle_dir = exports_dir.parent
    png_path = exports_dir / f"{basename}.png"
    hitmap_path = exports_dir / f"{basename}_hitmap.png"

    if not png_path.exists():
        return

    try:
        main_img = Image.open(png_path)
        img_width, img_height = main_img.size
        has_hitmap = hitmap_path.exists()

        # Load JSON files for displaying info
        spec_data = {}
        style_data = {}
        geometry_data = {}
        manifest_data = {}

        spec_path = bundle_dir / "spec.json"
        style_path = bundle_dir / "style.json"
        geometry_path = bundle_dir / "cache" / "geometry_px.json"
        manifest_path = bundle_dir / "cache" / "render_manifest.json"

        if spec_path.exists():
            with open(spec_path) as f:
                spec_data = json.load(f)
        if style_path.exists():
            with open(style_path) as f:
                style_data = json.load(f)
        if geometry_path.exists():
            with open(geometry_path) as f:
                geometry_data = json.load(f)
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest_data = json.load(f)

        # Get DPI and panel size for mm scaler
        dpi = manifest_data.get("dpi", get_default_dpi())
        panel_size_mm = manifest_data.get("panel_size_mm", [80, 68])

        # Create figure with 2 rows, 3 columns layout
        # Row 1: Plot | Hitmap | Overlay
        # Row 2: Bboxes | JSON Info | mm Scaler
        fig = plt.figure(figsize=(18, 12), facecolor="white")
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.2)

        # === Row 1: Images ===
        # 1. Main Plot
        ax_plot = fig.add_subplot(gs[0, 0])
        ax_plot.set_title("Plot", fontweight="bold", fontsize=11)
        ax_plot.imshow(main_img)
        ax_plot.axis("off")

        # 2. Hitmap with ID labels
        ax_hitmap = fig.add_subplot(gs[0, 1])
        ax_hitmap.set_title("Hit Regions", fontweight="bold", fontsize=11)
        if has_hitmap:
            hitmap_img = Image.open(hitmap_path)
            ax_hitmap.imshow(hitmap_img)

            # Add ID labels from hit_regions color_map
            color_map = geometry_data.get("hit_regions", {}).get("color_map", {})
            artists = geometry_data.get("artists", [])

            # Note: bbox_px coordinates are already in final image space
            for idx, artist in enumerate(artists):
                bbox = artist.get("bbox_px", {})
                if bbox:
                    # Get center of bbox for label placement
                    x0 = bbox.get("x0", 0)
                    y0 = bbox.get("y0", 0)
                    width = bbox.get("width", 0)
                    height = bbox.get("height", 0)
                    cx, cy = x0 + width / 2, y0 + height / 2

                    # Find label from color_map (color_map IDs are 1-indexed)
                    color_map_id = str(idx + 1)
                    label = f"artist_{idx}"
                    if color_map_id in color_map:
                        label = color_map[color_map_id].get("label", label)

                    ax_hitmap.text(
                        cx,
                        cy,
                        label,
                        fontsize=8,
                        ha="center",
                        va="center",
                        color="white",
                        fontweight="bold",
                        bbox=dict(
                            boxstyle="round,pad=0.2", facecolor="black", alpha=0.7
                        ),
                    )
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

        # 3. Overlay (plot + hitmap with transparency)
        ax_overlay = fig.add_subplot(gs[0, 2])
        ax_overlay.set_title("Overlay (Plot + Hit)", fontweight="bold", fontsize=11)
        ax_overlay.imshow(main_img)
        if has_hitmap:
            hitmap_img = Image.open(hitmap_path).convert("RGBA")
            hitmap_array = np.array(hitmap_img)
            # Create semi-transparent overlay
            hitmap_array[:, :, 3] = (hitmap_array[:, :, 3] * 0.5).astype(np.uint8)
            ax_overlay.imshow(hitmap_array, alpha=0.5)
        ax_overlay.axis("off")

        # === Row 2: Details ===
        # 4. Bboxes visualization
        ax_bboxes = fig.add_subplot(gs[1, 0])
        ax_bboxes.set_title("Element Bboxes", fontweight="bold", fontsize=11)
        ax_bboxes.imshow(main_img)

        # Note: bbox_px coordinates are already in final image space
        # (adjusted during save_layered_plot_bundle), so no offset needed

        # Draw bboxes from geometry
        colors = ["red", "blue", "green", "orange", "purple", "cyan"]
        selectable = geometry_data.get("selectable_regions", {})

        for ax_idx, ax_region in enumerate(selectable.get("axes", [])):
            color = colors[ax_idx % len(colors)]

            # Title bbox
            if "title" in ax_region:
                bbox = ax_region["title"].get("bbox_px", [])
                if len(bbox) == 4:
                    _draw_bbox(ax_bboxes, bbox, color, "title")

            # xlabel bbox
            if "xlabel" in ax_region:
                bbox = ax_region["xlabel"].get("bbox_px", [])
                if len(bbox) == 4:
                    _draw_bbox(ax_bboxes, bbox, color, "xlabel")

            # ylabel bbox
            if "ylabel" in ax_region:
                bbox = ax_region["ylabel"].get("bbox_px", [])
                if len(bbox) == 4:
                    _draw_bbox(ax_bboxes, bbox, color, "ylabel")

            # xaxis spine
            if "xaxis" in ax_region and "spine" in ax_region["xaxis"]:
                bbox = ax_region["xaxis"]["spine"].get("bbox_px", [])
                if len(bbox) == 4:
                    _draw_bbox(ax_bboxes, bbox, "gray", "xaxis", lw=1)

            # yaxis spine
            if "yaxis" in ax_region and "spine" in ax_region["yaxis"]:
                bbox = ax_region["yaxis"]["spine"].get("bbox_px", [])
                if len(bbox) == 4:
                    _draw_bbox(ax_bboxes, bbox, "gray", "yaxis", lw=1)

            # legend bbox
            if "legend" in ax_region:
                bbox = ax_region["legend"].get("bbox_px", [])
                if len(bbox) == 4:
                    _draw_bbox(ax_bboxes, bbox, "magenta", "legend")

        ax_bboxes.axis("off")

        # 5. JSON Info
        ax_json = fig.add_subplot(gs[1, 1])
        ax_json.set_title("Bundle Info (depth=2)", fontweight="bold", fontsize=11)
        ax_json.axis("off")

        # Format JSON summary with limited depth
        json_text = _format_json_summary(
            {"spec": spec_data, "style": style_data}, max_depth=2
        )
        ax_json.text(
            0.02,
            0.98,
            json_text,
            transform=ax_json.transAxes,
            fontsize=7,
            fontfamily="monospace",
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        # 6. mm Scaler
        ax_scale = fig.add_subplot(gs[1, 2])
        ax_scale.set_title("Size & Scale (mm)", fontweight="bold", fontsize=11)

        # Show the image with mm scale bars
        ax_scale.imshow(main_img, extent=[0, panel_size_mm[0], panel_size_mm[1], 0])

        # Add grid lines every 10mm
        for x in range(0, int(panel_size_mm[0]) + 1, 10):
            ax_scale.axvline(x, color="gray", linewidth=0.5, alpha=0.5)
            if x > 0:
                ax_scale.text(x, -1, f"{x}", ha="center", fontsize=7)
        for y in range(0, int(panel_size_mm[1]) + 1, 10):
            ax_scale.axhline(y, color="gray", linewidth=0.5, alpha=0.5)
            if y > 0:
                ax_scale.text(-1, y, f"{y}", ha="right", va="center", fontsize=7)

        ax_scale.set_xlabel("mm", fontsize=9)
        ax_scale.set_ylabel("mm", fontsize=9)
        ax_scale.set_xlim(-3, panel_size_mm[0] + 1)
        ax_scale.set_ylim(panel_size_mm[1] + 1, -3)

        # Add size text
        size_text = f"Panel: {panel_size_mm[0]:.1f} × {panel_size_mm[1]:.1f} mm\nDPI: {dpi}\nPixels: {img_width} × {img_height}"
        ax_scale.text(
            panel_size_mm[0] * 0.95,
            panel_size_mm[1] * 0.95,
            size_text,
            ha="right",
            va="bottom",
            fontsize=8,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        fig.suptitle(f"Overview: {basename}", fontsize=14, fontweight="bold", y=0.98)

        overview_path = exports_dir / f"{basename}_overview.png"
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*tight_layout.*")
            fig.savefig(
                overview_path,
                dpi=get_preview_dpi(),
                bbox_inches="tight",
                facecolor="white",
            )
        plt.close(fig)

    except Exception as e:
        logger.debug(f"Could not generate plot overview: {e}")
        import traceback

        logger.debug(traceback.format_exc())


def _generate_plot_readme(
    bundle_dir: Path,
    basename: str,
    spec: "PlotSpec",
    style: "PlotStyle",
    geometry: "PlotGeometry",
    manifest: "RenderManifest",
) -> None:
    """Generate a dynamic README.md describing the bundle.

    Parameters
    ----------
    bundle_dir : Path
        Path to the bundle directory.
    basename : str
        Base filename for the bundle.
    spec : PlotSpec
        The plot specification.
    style : PlotStyle
        The plot style.
    geometry : PlotGeometry
        The rendered geometry.
    manifest : RenderManifest
        The render manifest.
    """
    from datetime import datetime

    # Count elements
    n_axes = len(spec.axes) if spec.axes else 0
    n_traces = len(spec.traces) if spec.traces else 0

    # Get size info
    width_mm = style.size.width_mm if style.size else 0
    height_mm = style.size.height_mm if style.size else 0
    dpi = manifest.dpi
    render_px = manifest.render_px

    readme_content = f"""# {basename}.plot

> SciTeX Layered Plot Bundle - Auto-generated README

## Overview

![Plot Overview](exports/{basename}_overview.png)

## Bundle Structure

```
{basename}.plot/
├── spec.json           # WHAT to plot (semantic, editable)
├── style.json          # HOW it looks (appearance, editable)
├── {basename}.csv      # Raw data (immutable)
├── exports/
│   ├── {basename}.png          # Main plot image
│   ├── {basename}.svg          # Vector version
│   ├── {basename}_hitmap.png   # Hit detection image
│   └── {basename}_overview.png # Visual summary
├── cache/
│   ├── geometry_px.json       # Pixel coordinates (regenerable)
│   └── render_manifest.json   # Render metadata
└── README.md           # This file
```

## Plot Information

| Property | Value |
|----------|-------|
| Plot ID | `{spec.plot_id}` |
| Axes | {n_axes} |
| Traces | {n_traces} |
| Size | {width_mm:.1f} × {height_mm:.1f} mm |
| DPI | {dpi} |
| Pixels | {render_px[0]} × {render_px[1]} |
| Theme | {style.theme.mode if style.theme else "light"} |

## Coordinate System

The bundle uses a layered coordinate system:

1. **spec.json + style.json** = Source of truth (edit these)
2. **cache/** = Derived data (can be deleted and regenerated)

### Coordinate Transformation Pipeline

```
Original Figure (at export DPI)
         │
         ▼ crop_box offset
    ┌─────────────────┐
    │  Final PNG      │  ← bbox_px coordinates are in this space
    │  ({render_px[0]} × {render_px[1]})  │
    └─────────────────┘
```

**Formula**: `final_coords = original_coords - crop_offset`

## Usage

### Python

```python
import scitex as stx

# Load the bundle
bundle = stx.plt.io.load_layered_plot_bundle("{bundle_dir}")

# Access components
spec = bundle["spec"]       # What to plot
style = bundle["style"]     # How it looks
geometry = bundle["geometry"]  # Where in pixels
```

### Editing

Edit `spec.json` to change:
- Axis labels, titles, limits
- Trace data columns
- Data source

Edit `style.json` to change:
- Colors, line widths
- Font sizes
- Theme (light/dark)

After editing, regenerate cache with:
```python
stx.plt.io.regenerate_cache("{bundle_dir}")
```

---

*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Schema: scitex.plt v{PLOT_SPEC_VERSION}*
"""

    readme_path = bundle_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)


def _adjust_coords_for_offset(  # noqa: C901
    selectable_regions: Dict[str, Any],
    offset_left: float,
    offset_upper: float,
) -> Dict[str, Any]:
    """Adjust bbox_px coordinates by subtracting offset.

    Used when coordinates are already in PNG space (extracted at export DPI).

    Parameters
    ----------
    selectable_regions : dict
        The selectable_regions dict (already in PNG coords).
    offset_left : float
        Total offset from left edge to subtract.
    offset_upper : float
        Total offset from top edge to subtract.

    Returns
    -------
    dict
        selectable_regions with adjusted coordinates.
    """
    import copy

    result = copy.deepcopy(selectable_regions)

    def adjust_bbox(bbox: List[float]) -> List[float]:
        """Subtract offset from [x0, y0, x1, y1] bbox."""
        return [
            bbox[0] - offset_left,
            bbox[1] - offset_upper,
            bbox[2] - offset_left,
            bbox[3] - offset_upper,
        ]

    for ax_region in result.get("axes", []):
        # Adjust title, xlabel, ylabel
        for key in ["title", "xlabel", "ylabel"]:
            if key in ax_region and "bbox_px" in ax_region[key]:
                ax_region[key]["bbox_px"] = adjust_bbox(ax_region[key]["bbox_px"])

        # Adjust xaxis elements
        if "xaxis" in ax_region:
            xaxis = ax_region["xaxis"]
            if xaxis.get("spine") and "bbox_px" in xaxis["spine"]:
                xaxis["spine"]["bbox_px"] = adjust_bbox(xaxis["spine"]["bbox_px"])
            for tick in xaxis.get("ticks", []):
                if "bbox_px" in tick:
                    tick["bbox_px"] = adjust_bbox(tick["bbox_px"])
            for label in xaxis.get("ticklabels", []):
                if "bbox_px" in label:
                    label["bbox_px"] = adjust_bbox(label["bbox_px"])

        # Adjust yaxis elements
        if "yaxis" in ax_region:
            yaxis = ax_region["yaxis"]
            if yaxis.get("spine") and "bbox_px" in yaxis["spine"]:
                yaxis["spine"]["bbox_px"] = adjust_bbox(yaxis["spine"]["bbox_px"])
            for tick in yaxis.get("ticks", []):
                if "bbox_px" in tick:
                    tick["bbox_px"] = adjust_bbox(tick["bbox_px"])
            for label in yaxis.get("ticklabels", []):
                if "bbox_px" in label:
                    label["bbox_px"] = adjust_bbox(label["bbox_px"])

        # Adjust legend
        if "legend" in ax_region:
            legend = ax_region["legend"]
            if "bbox_px" in legend:
                legend["bbox_px"] = adjust_bbox(legend["bbox_px"])
            for entry in legend.get("entries", []):
                if "bbox_px" in entry:
                    entry["bbox_px"] = adjust_bbox(entry["bbox_px"])

    return result


def _adjust_path_data_for_offset(  # noqa: C901
    path_data: Dict[str, Any],
    offset_left: float,
    offset_upper: float,
) -> Dict[str, Any]:
    """Adjust path_data coordinates by subtracting offset.

    Used when coordinates are already in PNG space (extracted at export DPI).

    Parameters
    ----------
    path_data : dict
        The path_data dict (already in PNG coords).
    offset_left : float
        Total offset from left edge to subtract.
    offset_upper : float
        Total offset from top edge to subtract.

    Returns
    -------
    dict
        path_data with adjusted coordinates.
    """
    import copy

    result = copy.deepcopy(path_data)

    # Adjust axes bbox_px
    for ax in result.get("axes", []):
        if "bbox_px" in ax:
            bbox = ax["bbox_px"]
            if isinstance(bbox, dict):
                bbox["x0"] = bbox.get("x0", 0) - offset_left
                bbox["y0"] = bbox.get("y0", 0) - offset_upper
                if "x1" in bbox:
                    bbox["x1"] = bbox["x1"] - offset_left
                if "y1" in bbox:
                    bbox["y1"] = bbox["y1"] - offset_upper

    # Adjust artists
    for artist in result.get("artists", []):
        if "bbox_px" in artist and artist["bbox_px"]:
            bbox = artist["bbox_px"]
            if isinstance(bbox, dict):
                bbox["x0"] = bbox.get("x0", 0) - offset_left
                bbox["y0"] = bbox.get("y0", 0) - offset_upper
                if "x1" in bbox:
                    bbox["x1"] = bbox["x1"] - offset_left
                if "y1" in bbox:
                    bbox["y1"] = bbox["y1"] - offset_upper

        # Adjust path_px points
        if "path_px" in artist and artist["path_px"]:
            artist["path_px"] = [
                [pt[0] - offset_left, pt[1] - offset_upper]
                for pt in artist["path_px"]
                if len(pt) >= 2
            ]

    return result


def _adjust_path_data_for_crop(  # noqa: C901
    path_data: Dict[str, Any],
    offset_left: float,
    offset_upper: float,
) -> Dict[str, Any]:
    """Adjust path_data coordinates by subtracting crop offset.

    Parameters
    ----------
    path_data : dict
        The path_data dict from extract_path_data.
    offset_left : float
        Total offset from left edge.
    offset_upper : float
        Total offset from top edge.

    Returns
    -------
    dict
        path_data with adjusted coordinates.
    """
    import copy

    result = copy.deepcopy(path_data)

    # Adjust axes bbox_px
    for ax in result.get("axes", []):
        if "bbox_px" in ax:
            bbox = ax["bbox_px"]
            if isinstance(bbox, dict):
                bbox["x0"] = bbox.get("x0", 0) - offset_left
                bbox["y0"] = bbox.get("y0", 0) - offset_upper
                # x1, y1 if present
                if "x1" in bbox:
                    bbox["x1"] = bbox["x1"] - offset_left
                if "y1" in bbox:
                    bbox["y1"] = bbox["y1"] - offset_upper

    # Adjust artists
    for artist in result.get("artists", []):
        if "bbox_px" in artist and artist["bbox_px"]:
            bbox = artist["bbox_px"]
            if isinstance(bbox, dict):
                bbox["x0"] = bbox.get("x0", 0) - offset_left
                bbox["y0"] = bbox.get("y0", 0) - offset_upper
                if "x1" in bbox:
                    bbox["x1"] = bbox["x1"] - offset_left
                if "y1" in bbox:
                    bbox["y1"] = bbox["y1"] - offset_upper

        # Adjust path_px points
        if "path_px" in artist and artist["path_px"]:
            artist["path_px"] = [
                [pt[0] - offset_left, pt[1] - offset_upper]
                for pt in artist["path_px"]
                if len(pt) >= 2
            ]

    return result


def _draw_bbox(ax, bbox: List, color: str, label: str, lw: float = 2) -> None:
    """Draw a bounding box on an axes with label inside."""
    import matplotlib.patches as patches

    x0, y0, x1, y1 = bbox
    width = x1 - x0
    height = y1 - y0
    rect = patches.Rectangle(
        (x0, y0), width, height, linewidth=lw, edgecolor=color, facecolor="none"
    )
    ax.add_patch(rect)
    # Place label at top-left corner inside the box with background
    ax.text(
        x0 + 2,
        y0 + 2,
        label,
        fontsize=6,
        color="white",
        va="top",
        ha="left",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.1", facecolor=color, alpha=0.8),
    )


def _format_json_summary(  # noqa: C901
    data: Dict, max_depth: int = 2, current_depth: int = 0
) -> str:  # noqa: C901
    """Format JSON data as summary text with limited depth."""
    lines = []

    def _format_value(key: str, value, depth: int, prefix: str = "") -> None:
        indent = "  " * depth
        if depth >= max_depth:
            if isinstance(value, dict):
                lines.append(f"{prefix}{indent}{key}: {{...}} ({len(value)} keys)")
            elif isinstance(value, list):
                lines.append(f"{prefix}{indent}{key}: [...] ({len(value)} items)")
            else:
                val_str = str(value)[:30]
                if len(str(value)) > 30:
                    val_str += "..."
                lines.append(f"{prefix}{indent}{key}: {val_str}")
        elif isinstance(value, dict):
            lines.append(f"{prefix}{indent}{key}:")
            for k, v in list(value.items())[:8]:  # Limit items
                _format_value(k, v, depth + 1, prefix)
            if len(value) > 8:
                lines.append(f"{prefix}{indent}  ... ({len(value) - 8} more)")
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], dict):
                lines.append(f"{prefix}{indent}{key}: [{len(value)} items]")
            else:
                val_str = str(value)[:50]
                if len(str(value)) > 50:
                    val_str += "..."
                lines.append(f"{prefix}{indent}{key}: {val_str}")
        else:
            val_str = str(value)[:40]
            if len(str(value)) > 40:
                val_str += "..."
            lines.append(f"{prefix}{indent}{key}: {val_str}")

    for key, value in data.items():
        _format_value(key, value, current_depth)

    return "\n".join(lines[:40])  # Limit total lines


def load_layered_plot_bundle(bundle_dir: Path) -> Dict[str, Any]:
    """
    Load layered .plot bundle and return merged spec for editor.

    Parameters
    ----------
    bundle_dir : Path
        Path to .plot bundle.

    Returns
    -------
    dict
        Merged bundle data compatible with editor.
    """
    bundle_dir = Path(bundle_dir)

    result = {
        "spec": None,
        "style": None,
        "geometry": None,
        "merged": None,  # Combined for backward compatibility
        "basename": "plot",
    }

    # Load spec.json
    spec_path = bundle_dir / "spec.json"
    if spec_path.exists():
        with open(spec_path) as f:
            result["spec"] = json.load(f)
            result["basename"] = result["spec"].get("plot_id", "plot")  # type: ignore[attr-defined]

    # Load style.json
    style_path = bundle_dir / "style.json"
    if style_path.exists():
        with open(style_path) as f:
            result["style"] = json.load(f)

    # Load geometry from cache
    geometry_path = bundle_dir / "cache" / "geometry_px.json"
    if geometry_path.exists():
        with open(geometry_path) as f:
            result["geometry"] = json.load(f)

    # Create merged view for backward compatibility with editor
    result["merged"] = merge_layered_bundle(  # type: ignore[assignment]
        result["spec"], result["style"], result["geometry"]  # type: ignore[arg-type]
    )

    return result


def merge_layered_bundle(  # noqa: C901
    spec: Optional[Dict],
    style: Optional[Dict],
    geometry: Optional[Dict],
) -> Dict[str, Any]:
    """
    Merge spec/style/geometry into old-format compatible dict for editor.

    This provides backward compatibility with editors expecting the old format.
    """
    if spec is None:
        return {}

    merged = {
        "schema": {"name": "scitex.plt.plot", "version": "2.0.0"},
        "backend": "mpl",
    }

    # Merge data section
    if "data" in spec:
        merged["data"] = {
            "source": spec["data"].get("csv", "data.csv"),
            "path": spec["data"].get("csv", "data.csv"),
            "hash": spec["data"].get("hash"),
        }

    # Merge size from style
    if style and "size" in style:
        merged["size"] = {
            "width_mm": style["size"].get("width_mm", 80),
            "height_mm": style["size"].get("height_mm", 68),
            "dpi": (
                geometry.get("dpi", get_default_dpi())
                if geometry
                else get_default_dpi()
            ),
        }

    # Merge axes from spec + style + geometry
    merged["axes"] = []
    for ax_spec in spec.get("axes", []):
        ax_merged = {
            "id": ax_spec.get("id"),
            "xlabel": ax_spec.get("labels", {}).get("xlabel"),
            "ylabel": ax_spec.get("labels", {}).get("ylabel"),
            "title": ax_spec.get("labels", {}).get("title"),
            "xlim": ax_spec.get("limits", {}).get("x"),
            "ylim": ax_spec.get("limits", {}).get("y"),
            "bbox": ax_spec.get("bbox", {}),
        }

        # Add geometry bbox_px if available
        if geometry:
            for ax_geom in geometry.get("axes", []):
                if ax_geom.get("id") == ax_spec.get("id"):
                    ax_merged["bbox_px"] = ax_geom.get("bbox_px", {})
                    break

        merged["axes"].append(ax_merged)  # type: ignore[attr-defined]

    # Merge traces with styles
    merged["traces"] = []
    # Build lookup for trace styles by trace_id
    trace_style_map = {}
    if style and "traces" in style:
        for ts in style.get("traces", []):
            if isinstance(ts, dict):
                trace_style_map[ts.get("trace_id", "")] = ts

    for trace in spec.get("traces", []):
        trace_merged = dict(trace)
        # Add style if available
        trace_id = trace.get("id", "")
        if trace_id in trace_style_map:
            trace_merged.update(trace_style_map[trace_id])
        merged["traces"].append(trace_merged)  # type: ignore[attr-defined]

    # Merge theme from style
    if style and "theme" in style:
        merged["theme"] = style["theme"]

    # Merge legend from style (for editor compatibility)
    if style and "legend" in style:
        legend_style = style["legend"]
        merged["legend"] = {
            "visible": legend_style.get("visible", True),
            # Use "location" key but also provide "loc" for compatibility
            "loc": legend_style.get("location", "best"),
            "location": legend_style.get("location", "best"),
            "frameon": legend_style.get("frameon", False),
            "fontsize": legend_style.get("fontsize"),
            "ncols": legend_style.get("ncols", 1),
            "title": legend_style.get("title"),
        }

    # Merge hit_regions, selectable_regions, and figure_px from geometry
    if geometry:
        if "hit_regions" in geometry:
            merged["hit_regions"] = geometry["hit_regions"]
        if "selectable_regions" in geometry:
            merged["selectable_regions"] = geometry["selectable_regions"]
        if "figure_px" in geometry:
            merged["figure_px"] = geometry["figure_px"]
        if "artists" in geometry:
            merged["artists"] = geometry["artists"]

    return merged


# EOF
