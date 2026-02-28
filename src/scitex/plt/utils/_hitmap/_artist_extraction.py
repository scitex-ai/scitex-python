#!/usr/bin/env python3
# Timestamp: "2026-01-24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/plt/utils/_hitmap/_artist_extraction.py

"""
Artist extraction functions for hitmap generation.

This module provides functions to extract selectable artists from matplotlib
figures and detect logical groups (histogram, bar series, etc.).
"""

from typing import Any, Dict, List, Optional, Tuple

import matplotlib.axes as _mpl_axes

__all__ = [
    "get_all_artists",
    "get_all_artists_with_groups",
    "detect_logical_groups",
]


def _get_flat_axes(fig) -> List[Any]:
    """Return a flat list of matplotlib Axes from a figure.

    RecordingFigure (from stx.plt.subplots) may expose fig.axes as a nested
    list such as [[ax1], [ax2]], whereas plain matplotlib uses [ax1, ax2].
    This helper normalises both cases.
    """
    raw = fig.axes if hasattr(fig, "axes") else []
    flat: List[Any] = []
    for item in raw:
        if isinstance(item, (list, tuple)):
            for subitem in item:
                if isinstance(subitem, _mpl_axes.Axes):
                    flat.append(subitem)
        elif isinstance(item, _mpl_axes.Axes):
            flat.append(item)
    return flat


def get_all_artists(fig, include_text: bool = False) -> List[Tuple[Any, int, str]]:
    """
    Extract all selectable artists from a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to extract artists from.
    include_text : bool
        Whether to include text elements.

    Returns
    -------
    list of tuple
        List of (artist, axes_index, artist_type) tuples.
    """
    artists = []

    for ax_idx, ax in enumerate(_get_flat_axes(fig)):
        # Lines (Line2D)
        for line in ax.get_lines():
            label = line.get_label()
            if not label.startswith("_"):  # Skip internal lines
                artists.append((line, ax_idx, "line"))

        # Scatter plots (PathCollection)
        for coll in ax.collections:
            coll_type = type(coll).__name__
            if "PathCollection" in coll_type:
                artists.append((coll, ax_idx, "scatter"))
            elif "PolyCollection" in coll_type or "FillBetween" in coll_type:
                artists.append((coll, ax_idx, "fill"))
            elif "QuadMesh" in coll_type:
                artists.append((coll, ax_idx, "mesh"))

        # Bars (Rectangle patches in containers)
        for container in ax.containers:
            if hasattr(container, "patches") and container.patches:
                artists.append((container, ax_idx, "bar"))

        # Individual patches (rectangles, circles, etc.)
        for patch in ax.patches:
            patch_type = type(patch).__name__
            if patch_type == "Rectangle":
                artists.append((patch, ax_idx, "rectangle"))
            elif patch_type in ("Circle", "Ellipse"):
                artists.append((patch, ax_idx, "circle"))
            elif patch_type == "Polygon":
                artists.append((patch, ax_idx, "polygon"))

        # Images
        for img in ax.images:
            artists.append((img, ax_idx, "image"))

        # Text (optional)
        if include_text:
            for text in ax.texts:
                if text.get_text():
                    artists.append((text, ax_idx, "text"))

    return artists


