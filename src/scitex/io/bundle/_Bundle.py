#!/usr/bin/env python3
# Timestamp: 2025-12-20
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/bundle/_Bundle.py

"""Bundle Class - Main entry point for scitex bundles.

Structure (identical for all kinds):
- canonical/: Source of truth (spec.json, encoding.json, theme.json)
- payload/: Data files (empty for composites)
- artifacts/: Exports and cache
- children/: Embedded child bundles (empty for leaves)
"""

import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ._children import ValidationError, embed_child, load_embedded_children
from scitex_io.bundle._dataclasses import DataInfo, SizeMM, Spec
from ._loader import load_bundle_components
from ._saver import (
    compute_canonical_hash,
    compute_theme_hash,
    save_bundle_components,
    save_render_outputs,
)
from scitex_io.bundle._storage import Storage, get_storage
from scitex_io.bundle._validation import ValidationResult
from .kinds._plot import Encoding, Theme
from scitex_stats._dataclasses import Stats

if TYPE_CHECKING:
    from matplotlib.figure import Figure as MplFigure


class Bundle:
    """Scitex Bundle - Self-contained figure/plot/stats package.

    Attributes
    ----------
        spec: Spec metadata (kind, children, layout, payload_schema, etc.)
        encoding: Encoding specification (traces, channels)
        theme: Theme specification (colors, fonts)
        stats: Statistics (for kind=stats)
        data_info: Data info metadata
    """

    def __init__(
        self,
        path: Union[str, Path],
        create: bool = False,
        kind: str = "plot",
        name: Optional[str] = None,
        size_mm: Optional[Dict[str, float]] = None,
        # Legacy support
        node_type: Optional[str] = None,
    ):
        """Initialize Bundle.

        Args:
            path: Bundle path (directory or .zip file)
            create: If True, create new bundle; if False, load existing
            kind: Bundle kind (plot, figure, table, stats, group, collection)
            name: Bundle name (default: stem of path)
            size_mm: Figure size in mm (e.g., {"width": 170, "height": 85})
            node_type: DEPRECATED - use 'kind' instead
        """
        self._path = Path(path)
        self._is_zip = self._path.suffix == ".zip"
        self._spec: Optional[Spec] = None
        self._encoding: Optional[Encoding] = None
        self._theme: Optional[Theme] = None
        self._stats: Optional[Stats] = None
        self._data_info: Optional[DataInfo] = None
        self._dirty = False
        self._storage: Optional[Storage] = None

        # Handle legacy node_type parameter
        if node_type is not None:
            kind = node_type

        if create:
            self._create_new(kind, name, size_mm)
        else:
            self._load()

    @property
    def path(self) -> Path:
        """Bundle path (directory or ZIP)."""
        return self._path

    @property
    def is_zip(self) -> bool:
        """Whether bundle is a ZIP file."""
        return self._is_zip

    @property
    def bundle_type(self) -> str:
        """Bundle kind (figure, plot, table, etc.)."""
        return self._spec.kind if self._spec else "unknown"

    @property
    def is_dirty(self) -> bool:
        """Whether bundle has unsaved changes."""
        return self._dirty

    @property
    def storage(self) -> Storage:
        """Get storage for this bundle."""
        if self._storage is None:
            self._storage = get_storage(self._path)
        return self._storage

    @property
    def spec(self) -> Optional[Spec]:
        """Bundle specification metadata."""
        return self._spec

    @spec.setter
    def spec(self, value: Union[Spec, Dict[str, Any]]):
        if isinstance(value, dict):
            self._spec = Spec.from_dict(value)
        else:
            self._spec = value
        self._dirty = True

    @property
    def encoding(self) -> Optional[Encoding]:
        """Encoding specification (typed object)."""
        return self._encoding

    @encoding.setter
    def encoding(self, value: Union[Encoding, Dict[str, Any]]):
        if isinstance(value, dict):
            self._encoding = Encoding.from_dict(value)
        else:
            self._encoding = value
        self._dirty = True

    @property
    def encoding_dict(self) -> Optional[Dict[str, Any]]:
        """Encoding as dictionary (for serialization)."""
        return self._encoding.to_dict() if self._encoding else None

    @property
    def theme(self) -> Optional[Theme]:
        """Theme specification (typed object)."""
        return self._theme

    @theme.setter
    def theme(self, value: Union[Theme, Dict[str, Any]]):
        if isinstance(value, dict):
            self._theme = Theme.from_dict(value)
        else:
            self._theme = value
        self._dirty = True

    @property
    def theme_dict(self) -> Optional[Dict[str, Any]]:
        """Theme as dictionary (for serialization)."""
        return self._theme.to_dict() if self._theme else None

    @property
    def stats(self) -> Optional[Stats]:
        """Statistics."""
        return self._stats

    @stats.setter
    def stats(self, value: Union[Stats, Dict[str, Any]]):
        if isinstance(value, dict):
            self._stats = Stats.from_dict(value)
        else:
            self._stats = value
        self._dirty = True

    @property
    def data_info(self) -> Optional[DataInfo]:
        """Data info metadata."""
        return self._data_info

    @data_info.setter
    def data_info(self, value: Union[DataInfo, Dict[str, Any]]):
        if isinstance(value, dict):
            self._data_info = DataInfo.from_dict(value)
        else:
            self._data_info = value
        self._dirty = True

    def _create_new(
        self,
        kind: str,
        name: Optional[str],
        size_mm: Optional[Dict[str, float]],
    ):
        """Create a new bundle."""
        bundle_id = str(uuid.uuid4())
        if name is None:
            name = self._path.stem

        # Determine payload_schema for leaf kinds
        # Note: payload_schema is optional. For plots without data, it's None.
        # For plots with data, from_matplotlib will set it.
        payload_schema = None
        if kind in Spec.LEAF_KINDS and kind != "plot":
            # Only auto-set for non-plot leaf kinds
            payload_schema_map = {
                "table": "scitex.io.bundle.payload.table@1",
                "stats": "scitex.io.bundle.payload.stats@1",
            }
            payload_schema = payload_schema_map.get(kind)

        self._spec = Spec(
            id=bundle_id,
            kind=kind,
            name=name,
            size_mm=SizeMM.from_dict(size_mm) if size_mm else None,
            payload_schema=payload_schema,
        )
        self._encoding = Encoding()
        self._theme = Theme()
        self._stats = Stats()
        self._dirty = True

    def _load(self):
        """Load existing bundle."""
        if not self._path.exists():
            raise FileNotFoundError(f"Bundle not found: {self._path}")

        (
            self._spec,
            self._encoding,
            self._theme,
            self._stats,
            self._data_info,
        ) = load_bundle_components(self._path)

    def add_child(
        self,
        child: Union[str, Path, "Bundle"],
        row: int = 0,
        col: int = 0,
        label: Optional[str] = None,
        row_span: int = 1,
        col_span: int = 1,
        **kwargs,
    ) -> str:
        """Add and embed a child bundle. Returns child_name in children/."""
        if not self.spec.is_composite_kind():
            raise TypeError(f"kind={self.spec.kind} cannot have children")

        # Get child path
        if isinstance(child, Bundle):
            child_path = child.path
        else:
            child_path = Path(child)

        # Embed child into children/ directory
        # Returns (child_name, child_id) tuple
        child_name, child_id = embed_child(self.storage, child_path)

        # Add to spec.children
        self._spec.children.append(child_name)

        # Initialize layout if needed
        if self._spec.layout is None:
            self._spec.layout = {"rows": 2, "cols": 2, "panels": []}

        # Update grid size if needed
        self._spec.layout["rows"] = max(
            self._spec.layout.get("rows", 1), row + row_span
        )
        self._spec.layout["cols"] = max(
            self._spec.layout.get("cols", 1), col + col_span
        )

        # Add to layout.panels
        panel_info = {
            "child": child_name,
            "child_id": child_id,  # Full UUID for identity tracking
            "row": row,
            "col": col,
            "row_span": row_span,
            "col_span": col_span,
            **kwargs,
        }
        if label:
            panel_info["label"] = label

        self._spec.layout["panels"].append(panel_info)
        self._dirty = True

        return child_name

    def load_children(self) -> Dict[str, "Bundle"]:
        """Load embedded children. Returns dict: child_name -> Bundle."""
        return load_embedded_children(self._path)

    def render(self) -> Optional["MplFigure"]:
        """Render figure. Composite renders children, leaf renders from encoding."""
        if self._spec is None:
            return None

        if self._spec.is_composite_kind():
            return self._render_composite()
        elif self._spec.is_data_leaf_kind():
            # Data kinds (plot, table, stats) need payload data
            return self._render_from_encoding()
        elif self._spec.is_annotation_leaf_kind():
            # Annotation kinds (text, shape) render from spec params
            return self._render_annotation()
        elif self._spec.is_image_leaf_kind():
            # Image kinds render from payload image
            return self._render_image()

        return None

    def _render_composite(self) -> Optional["MplFigure"]:
        """Render composite figure with children."""
        import figrecipe as splt

        size_mm = (
            self._spec.size_mm.to_dict()
            if self._spec.size_mm
            else {"width": 170, "height": 100}
        )

        # Get background color from theme
        bg_color = "#ffffff"
        if self._theme and self._theme.colors:
            bg_color = self._theme.colors.background or "#ffffff"

        if not self._spec.children:
            # Empty container - render blank figure with specified size and background
            fig, ax = splt.subplots(
                figsize_mm=(size_mm.get("width", 170), size_mm.get("height", 100))
            )
            fig.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            ax.set_axis_off()
            return fig

        from .kinds._figure._composite import render_composite

        children = self.load_children()

        fig, geometry = render_composite(
            children=children,
            layout=self._spec.layout or {"rows": 1, "cols": 1, "panels": []},
            size_mm=size_mm,
            theme=self._theme,
        )

        return fig

    def _render_from_encoding(self) -> Optional["MplFigure"]:
        """Render leaf figure from encoding + payload."""
        if self._encoding is None:
            return None

        import figrecipe as splt

        size_mm = (
            self._spec.size_mm.to_dict()
            if self._spec.size_mm
            else {"width": 85, "height": 85}
        )

        # Use scitex.plt for proper styling (3-4 ticks, etc.)
        fig, ax = splt.subplots(
            figsize_mm=(size_mm.get("width", 85), size_mm.get("height", 85))
        )

        # Load data from payload
        data = self._load_payload_data()

        # Render traces
        from .kinds._plot._backend._render import render_traces

        traces = self._encoding.traces if self._encoding.traces else []
        for trace in traces:
            render_traces(ax, trace, data, self._theme)

        # Apply labels from encoding axes config (if available)
        # Note: Unit validation happens in scitex.plt via UnitAwareMixin.set_xlabel/set_ylabel
        if self._encoding.axes:
            if "x" in self._encoding.axes and self._encoding.axes["x"].title:
                ax.set_xlabel(self._encoding.axes["x"].title)
            if "y" in self._encoding.axes and self._encoding.axes["y"].title:
                ax.set_ylabel(self._encoding.axes["y"].title)

        fig.tight_layout()
        return fig

    def _load_payload_data(self) -> Optional["pd.DataFrame"]:
        """Load data from payload/data.csv or legacy data/data.csv."""
        from io import StringIO

        import pandas as pd

        # Try new path first, then legacy
        for path in ["payload/data.csv", "data/data.csv"]:
            if self.storage.exists(path):
                csv_bytes = self.storage.read(path)
                # Handle empty CSV files
                if not csv_bytes.strip():
                    return None
                return pd.read_csv(StringIO(csv_bytes.decode("utf-8")))
        return None

    def _render_annotation(self) -> Optional["MplFigure"]:
        """Render annotation (text/shape) from spec parameters."""
        import figrecipe as splt

        size_mm = (
            self._spec.size_mm.to_dict()
            if self._spec.size_mm
            else {"width": 85, "height": 85}
        )

        fig, ax = splt.subplots(
            figsize_mm=(size_mm.get("width", 85), size_mm.get("height", 85))
        )

        # Get background color
        bg_color = "#ffffff"
        if self._theme and self._theme.colors:
            bg_color = self._theme.colors.background or "#ffffff"
        fig.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.set_axis_off()

        if self._spec.kind == "text":
            # Render text annotation
            text_obj = self._spec.text
            if text_obj:
                text_content = text_obj.content or self._spec.name or ""
                kwargs = {"ha": text_obj.ha, "va": text_obj.va}
                if text_obj.fontsize:
                    kwargs["fontsize"] = text_obj.fontsize
                if text_obj.fontweight:
                    kwargs["fontweight"] = text_obj.fontweight
            else:
                text_content = self._spec.name or ""
                kwargs = {"ha": "center", "va": "center"}
            ax.text(0.5, 0.5, text_content, transform=ax.transAxes, **kwargs)

        elif self._spec.kind == "shape":
            # Render shape annotation
            from scitex_io.bundle.kinds._shape import render_shape

            shape_obj = self._spec.shape
            if shape_obj:
                render_shape(
                    ax,
                    shape_type=shape_obj.shape_type,
                    x=0.2,
                    y=0.2,
                    width=0.6,
                    height=0.6,
                    facecolor=shape_obj.color if shape_obj.fill else "none",
                    edgecolor=shape_obj.color,
                    linewidth=shape_obj.linewidth,
                )

        fig.tight_layout()
        return fig

    def _render_image(self) -> Optional["MplFigure"]:
        """Render image from payload."""
        import figrecipe as splt
        import numpy as np

        size_mm = (
            self._spec.size_mm.to_dict()
            if self._spec.size_mm
            else {"width": 85, "height": 85}
        )

        fig, ax = splt.subplots(
            figsize_mm=(size_mm.get("width", 85), size_mm.get("height", 85))
        )
        ax.set_axis_off()

        # Try to find image in payload
        for ext in ["png", "jpg", "jpeg", "gif", "bmp"]:
            path = f"payload/image.{ext}"
            if self.storage.exists(path):
                from io import BytesIO

                from PIL import Image

                img_bytes = self.storage.read(path)
                img = Image.open(BytesIO(img_bytes))
                ax.imshow(np.array(img))
                break

        fig.tight_layout()
        return fig

    def _validate_manifest(self) -> tuple:
        """Validate manifest.json existence and structure.

        Returns
        -------
            Tuple of (errors: List[str], warnings: List[str])
        """
        import json

        errors = []
        warnings = []

        # Check if bundle path exists
        if not self._path.exists():
            return errors, warnings  # Can't validate non-existent bundle

        # Check manifest.json exists (required)
        manifest_path = "manifest.json"
        if not self.storage.exists(manifest_path):
            errors.append("Missing required manifest.json")
            return errors, warnings

        # Validate manifest structure
        try:
            content = self.storage.read(manifest_path)
            manifest = json.loads(content.decode("utf-8"))

            if "scitex" not in manifest:
                errors.append("manifest.json missing 'scitex' key")
            else:
                scitex = manifest["scitex"]
                if "type" not in scitex:
                    errors.append("manifest.json missing 'scitex.type'")
                if "version" not in scitex:
                    errors.append("manifest.json missing 'scitex.version'")

                # Validate type matches spec kind
                manifest_type = scitex.get("type")
                if manifest_type and self._spec:
                    # Normalize both to compare
                    from scitex_io.bundle._types import BundleType

                    normalized_manifest = BundleType.normalize(manifest_type)
                    normalized_node = BundleType.normalize(self._spec.kind)
                    if normalized_manifest != normalized_node:
                        errors.append(
                            f"Type mismatch: manifest says '{manifest_type}', "
                            f"spec says '{self._spec.kind}'"
                        )

        except json.JSONDecodeError as e:
            errors.append(f"manifest.json is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading manifest.json: {e}")

        return errors, warnings

    def validate(self, level: str = "schema") -> ValidationResult:
        """Validate bundle.

        Args:
            level: Validation level - "schema", "semantic", or "strict"

        Returns
        -------
            ValidationResult with is_valid property and errors list
        """
        result = ValidationResult(level=level)

        # Manifest validation (returns errors, warnings tuple)
        manifest_errors, manifest_warnings = self._validate_manifest()
        result.errors.extend(manifest_errors)
        result.warnings.extend(manifest_warnings)

        # Spec logical validation
        if self._spec:
            result.errors.extend(self._spec.validate())

        # Storage-level validation - check required payload files
        if self._spec and self._spec.is_leaf_kind():
            required_file = self._spec.get_required_payload_file()
            if required_file:
                # Check both new structure (payload/) and legacy structure (data/)
                # Legacy sio.save() uses data/data.csv, new Bundle uses payload/data.csv
                legacy_paths = {
                    "payload/data.csv": "data/data.csv",
                    "payload/table.csv": "data/table.csv",
                    "payload/stats.json": "stats/stats.json",
                }
                legacy_path = legacy_paths.get(required_file)
                if not self.storage.exists(required_file):
                    if not legacy_path or not self.storage.exists(legacy_path):
                        result.errors.append(
                            f"Missing required payload file: {required_file}"
                        )

        # NOTE: For composite kinds, do NOT validate payload/ emptiness by listing files.
        # Payload prohibition is enforced purely via payload_schema is None (in Spec.validate).

        # Recursively validate embedded children
        if self._spec and self._spec.is_composite_kind() and self._spec.children:
            children = self.load_children()
            for child_name, child in children.items():
                child_result = child.validate(level)
                result.errors.extend(
                    [f"{child_name}: {e}" for e in child_result.errors]
                )
                result.warnings.extend(
                    [f"{child_name}: {w}" for w in child_result.warnings]
                )

        # Schema validation for other components
        if level in ("semantic", "strict"):
            # Additional semantic validation
            if self._encoding and self._spec:
                if self._spec.is_composite_kind() and self._encoding.traces:
                    result.errors.append(
                        "Composite kinds should not have encoding traces"
                    )

        return result

    def save(
        self,
        path: Optional[Union[str, Path]] = None,
        validate: bool = True,
        validation_level: str = "schema",
        render: bool = True,
    ):
        """Save bundle to disk.

        Args:
            path: Override save path
            validate: Run validation before saving
            validation_level: Validation level
            render: Generate exports/cache (default True).
                    Set False for WIP saves (faster, spec/payload/children only).
        """
        if path:
            self._path = Path(path)
            self._is_zip = self._path.suffix == ".zip"
            self._storage = None  # Reset storage

        # Validate before saving
        if validate:
            result = self.validate(level=validation_level)
            if not result.is_valid:
                raise ValidationError(f"Validation failed: {result.errors}")

        # Update modified timestamp
        if self._spec:
            self._spec.touch()

        # Save canonical files
        save_bundle_components(
            self._path,
            spec=self._spec,
            encoding=self._encoding,
            theme=self._theme,
            stats=self._stats,
            data_info=self._data_info,
            render=render,
        )

        # Render and save exports/cache (optional)
        if render:
            fig = self.render()
            if fig:
                source_hash = compute_canonical_hash(self.storage)
                theme_hash = compute_theme_hash(self._theme)
                # Extract figure dimensions in pixels
                dpi = fig.get_dpi()
                width_px = int(fig.get_figwidth() * dpi)
                height_px = int(fig.get_figheight() * dpi)
                geometry = {
                    "figure_px": [width_px, height_px],
                }
                save_render_outputs(
                    self.storage,
                    fig,
                    geometry=geometry,
                    source_hash=source_hash,
                    theme_hash=theme_hash,
                )
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure as MplFigure

                # Handle FigWrapper from scitex.plt
                if isinstance(fig, MplFigure):
                    plt.close(fig)
                elif hasattr(fig, "figure") and isinstance(fig.figure, MplFigure):
                    plt.close(fig.figure)
                else:
                    plt.close(fig)

        self._dirty = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert bundle to dictionary."""
        result = {
            "path": str(self._path),
            "is_zip": self._is_zip,
            "kind": self.bundle_type,
        }
        if self._spec:
            result["spec"] = self._spec.to_dict()
        if self._encoding:
            result["encoding"] = self._encoding.to_dict()
        if self._theme:
            result["theme"] = self._theme.to_dict()
        if self._stats:
            result["stats"] = self._stats.to_dict()
        if self._data_info:
            result["data_info"] = self._data_info.to_dict()
        return result

    def __enter__(self) -> "Bundle":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context manager, auto-saving if dirty and no exception."""
        if exc_type is None and self._dirty:
            self.save()
        return False

    def __repr__(self) -> str:
        dirty_marker = "*" if self._dirty else ""
        kind = self._spec.kind if self._spec else "unknown"
        return f"Bundle({self._path!r}, kind={kind!r}){dirty_marker}"


# =============================================================================
# Factory Functions
# =============================================================================

# Import from_matplotlib from helper module (single source of truth)
from ._mpl_helpers import from_matplotlib


def load_bundle(path: Union[str, Path]) -> Bundle:
    """Load an existing Bundle."""
    return Bundle(path)


def create_bundle(
    path: Union[str, Path],
    kind: str = "plot",
    name: Optional[str] = None,
    size_mm: Optional[Dict[str, float]] = None,
    # Legacy support
    node_type: Optional[str] = None,
) -> Bundle:
    """Create a new Bundle."""
    if node_type is not None:
        kind = node_type
    return Bundle(path, create=True, kind=kind, name=name, size_mm=size_mm)


__all__ = ["Bundle", "load_bundle", "create_bundle", "from_matplotlib"]

# EOF
