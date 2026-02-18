#!/usr/bin/env python3
# Timestamp: "2025-12-08 23:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/gallery/_generate.py

"""Gallery generation functionality."""

import json
from pathlib import Path

import numpy as np

from ._plots import PLOT_FUNCTIONS
from ._registry import CATEGORIES


def generate(  # noqa: C901
    output_dir="./gallery",
    category=None,
    plot_type=None,
    figsize=(4, 3),
    dpi=150,
    save_csv=True,
    save_png=True,
    save_svg=True,
    save_plot=True,
    verbose=True,
):
    """Generate gallery plots with CSVs and optional .plot bundles.

    Parameters
    ----------
    output_dir : str or Path
        Output directory for the gallery.
    category : str, optional
        Generate only plots in this category.
        Available: line, statistical, distribution, categorical, scatter,
                   area, grid, contour, vector, special
    plot_type : str, optional
        Generate only this specific plot type.
    figsize : tuple
        Figure size (width, height) in inches.
    dpi : int
        Resolution for PNG output.
    save_csv : bool
        Whether to save CSV data files.
    save_png : bool
        Whether to save PNG image files.
    save_svg : bool
        Whether to save SVG image files for element selection.
    save_plot : bool
        Whether to save .plot bundles (reproducible plot packages).
    verbose : bool
        Print progress messages.

    Returns
    -------
    dict
        Dictionary with generated file paths.

    Examples
    --------
    >>> import scitex as stx
    >>> stx.plt.gallery.generate("./my_gallery")
    >>> stx.plt.gallery.generate("./my_gallery", category="line")
    >>> stx.plt.gallery.generate("./my_gallery", plot_type="scatter")
    """
    import scitex as stx
    from scitex.plt.styles.presets import SCITEX_STYLE

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which plots to generate
    plots_to_generate = _get_plots_to_generate(category, plot_type)

    if verbose:
        print(f"Generating {len(plots_to_generate)} plots to {output_dir}")

    results = {"png": [], "svg": [], "csv": [], "plot": [], "errors": []}  # type: ignore[var-annotated]

    for plot_name in plots_to_generate:
        if plot_name not in PLOT_FUNCTIONS:
            if verbose:
                print(f"  [SKIP] {plot_name}: not implemented")
            continue

        plot_func = PLOT_FUNCTIONS[plot_name]
        cat_name = _get_category_for_plot(plot_name)

        # Create category subdirectory
        cat_dir = output_dir / cat_name
        cat_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create figure
            style = SCITEX_STYLE.copy()
            style["figsize"] = figsize
            fig, ax = stx.plt.subplots(**style)

            # Generate plot
            fig, ax = plot_func(fig, ax, stx)

            # Save as .plot bundle - this is the single source of truth
            # All other formats (PNG, SVG, CSV, hitmap) are extracted from the bundle
            plot_path = cat_dir / f"{plot_name}.plot"
            stx.io.save(fig, plot_path, dpi=dpi)

            if verbose:
                print(f"  [PLTZ] {plot_path}")

            # Extract files from bundle to gallery directory
            # The plot bundle contains: plot.png, plot.svg, plot.pdf, plot.csv, plot.json, plot_hitmap.png
            import shutil

            if save_png:
                bundle_png = plot_path / "plot.png"
                gallery_png = cat_dir / f"{plot_name}.png"
                if bundle_png.exists():
                    shutil.copy(bundle_png, gallery_png)
                    results["png"].append(str(gallery_png))
                    if verbose:
                        from PIL import Image

                        with Image.open(gallery_png) as img:
                            print(
                                f"  [PNG] {gallery_png} ({img.size[0]}x{img.size[1]})"
                            )

            if save_csv:
                bundle_csv = plot_path / "plot.csv"
                gallery_csv = cat_dir / f"{plot_name}.csv"
                if bundle_csv.exists():
                    shutil.copy(bundle_csv, gallery_csv)
                    results["csv"].append(str(gallery_csv))
                    if verbose:
                        print(f"  [CSV] {gallery_csv}")

            if save_svg:
                bundle_svg = plot_path / "plot.svg"
                gallery_svg = cat_dir / f"{plot_name}.svg"
                if bundle_svg.exists():
                    shutil.copy(bundle_svg, gallery_svg)
                    results["svg"].append(str(gallery_svg))
                    if verbose:
                        print(f"  [SVG] {gallery_svg}")

            # Copy hitmap from bundle
            bundle_hitmap = plot_path / "plot_hitmap.png"
            gallery_hitmap = cat_dir / f"{plot_name}_hitmap.png"
            if bundle_hitmap.exists():
                shutil.copy(bundle_hitmap, gallery_hitmap)
                if verbose:
                    from PIL import Image

                    with Image.open(gallery_hitmap) as img:
                        print(
                            f"  [HITMAP] {gallery_hitmap} ({img.size[0]}x{img.size[1]})"
                        )

            # Copy and update JSON from bundle
            bundle_json = plot_path / "plot.json"
            gallery_json = cat_dir / f"{plot_name}.json"
            if bundle_json.exists():
                shutil.copy(bundle_json, gallery_json)
                # Add element_bboxes to the copied JSON
                _add_element_bboxes_to_json(fig, ax, dpi, gallery_json, verbose)

            if save_plot:
                results["plot"].append(str(plot_path))
            else:
                # Remove bundle if not requested
                shutil.rmtree(plot_path)

            stx.plt.close(fig._fig_mpl if hasattr(fig, "_fig_mpl") else fig)

        except Exception as e:
            results["errors"].append({"plot": plot_name, "error": str(e)})
            if verbose:
                print(f"  [ERROR] {plot_name}: {e}")

    if verbose:
        print(
            f"\nGenerated: {len(results['png'])} PNG, {len(results['svg'])} SVG, {len(results['csv'])} CSV, {len(results['plot'])} PLTZ"
        )
        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")

    return results


