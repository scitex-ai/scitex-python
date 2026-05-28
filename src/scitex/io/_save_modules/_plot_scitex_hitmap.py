#!/usr/bin/env python3

"""Hitmap geometry + image export for the scitex `.plot` bundle.

The element-selection hitmap (per-artist ID colors, path/region geometry for
GUI hit-testing) is owned by figrecipe — this is a thin helper that drives
``figrecipe._hitmap`` for the bundle's ``cache/`` artifacts.
"""

import json


def save_hitmap_geometry_and_images(fig, cache_dir, dpi):
    """Write ``cache/geometry_px.json`` + ``cache/hitmap.{png,svg}``.

    Best-effort: silently skips if hitmap extraction fails (e.g. a backend
    without the artists figrecipe expects), so bundle saving never breaks on
    the optional GUI hit-areas.
    """
    try:
        from figrecipe._hitmap import (
            HITMAP_AXES_COLOR,
            HITMAP_BACKGROUND_COLOR,
            apply_hitmap_colors,
            as_mpl_figure,
            extract_path_data,
            extract_selectable_regions,
            restore_original_colors,
        )

        # Normalise figrecipe RecordingFigure -> matplotlib Figure so the
        # facecolor loop below sees a flat fig.axes of real Axes.
        fig = as_mpl_figure(fig)

        geometry = {
            "path_data": extract_path_data(fig),
            "selectable_regions": extract_selectable_regions(fig),
        }
        with open(cache_dir / "geometry_px.json", "w") as f:
            json.dump(geometry, f, indent=2)

        # Generate hitmap images
        axes_list = list(fig.axes) if hasattr(fig.axes, "__iter__") else [fig.axes]
        original_props, color_map, groups = apply_hitmap_colors(fig)

        # Store and set hitmap colors
        saved_fig_facecolor = fig.patch.get_facecolor()
        saved_ax_facecolors = []
        for ax in axes_list:
            saved_ax_facecolors.append(ax.get_facecolor())
            ax.set_facecolor(HITMAP_BACKGROUND_COLOR)
            for spine in ax.spines.values():
                spine.set_color(HITMAP_AXES_COLOR)
        fig.patch.set_facecolor(HITMAP_BACKGROUND_COLOR)

        # Save hitmap PNG
        fig.savefig(
            cache_dir / "hitmap.png",
            dpi=dpi,
            format="png",
            facecolor=HITMAP_BACKGROUND_COLOR,
        )

        # Save hitmap SVG
        fig.savefig(
            cache_dir / "hitmap.svg",
            format="svg",
            facecolor=HITMAP_BACKGROUND_COLOR,
        )

        # Restore colors
        restore_original_colors(original_props)
        fig.patch.set_facecolor(saved_fig_facecolor)
        for i, ax in enumerate(axes_list):
            ax.set_facecolor(saved_ax_facecolors[i])

    except Exception:
        pass  # Skip if hitmap extraction fails


# EOF
