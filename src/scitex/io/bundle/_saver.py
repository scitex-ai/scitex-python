#!/usr/bin/env python3
# Timestamp: 2026-01-07
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/bundle/_saver.py

"""Bundle saving utilities.

Bundle structure (IDENTICAL for all kinds):
    bundle.zip/
    ├── canonical/              # Source of truth (editable, human-readable)
    │   ├── spec.json           # {kind, children, layout, payload_schema, ...}
    │   ├── encoding.json       # Data-to-visual mappings
    │   ├── theme.json          # Visual aesthetics
    │   ├── data_info.json      # Column metadata
    │   └── runtime.json        # Runtime configuration
    ├── payload/                # ALWAYS exists (empty for kind=figure)
    │   ├── data.csv            # Source data (for kind=plot)
    │   └── stats.json          # Statistics (for kind=stats)
    ├── artifacts/              # Derived (can be deleted and regenerated)
    │   ├── cache/
    │   │   ├── geometry_px.json
    │   │   ├── hitmap.png
    │   │   ├── hitmap.svg
    │   │   └── render_manifest.json
    │   └── exports/
    │       ├── figure.png
    │       ├── figure.svg
    │       └── figure.pdf
    └── children/               # ALWAYS exists (empty for kind=plot)
        └── {child_id}.zip
"""

import hashlib
import io
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from scitex_io.bundle._storage import Storage, get_storage

if TYPE_CHECKING:
    from scitex_io.bundle._dataclasses import DataInfo, Spec
    from .kinds._plot._dataclasses import Encoding, Theme
    from scitex_stats._dataclasses import Stats


def save_bundle_components(
    path: Path,
    spec: Optional["Spec"] = None,
    encoding: Optional["Encoding"] = None,
    theme: Optional["Theme"] = None,
    stats: Optional["Stats"] = None,
    data_info: Optional["DataInfo"] = None,
    render: bool = True,
) -> None:
    """Save all bundle components to storage.

    Uses the new canonical/artifacts/payload/children structure.

    Args:
        path: Bundle path (directory or ZIP)
        spec: Spec metadata (saved to canonical/spec.json)
        encoding: Encoding specification (saved to canonical/encoding.json)
        theme: Theme specification (saved to canonical/theme.json)
        stats: Statistics (saved to payload/stats.json for kind=stats)
        data_info: Data info metadata (saved to canonical/data_info.json)
        render: Whether to generate exports/cache (default True)
    """
    storage = get_storage(path)

    # Collect all files to write
    files = {}

    # === ALWAYS create all directories and placeholder files ===
    # Use .keep files as directory markers for ZIP compatibility
    files["canonical/.keep"] = ""
    files["payload/.keep"] = ""
    # NOTE: Don't write empty payload/data.csv - it may already contain data
    files["artifacts/.keep"] = ""
    files["artifacts/exports/.keep"] = ""
    files["artifacts/cache/.keep"] = ""
    files["children/.keep"] = ""

    # canonical/ - Source of truth
    if spec:
        files["canonical/spec.json"] = json.dumps(spec.to_dict(), indent=2)

    if encoding:
        files["canonical/encoding.json"] = encoding.to_json()

    if theme:
        files["canonical/theme.json"] = theme.to_json()

    if data_info:
        files["canonical/data_info.json"] = data_info.to_json()

    # payload/ - Data files (for leaf kinds)
    if stats and stats.analyses:
        files["payload/stats.json"] = stats.to_json()

    # Write files, preserving any existing children/ files
    # For ZIP, we need to merge with existing content
    if hasattr(storage, "write_all_preserve"):
        storage.write_all_preserve(files)
    else:
        # Fallback: write each file individually (preserves existing)
        for name, data in files.items():
            if isinstance(data, str):
                data = data.encode("utf-8")
            storage.write(name, data)