def _get_plots_to_generate(category=None, plot_type=None):
    """Get list of plots to generate based on filters."""
    if plot_type is not None:
        return [plot_type]

    if category is not None:
        if category not in CATEGORIES:
            raise ValueError(
                f"Unknown category: {category}. Available: {list(CATEGORIES.keys())}"
            )
        return CATEGORIES[category]["plots"]

    # All plots
    all_plots = []  # type: ignore[var-annotated]
    for cat_info in CATEGORIES.values():
        all_plots.extend(cat_info["plots"])
    return all_plots


def _get_category_for_plot(plot_name):
    """Find which category a plot belongs to."""
    for cat_name, cat_info in CATEGORIES.items():
        if plot_name in cat_info["plots"]:
            return cat_name
    return "uncategorized"


def _add_element_bboxes_to_json(fig, ax, dpi, json_path, verbose=True):
    """Add element_bboxes to an existing JSON metadata file.

    Extracts bounding boxes and path_simplified for all figure elements
    to enable interactive element selection in web editors.

    Parameters
    ----------
    fig : FigureWrapper or matplotlib.figure.Figure
        The figure object
    ax : AxisWrapper or matplotlib.axes.Axes
        The axes object
    dpi : int
        DPI used for saving
    json_path : Path
        Path to the JSON file to update
    verbose : bool
        Print progress messages
    """
    from PIL import Image

    try:
        # Get matplotlib objects
        mpl_fig = fig._fig_mpl if hasattr(fig, "_fig_mpl") else fig
        mpl_ax = ax._ax_mpl if hasattr(ax, "_ax_mpl") else ax

        # Get renderer
        try:
            renderer = mpl_fig.canvas.get_renderer()
        except Exception:
            mpl_fig.canvas.draw()
            renderer = mpl_fig.canvas.get_renderer()

        # Get saved image dimensions (needed for coordinate transformation)
        png_path = json_path.with_suffix(".png")
        if png_path.exists():
            with Image.open(png_path) as img:
                img_width, img_height = img.size
        else:
            # Fallback to figure dimensions
            img_width = int(mpl_fig.get_figwidth() * dpi)
            img_height = int(mpl_fig.get_figheight() * dpi)

        # Extract element bboxes using the same logic as vis_app
        element_bboxes = _extract_element_bboxes_for_gallery(
            mpl_fig, mpl_ax, renderer, img_width, img_height
        )

        if not element_bboxes:
            return

        # Load existing JSON
        with open(json_path) as f:
            metadata = json.load(f)

        # Add element_bboxes
        metadata["element_bboxes"] = element_bboxes

        # Also ensure figure_size_px is present
        if "dimensions" not in metadata:
            metadata["dimensions"] = {}
        metadata["dimensions"]["figure_size_px"] = {
            "width": img_width,
            "height": img_height,
        }

        # Save updated JSON
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=4)

        if verbose:
            print(
                f"  [BBOXES] Added {len(element_bboxes)} element bboxes to {json_path.name}"
            )

    except Exception as e:
        if verbose:
            print(f"  [WARN] Could not add element_bboxes: {e}")