def detect_logical_groups(fig) -> Dict[str, Dict[str, Any]]:
    """
    Detect logical groups in a matplotlib figure.

    Logical groups represent high-level plot elements that may consist of
    multiple physical matplotlib artists. For example:
    - Histogram: Many Rectangle patches grouped as one "histogram"
    - Bar series: BarContainer with multiple bars
    - Box plot: Box, whiskers, caps, median, fliers as one "boxplot"
    - Error bars: Line + error caps as one "errorbar"

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to analyze.

    Returns
    -------
    dict
        Dictionary mapping group_id to group info.
    """
    groups = {}
    group_counter = {}

    def get_group_id(group_type: str, ax_idx: int) -> str:
        """Generate unique group ID."""
        key = f"{group_type}_{ax_idx}"
        if key not in group_counter:
            group_counter[key] = 0
        idx = group_counter[key]
        group_counter[key] += 1
        return f"{group_type}_{ax_idx}_{idx}"

    for ax_idx, ax in enumerate(_get_flat_axes(fig)):
        # Detect BarContainers (covers bar charts and histograms)
        bar_containers = [
            c for c in ax.containers if "BarContainer" in type(c).__name__
        ]
        n_bar_containers = len(bar_containers)

        for container in ax.containers:
            container_type = type(container).__name__

            if "BarContainer" in container_type:
                patches = (
                    list(container.patches) if hasattr(container, "patches") else []
                )
                if not patches:
                    continue

                # Check if bars are adjacent (histogram) or spaced (bar chart)
                is_histogram = False
                if len(patches) > 1:
                    widths = [p.get_width() for p in patches]
                    x_positions = [p.get_x() for p in patches]
                    if len(x_positions) > 1:
                        gaps = [
                            x_positions[i + 1] - (x_positions[i] + widths[i])
                            for i in range(len(x_positions) - 1)
                        ]
                        avg_width = sum(widths) / len(widths)
                        is_histogram = all(abs(g) < avg_width * 0.1 for g in gaps)

                if is_histogram:
                    group_type = "histogram"
                    group_id = get_group_id(group_type, ax_idx)
                    label = ""
                    if hasattr(container, "get_label"):
                        label = container.get_label()
                    if not label or label.startswith("_"):
                        label = f"{group_type}_{len([g for g in groups if group_type in g])}"

                    groups[group_id] = {
                        "type": group_type,
                        "label": label,
                        "axes_index": ax_idx,
                        "artists": patches,
                        "artist_types": ["rectangle"] * len(patches),
                        "role": "logical",
                        "member_count": len(patches),
                    }

                elif n_bar_containers > 1:
                    group_type = "bar_series"
                    group_id = get_group_id(group_type, ax_idx)
                    label = ""
                    if hasattr(container, "get_label"):
                        label = container.get_label()
                    if not label or label.startswith("_"):
                        label = f"{group_type}_{len([g for g in groups if group_type in g])}"

                    groups[group_id] = {
                        "type": group_type,
                        "label": label,
                        "axes_index": ax_idx,
                        "artists": patches,
                        "artist_types": ["rectangle"] * len(patches),
                        "role": "logical",
                        "member_count": len(patches),
                    }

            elif "ErrorbarContainer" in container_type:
                group_id = get_group_id("errorbar", ax_idx)
                artists = []
                artist_types = []

                if hasattr(container, "lines"):
                    data_line, caplines, barlinecols = container.lines
                    if data_line:
                        artists.append(data_line)
                        artist_types.append("line")
                    artists.extend(caplines)
                    artist_types.extend(["line"] * len(caplines))
                    artists.extend(barlinecols)
                    artist_types.extend(["line_collection"] * len(barlinecols))

                label = container.get_label() if hasattr(container, "get_label") else ""
                if not label or label.startswith("_"):
                    label = f"errorbar_{len([g for g in groups if 'errorbar' in g])}"

                groups[group_id] = {
                    "type": "errorbar",
                    "label": label,
                    "axes_index": ax_idx,
                    "artists": artists,
                    "artist_types": artist_types,
                    "role": "logical",
                    "member_count": len(artists),
                }

        # Detect pie charts (Wedge patches)
        wedges = [p for p in ax.patches if type(p).__name__ == "Wedge"]
        if wedges:
            group_id = get_group_id("pie", ax_idx)
            groups[group_id] = {
                "type": "pie",
                "label": "Pie Chart",
                "axes_index": ax_idx,
                "artists": wedges,
                "artist_types": ["wedge"] * len(wedges),
                "role": "logical",
                "member_count": len(wedges),
            }

        # Detect contour sets
        poly_collections = [
            c
            for c in ax.collections
            if "PolyCollection" in type(c).__name__
            and hasattr(c, "get_array")
            and c.get_array() is not None
        ]
        if len(poly_collections) > 2:
            group_id = get_group_id("contour", ax_idx)
            groups[group_id] = {
                "type": "contour",
                "label": "Contour Plot",
                "axes_index": ax_idx,
                "artists": poly_collections,
                "artist_types": ["poly_collection"] * len(poly_collections),
                "role": "logical",
                "member_count": len(poly_collections),
            }

    return groups


def get_all_artists_with_groups(
    fig, include_text: bool = False
) -> Tuple[List[Tuple[Any, int, str, Optional[str]]], Dict[str, Dict[str, Any]]]:
    """
    Extract all selectable artists from a figure with logical group information.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to extract artists from.
    include_text : bool
        Whether to include text elements.

    Returns
    -------
    tuple
        (artists_list, groups_dict) where:
        - artists_list: List of (artist, axes_index, artist_type, group_id) tuples
        - groups_dict: Dictionary of logical groups
    """
    groups = detect_logical_groups(fig)

    artist_to_group = {}
    for group_id, group_info in groups.items():
        for artist in group_info["artists"]:
            artist_to_group[id(artist)] = group_id

    artists_with_groups = []

    for ax_idx, ax in enumerate(_get_flat_axes(fig)):
        # Lines
        for line in ax.get_lines():
            label = line.get_label()
            if not label.startswith("_"):
                group_id = artist_to_group.get(id(line))
                artists_with_groups.append((line, ax_idx, "line", group_id))

        # Collections
        for coll in ax.collections:
            coll_type = type(coll).__name__
            group_id = artist_to_group.get(id(coll))
            if "PathCollection" in coll_type:
                artists_with_groups.append((coll, ax_idx, "scatter", group_id))
            elif "PolyCollection" in coll_type or "FillBetween" in coll_type:
                artists_with_groups.append((coll, ax_idx, "fill", group_id))
            elif "QuadMesh" in coll_type:
                artists_with_groups.append((coll, ax_idx, "mesh", group_id))

        # Bars
        processed_patches = set()
        for container in ax.containers:
            if hasattr(container, "patches") and container.patches:
                group_id = artist_to_group.get(id(container.patches[0]))
                if group_id:
                    artists_with_groups.append((container, ax_idx, "bar", group_id))
                    for patch in container.patches:
                        processed_patches.add(id(patch))
                else:
                    for patch in container.patches:
                        artists_with_groups.append((patch, ax_idx, "rectangle", None))
                        processed_patches.add(id(patch))

        # Patches
        for patch in ax.patches:
            if id(patch) in processed_patches:
                continue
            patch_type = type(patch).__name__
            group_id = artist_to_group.get(id(patch))
            if patch_type == "Rectangle":
                artists_with_groups.append((patch, ax_idx, "rectangle", group_id))
            elif patch_type in ("Circle", "Ellipse"):
                artists_with_groups.append((patch, ax_idx, "circle", group_id))
            elif patch_type == "Polygon":
                artists_with_groups.append((patch, ax_idx, "polygon", group_id))
            elif patch_type == "Wedge":
                artists_with_groups.append((patch, ax_idx, "wedge", group_id))

        # Images
        for img in ax.images:
            group_id = artist_to_group.get(id(img))
            artists_with_groups.append((img, ax_idx, "image", group_id))

        # Text
        if include_text:
            for text in ax.texts:
                if text.get_text():
                    group_id = artist_to_group.get(id(text))
                    artists_with_groups.append((text, ax_idx, "text", group_id))

    return artists_with_groups, groups


# EOF