def save_render_outputs(
    storage: Storage,
    figure: Any,  # matplotlib.figure.Figure
    geometry: Dict,
    source_hash: str,
    theme_hash: str,
    renderer_version: str = "1.0.0",
    dpi: int = 300,
) -> None:
    """Save artifacts/exports/ and artifacts/cache/.

    Same structure for both kind=plot and kind=figure.

    Args:
        storage: Bundle storage
        figure: Matplotlib figure to save
        geometry: Geometry data (hit areas, element positions)
        source_hash: Hash of canonical/ for cache invalidation
        theme_hash: Hash of effective theme (after parent overrides)
        renderer_version: Renderer version for cache invalidation
        dpi: Output DPI for raster formats
    """
    # Save artifacts/exports/
    for fmt in ["png", "svg", "pdf"]:
        buf = io.BytesIO()
        figure.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight")
        storage.write(f"artifacts/exports/figure.{fmt}", buf.getvalue())

    # Save artifacts/cache/geometry_px.json
    # Add coordinate space declaration
    geometry_with_space = {
        "space": "figure_px",  # Coordinate space declaration
        **geometry,
    }
    storage.write(
        "artifacts/cache/geometry_px.json",
        json.dumps(geometry_with_space, indent=2).encode(),
    )

    # Generate and save hitmaps
    hitmap_png, hitmap_svg = generate_hitmap(figure, geometry, dpi)
    if hitmap_png:
        storage.write("artifacts/cache/hitmap.png", hitmap_png)
    if hitmap_svg:
        storage.write("artifacts/cache/hitmap.svg", hitmap_svg)

    # Save render manifest (includes cache invalidation keys)
    manifest = {
        "dpi": dpi,
        "formats": ["png", "svg", "pdf"],
        # Cache invalidation keys
        "canonical_hash": source_hash,
        "effective_theme_hash": theme_hash,
        "renderer_version": renderer_version,
    }
    storage.write(
        "artifacts/cache/render_manifest.json",
        json.dumps(manifest, indent=2).encode(),
    )


def generate_hitmap(
    figure: Any,  # matplotlib.figure.Figure
    geometry: Dict,
    dpi: int = 300,
) -> tuple:
    """Generate hitmap.png and hitmap.svg for click detection.

    Returns:
        (hitmap_png_bytes, hitmap_svg_bytes) - bytes or None if failed
    """
    # Basic implementation - generate colored regions for hit testing
    # This is a simplified version; full implementation would color-code elements
    try:
        import io

        import matplotlib.pyplot as plt

        # Create hitmap figure with same dimensions
        fig_size = figure.get_size_inches()
        hitmap_fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # Draw colored regions for each element in geometry
        elements = geometry.get("elements", [])
        for i, elem in enumerate(elements):
            if "bbox" in elem:
                bbox = elem["bbox"]
                color = plt.cm.tab20(i % 20)
                ax.add_patch(
                    plt.Rectangle(
                        (bbox.get("x", 0), bbox.get("y", 0)),
                        bbox.get("width", 0.1),
                        bbox.get("height", 0.1),
                        facecolor=color,
                        edgecolor="none",
                    )
                )

        # Save as PNG
        png_buf = io.BytesIO()
        hitmap_fig.savefig(png_buf, format="png", dpi=dpi, bbox_inches="tight")
        png_bytes = png_buf.getvalue()

        # Save as SVG
        svg_buf = io.BytesIO()
        hitmap_fig.savefig(svg_buf, format="svg", bbox_inches="tight")
        svg_bytes = svg_buf.getvalue()

        plt.close(hitmap_fig)
        return png_bytes, svg_bytes

    except Exception:
        # If hitmap generation fails, return None (non-critical)
        return None, None


def compute_canonical_hash(storage: Storage) -> str:
    """Compute hash of canonical/ directory for cache invalidation."""
    hasher = hashlib.sha256()

    canonical_files = [
        "canonical/spec.json",
        "canonical/encoding.json",
        "canonical/theme.json",
        "canonical/data_info.json",
    ]

    for filepath in canonical_files:
        if storage.exists(filepath):
            data = storage.read(filepath)
            hasher.update(data)

    return hasher.hexdigest()[:16]


def compute_theme_hash(theme: Optional["Theme"]) -> str:
    """Compute hash of theme for cache invalidation."""
    if theme is None:
        return "default"

    hasher = hashlib.sha256()
    hasher.update(theme.to_json().encode())
    return hasher.hexdigest()[:16]


__all__ = [
    "save_bundle_components",
    "save_render_outputs",
    "generate_hitmap",
    "compute_canonical_hash",
    "compute_theme_hash",
]

# EOF