def _extract_element_bboxes_for_gallery(  # noqa: C901
    fig, ax, renderer, img_width, img_height
):
    """Extract element bounding boxes for gallery figures.

    Similar to vis_app's extract_element_bboxes but simplified for gallery use.
    """
    import numpy as np

    # Get figure tight bbox in inches
    fig_bbox = fig.get_tightbbox(renderer)
    tight_x0 = fig_bbox.x0
    tight_y0 = fig_bbox.y0
    tight_width = fig_bbox.width
    tight_height = fig_bbox.height

    # bbox_inches='tight' adds pad_inches around the tight bbox
    pad_inches = 0.1
    saved_width_inches = tight_width + 2 * pad_inches
    saved_height_inches = tight_height + 2 * pad_inches

    # Scale factors for converting inches to pixels
    scale_x = img_width / saved_width_inches
    scale_y = img_height / saved_height_inches

    bboxes = {}

    def get_element_bbox(element, name):
        """Get element bbox in image pixel coordinates."""
        try:
            bbox = element.get_window_extent(renderer)
            if not (
                np.isfinite(bbox.x0)
                and np.isfinite(bbox.x1)
                and np.isfinite(bbox.y0)
                and np.isfinite(bbox.y1)
            ):
                return

            elem_x0_inches = bbox.x0 / fig.dpi
            elem_x1_inches = bbox.x1 / fig.dpi
            elem_y0_inches = bbox.y0 / fig.dpi
            elem_y1_inches = bbox.y1 / fig.dpi

            x0_rel = elem_x0_inches - tight_x0 + pad_inches
            x1_rel = elem_x1_inches - tight_x0 + pad_inches
            y0_rel = saved_height_inches - (elem_y1_inches - tight_y0 + pad_inches)
            y1_rel = saved_height_inches - (elem_y0_inches - tight_y0 + pad_inches)

            bboxes[name] = {
                "x0": max(0, int(x0_rel * scale_x)),
                "y0": max(0, int(y0_rel * scale_y)),
                "x1": min(img_width, int(x1_rel * scale_x)),
                "y1": min(img_height, int(y1_rel * scale_y)),
                "label": name.replace("_", " ").title(),
            }
        except Exception:
            pass

    def coords_to_img_points(data_coords):
        """Convert data coordinates to image pixel coordinates."""
        if len(data_coords) == 0:
            return []
        transform = ax.transData
        points_display = transform.transform(data_coords)
        points_img = []
        for px, py in points_display:
            if not np.isfinite(px) or not np.isfinite(py):
                continue
            px_inches = px / fig.dpi
            py_inches = py / fig.dpi
            x_rel = px_inches - tight_x0 + pad_inches
            y_rel = saved_height_inches - (py_inches - tight_y0 + pad_inches)
            x_img = max(-10000, min(10000, int(x_rel * scale_x)))
            y_img = max(-10000, min(10000, int(y_rel * scale_y)))
            points_img.append([x_img, y_img])
        # Downsample if too many points
        if len(points_img) > 100:
            step = len(points_img) // 100
            points_img = points_img[::step]
        return points_img

    # Extract lines
    line_idx = 0
    for line in ax.get_lines():
        try:
            label = line.get_label()
            if label.startswith("_"):
                continue

            trace_name = f"trace_{line_idx}"
            get_element_bbox(line, trace_name)

            if trace_name in bboxes:
                bboxes[trace_name]["label"] = label or f"Line {line_idx}"
                bboxes[trace_name]["trace_idx"] = line_idx
                bboxes[trace_name]["element_type"] = "line"

                xdata, ydata = line.get_xdata(), line.get_ydata()
                if len(xdata) > 0:
                    # Use path_simplified for hit detection
                    bboxes[trace_name]["path_simplified"] = coords_to_img_points(
                        list(zip(xdata, ydata))
                    )
            line_idx += 1
        except Exception:
            pass

    # Extract scatter collections
    scatter_idx = 0
    for coll in ax.collections:
        try:
            coll_type = type(coll).__name__
            if coll_type == "PathCollection":
                label = coll.get_label()
                if label and label.startswith("_"):
                    label = None

                element_name = f"scatter_{scatter_idx}"
                offsets = coll.get_offsets()

                if len(offsets) > 0:
                    points_img = coords_to_img_points(offsets)
                    if points_img:
                        xs = [p[0] for p in points_img]
                        ys = [p[1] for p in points_img]
                        padding = 10
                        bboxes[element_name] = {
                            "x0": max(0, min(xs) - padding),
                            "y0": max(0, min(ys) - padding),
                            "x1": min(img_width, max(xs) + padding),
                            "y1": min(img_height, max(ys) + padding),
                            "label": label or f"Scatter {scatter_idx}",
                            "element_type": "scatter",
                            "points": points_img,
                        }
                scatter_idx += 1
        except Exception:
            pass

    # Extract bars
    bar_idx = 0
    for patch in ax.patches:
        try:
            patch_type = type(patch).__name__
            if patch_type == "Rectangle":
                label = patch.get_label()
                element_name = f"bar_{bar_idx}"
                get_element_bbox(patch, element_name)
                if element_name in bboxes:
                    bboxes[element_name]["label"] = label or f"Bar {bar_idx}"
                    bboxes[element_name]["element_type"] = "bar"
                bar_idx += 1
        except Exception:
            pass

    return bboxes


