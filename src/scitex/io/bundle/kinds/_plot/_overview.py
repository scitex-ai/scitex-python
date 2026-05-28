#!/usr/bin/env python3
"""Umbrella-internal montage preview for legacy ``.plot`` directory bundles.

``generate_bundle_overview`` renders an at-a-glance dashboard image
(``{basename}_overview.png``) showing the bundle's CSV stats, JSON tree,
saved PNG + hitmap, SVG sizes, an overlay diff, and an alignment
validation panel. It runs as a best-effort post-save hook from
``save_plot_bundle``.

Kept as umbrella presentation (not in figrecipe) — figrecipe deliberately
has no overview synthesizer (see ``GITIGNORED/tasks/RESUME.md`` "Known
gaps").
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def generate_bundle_overview(
    dir_path: Path, spec: Dict, data: Dict, basename: str = "plot"
) -> None:
    """Render a multi-panel overview image of bundle contents.

    Parameters
    ----------
    dir_path : Path
        Bundle directory path.
    spec : dict
        Bundle specification (rendered as a tree).
    data : dict
        Bundle data dictionary (CSV is summarised).
    basename : str
        Base filename for bundle files (e.g., ``"myplot"``).
    """
    import matplotlib.gridspec as gridspec
    import matplotlib.pyplot as plt
    from figrecipe.presets import get_preview_dpi
    from PIL import Image

    fig = plt.figure(figsize=(16, 10), facecolor="white")
    gs = gridspec.GridSpec(
        2,
        4,
        figure=fig,
        hspace=0.3,
        wspace=0.3,
        left=0.05,
        right=0.95,
        top=0.92,
        bottom=0.05,
    )

    bundle_name = dir_path.name
    fig.suptitle(f"Bundle Overview: {bundle_name}", fontsize=16, fontweight="bold")

    # === Panel 1: CSV Statistics ===
    ax_csv = fig.add_subplot(gs[0, 0])
    ax_csv.set_title("CSV Data", fontweight="bold", fontsize=11)
    ax_csv.axis("off")

    csv_text: List[str] = []
    if "data" in data and hasattr(data["data"], "columns"):
        df = data["data"]
        csv_text.append(f"Rows: {len(df)}")
        csv_text.append(f"Columns: {len(df.columns)}")
        csv_text.append("")
        csv_text.append("Columns:")
        for col in df.columns[:10]:
            dtype = str(df[col].dtype)
            csv_text.append(f"  • {col} ({dtype})")
        if len(df.columns) > 10:
            csv_text.append(f"  ... +{len(df.columns) - 10} more")
    else:
        csv_text.append("No CSV data")

    ax_csv.text(
        0.05,
        0.95,
        "\n".join(csv_text),
        transform=ax_csv.transAxes,
        fontsize=9,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8),
    )

    # === Panel 2: JSON Tree ===
    ax_json = fig.add_subplot(gs[0, 1])
    ax_json.set_title("JSON Structure", fontweight="bold", fontsize=11)
    ax_json.axis("off")

    json_lines = _json_to_tree(spec, max_depth=4, max_keys=8, max_lines=25)
    ax_json.text(
        0.02,
        0.98,
        "\n".join(json_lines),
        transform=ax_json.transAxes,
        fontsize=7,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8),
    )

    # === Panel 3: PNG Image ===
    ax_png = fig.add_subplot(gs[0, 2])
    ax_png.set_title(f"{basename}.png", fontweight="bold", fontsize=11)
    png_path = dir_path / f"{basename}.png"
    if png_path.exists():
        png_img = Image.open(png_path)
        ax_png.imshow(png_img)
        ax_png.set_xlabel(f"{png_img.size[0]}×{png_img.size[1]}", fontsize=9)
    ax_png.axis("off")

    # === Panel 4: Hitmap PNG ===
    ax_hitmap = fig.add_subplot(gs[0, 3])
    ax_hitmap.set_title(f"{basename}_hitmap.png", fontweight="bold", fontsize=11)
    hitmap_path = dir_path / f"{basename}_hitmap.png"
    if hitmap_path.exists():
        hitmap_img = Image.open(hitmap_path)
        ax_hitmap.imshow(hitmap_img)
        ax_hitmap.set_xlabel(f"{hitmap_img.size[0]}×{hitmap_img.size[1]}", fontsize=9)
    ax_hitmap.axis("off")

    # === Panel 5: SVG info ===
    ax_svg = fig.add_subplot(gs[1, 0])
    ax_svg.set_title(f"{basename}.svg", fontweight="bold", fontsize=11)
    svg_path = dir_path / f"{basename}.svg"
    if svg_path.exists():
        svg_size = svg_path.stat().st_size
        ax_svg.text(
            0.5,
            0.5,
            f"SVG File\n{svg_size / 1_024:.1f} KB",
            transform=ax_svg.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="round", facecolor="#e0e0ff"),
        )
    ax_svg.axis("off")

    # === Panel 6: Hitmap SVG ===
    ax_hitmap_svg = fig.add_subplot(gs[1, 1])
    ax_hitmap_svg.set_title(f"{basename}_hitmap.svg", fontweight="bold", fontsize=11)
    hitmap_svg_path = dir_path / f"{basename}_hitmap.svg"
    if hitmap_svg_path.exists():
        svg_size = hitmap_svg_path.stat().st_size
        ax_hitmap_svg.text(
            0.5,
            0.5,
            f"SVG Hitmap\n{svg_size / 1_024:.1f} KB",
            transform=ax_hitmap_svg.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="round", facecolor="#ffe0e0"),
        )
    ax_hitmap_svg.axis("off")

    # === Panel 7: PNG vs Hitmap Diff ===
    ax_diff = fig.add_subplot(gs[1, 2])
    ax_diff.set_title("PNG vs Hitmap (Overlay)", fontweight="bold", fontsize=11)
    if png_path.exists() and hitmap_path.exists():
        png_arr = np.array(Image.open(png_path).convert("RGB"))
        hitmap_arr = np.array(Image.open(hitmap_path).convert("RGB"))

        if png_arr.shape == hitmap_arr.shape:
            overlay = np.zeros_like(png_arr)
            overlay[:, :, 0] = hitmap_arr[:, :, 0]
            overlay[:, :, 2] = np.mean(png_arr, axis=2).astype(np.uint8)
            overlay[:, :, 1] = 128
            ax_diff.imshow(overlay)
            ax_diff.set_xlabel("Red=Hitmap, Blue=PNG", fontsize=9)
        else:
            ax_diff.text(
                0.5,
                0.5,
                "Size mismatch!",
                transform=ax_diff.transAxes,
                ha="center",
                va="center",
                fontsize=14,
                color="red",
            )
    ax_diff.axis("off")

    # === Panel 8: Alignment Validation ===
    ax_valid = fig.add_subplot(gs[1, 3])
    ax_valid.set_title("Alignment Check", fontweight="bold", fontsize=11)
    ax_valid.axis("off")

    validation_text = _generate_alignment_validation(png_path, hitmap_path)
    color = (
        "green"
        if all(
            "✓" in t for t in validation_text if t.startswith("✓") or t.startswith("✗")
        )
        else "red"
    )

    ax_valid.text(
        0.05,
        0.95,
        "\n".join(validation_text),
        transform=ax_valid.transAxes,
        fontsize=9,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f0fff0" if color == "green" else "#fff0f0",
            alpha=0.8,
        ),
    )

    overview_path = dir_path / f"{basename}_overview.png"
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*tight_layout.*")
        fig.savefig(
            overview_path, dpi=get_preview_dpi(), bbox_inches="tight", facecolor="white"
        )
    plt.close(fig)


def _json_to_tree(
    obj: Any,
    prefix: str = "",
    max_depth: int = 4,
    depth: int = 0,
    max_keys: int = 6,
    max_lines: int = 30,
) -> List[str]:
    """Convert JSON to a depth-limited tree representation."""
    lines: List[str] = []
    if depth >= max_depth:
        return []

    if isinstance(obj, dict):
        items = list(obj.items())[:max_keys]
        for i, (k, v) in enumerate(items):
            is_last = i == len(items) - 1 and len(obj) <= max_keys
            branch = "└─ " if is_last else "├─ "
            next_prefix = prefix + ("   " if is_last else "│  ")

            if isinstance(v, dict):
                if depth < max_depth - 1 and v:
                    lines.append(prefix + branch + f"{k}:")
                    lines.extend(
                        _json_to_tree(
                            v, next_prefix, max_depth, depth + 1, max_keys, max_lines
                        )
                    )
                else:
                    lines.append(prefix + branch + f"{k}: {{{len(v)} keys}}")
            elif isinstance(v, list):
                lines.append(prefix + branch + f"{k}: [{len(v)} items]")
            else:
                val_str = str(v)
                if len(val_str) > 25:
                    val_str = val_str[:22] + "..."
                lines.append(prefix + branch + f"{k}: {val_str}")

        if len(obj) > max_keys:
            lines.append(prefix + f"   ... +{len(obj) - max_keys} more")

    return lines[:max_lines]


def _generate_alignment_validation(png_path: Path, hitmap_path: Path) -> List[str]:
    """Generate alignment-check text comparing the rendered PNG to its hitmap."""
    from PIL import Image

    validation_text: List[str] = []

    if png_path.exists() and hitmap_path.exists():
        png_img = Image.open(png_path)
        hitmap_img = Image.open(hitmap_path)

        # Size check.
        size_match = png_img.size == hitmap_img.size
        validation_text.append(
            f"✓ Size match: {png_img.size}"
            if size_match
            else f"✗ Size mismatch: PNG={png_img.size}, Hitmap={hitmap_img.size}"
        )

        # Content bounds check.
        png_arr = np.array(png_img.convert("RGB"))
        hitmap_arr = np.array(hitmap_img.convert("RGB"))

        def find_bounds(arr):
            white = np.array([255, 255, 255])
            mask = np.any(np.abs(arr.astype(int) - white) > 20, axis=2)
            rows = np.any(mask, axis=1)
            cols = np.any(mask, axis=0)
            if np.any(rows) and np.any(cols):
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]
                return (int(x_min), int(y_min), int(x_max), int(y_max))
            return (0, 0, arr.shape[1], arr.shape[0])

        png_bounds = find_bounds(png_arr)
        hitmap_bounds = find_bounds(hitmap_arr)

        bounds_match = png_bounds == hitmap_bounds
        validation_text.append(
            "✓ Content aligned"
            if bounds_match
            else f"✗ Content offset: {hitmap_bounds[0] - png_bounds[0]}, {hitmap_bounds[1] - png_bounds[1]}"
        )

        validation_text.append("")
        validation_text.append(f"PNG bounds: {png_bounds}")
        validation_text.append(f"Hitmap bounds: {hitmap_bounds}")
    else:
        validation_text.append("Files not found")

    return validation_text


__all__: List[str] = [
    "generate_bundle_overview",
]