def _generate_and_save_hitmap(  # noqa: C901
    fig, dpi, hitmap_path, json_path, verbose=True, crop_box=None
):
    """Generate hitmap PNG and add color_map to JSON.

    The hitmap is generated at the same size as the PNG by:
    1. Rendering the full figure with ID colors (same as PNG before crop)
    2. Applying the exact same crop coordinates as the PNG

    Parameters
    ----------
    fig : FigureWrapper or matplotlib.figure.Figure
        The figure object (before closing)
    dpi : int
        DPI for hitmap rendering
    hitmap_path : Path
        Output path for hitmap PNG
    json_path : Path
        Path to JSON file to update with hitmap_color_map
    verbose : bool
        Print progress messages
    crop_box : tuple, optional
        Explicit crop coordinates (left, upper, right, lower) from PNG cropping.
        If provided, applies the same crop to hitmap for exact size matching.
    """
    from PIL import Image

    from scitex.plt.utils._hitmap import generate_hitmap_id_colors

    try:
        # Get matplotlib figure
        mpl_fig = fig._fig_mpl if hasattr(fig, "_fig_mpl") else fig

        # Generate hitmap at original figure size (same as PNG before cropping)
        hitmap_array, color_map = generate_hitmap_id_colors(mpl_fig, dpi=dpi)

        if not color_map:
            if verbose:
                print("  [HITMAP] No elements found to map - generating empty hitmap")
            # Still generate hitmap (all zeros/black) for consistency
            # This ensures hitmap always exists with correct size

        # Convert hitmap array to RGB PNG
        h, w = hitmap_array.shape
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
        rgb[:, :, 0] = (hitmap_array >> 16) & 0xFF
        rgb[:, :, 1] = (hitmap_array >> 8) & 0xFF
        rgb[:, :, 2] = hitmap_array & 0xFF
        hitmap_full = Image.fromarray(rgb, mode="RGB")

        # Save full hitmap first (before cropping)
        hitmap_full.save(hitmap_path, format="PNG")

        if verbose:
            print(f"  [HITMAP] Full size: {w}x{h}")

        # Apply same crop as PNG if crop_box provided
        if crop_box is not None:
            from figrecipe import crop

            crop(
                str(hitmap_path),
                output_path=str(hitmap_path),
                overwrite=True,
                crop_box=crop_box,
                verbose=False,
            )
            if verbose:
                with Image.open(hitmap_path) as cropped:
                    print(f"  [HITMAP] Cropped to: {cropped.size[0]}x{cropped.size[1]}")

        # Validate sizes match
        png_path = hitmap_path.parent / hitmap_path.name.replace("_hitmap.png", ".png")
        if png_path.exists():
            with Image.open(png_path) as png_img, Image.open(hitmap_path) as hitmap_img:
                png_size = png_img.size
                hitmap_size = hitmap_img.size
                if png_size != hitmap_size:
                    print(
                        f"  [ERROR] Size mismatch! PNG={png_size}, Hitmap={hitmap_size}"
                    )
                    raise ValueError(
                        f"Hitmap size {hitmap_size} doesn't match PNG size {png_size}"
                    )
                elif verbose:
                    print(
                        f"  [HITMAP] Size validated: {hitmap_size[0]}x{hitmap_size[1]} (matches PNG)"
                    )

        if verbose:
            print(f"  [HITMAP] {hitmap_path.name} ({len(color_map)} elements)")

        # Add hitmap_color_map to JSON
        if json_path.exists():
            with open(json_path) as f:
                metadata = json.load(f)

            # Store color_map with string keys for JSON compatibility
            metadata["hitmap_color_map"] = {str(k): v for k, v in color_map.items()}
            metadata["hitmap_file"] = hitmap_path.name

            # Store crop_box in metadata for reference
            if crop_box is not None:
                metadata["hitmap_crop_box"] = {
                    "left": int(crop_box[0]),
                    "upper": int(crop_box[1]),
                    "right": int(crop_box[2]),
                    "lower": int(crop_box[3]),
                }

            with open(json_path, "w") as f:
                json.dump(metadata, f, indent=4)

    except Exception as e:
        if verbose:
            print(f"  [WARN] Could not generate hitmap: {e}")
            import traceback

            traceback.print_exc()


# EOF
