#!/usr/bin/env python3
"""Bridge adapter for figrecipe integration.

This module provides functions to save figures with both:
- SigmaPlot-compatible CSV (scitex format)
- figrecipe YAML recipe (reproducible figures)

The FTS bundle structure:
    figure/
    ├── recipe.yaml     # Source of truth (figrecipe format)
    ├── recipe_data/    # Large arrays (if needed)
    ├── plot.csv        # SigmaPlot combined CSV (derived)
    ├── plot.png        # Primary image (derived)
    └── meta.yaml       # FTS metadata (optional)
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

# Check figrecipe availability
try:
    import figrecipe as fr
    from figrecipe._serializer import save_recipe as _fr_save_recipe

    FIGRECIPE_AVAILABLE = True
except ImportError:
    FIGRECIPE_AVAILABLE = False


def save_with_recipe(
    fig,
    path: Union[str, Path],
    include_csv: bool = True,
    include_recipe: bool = True,
    data_format: str = "csv",
    dpi: int = 300,
    **kwargs,
) -> Dict[str, Path]:
    """Save figure with both CSV and figrecipe recipe.

    Parameters
    ----------
    fig : FigWrapper or matplotlib Figure
        The figure to save.
    path : str or Path
        Output path. Can be:
        - Directory path (creates bundle)
        - File path with .zip extension (creates zip bundle)
        - File path with image extension (saves image + sidecar files)
    include_csv : bool
        If True, save SigmaPlot-compatible CSV.
    include_recipe : bool
        If True, save figrecipe YAML recipe (requires figrecipe).
    data_format : str
        Format for recipe data: 'csv', 'npz', or 'inline'.
    dpi : int
        Resolution for image output.
    **kwargs
        Additional arguments passed to savefig (including facecolor).

    Returns
    -------
    dict
        Paths to saved files: {'image': Path, 'csv': Path, 'recipe': Path}
    """
    from scitex.io.bundle._bundle._storage import get_storage

    path = Path(path)
    result = {}

    # Determine if this is a bundle (directory or zip)
    is_bundle = path.suffix == ".zip" or path.suffix == "" or path.is_dir()

    if is_bundle:
        # Create bundle storage
        storage = get_storage(path)
        storage.ensure_exists()

        # 1. Save image - use fig.savefig() to get facecolor fix from FigWrapper
        image_path = storage.path / "plot.png"
        _save_figure_image(fig, image_path, dpi=dpi, **kwargs)
        result["image"] = image_path

        # 2. Save SigmaPlot CSV
        if include_csv and hasattr(fig, "export_as_csv"):
            try:
                csv_df = fig.export_as_csv()
                if not csv_df.empty:
                    csv_path = storage.path / "plot.csv"
                    csv_df.to_csv(csv_path, index=False)
                    result["csv"] = csv_path
            except Exception:
                pass  # CSV export is optional

        # 3. Save figrecipe recipe
        if include_recipe:
            recipe_path = _save_recipe_to_path(
                fig, storage.path / "recipe.yaml", data_format
            )
            if recipe_path:
                result["recipe"] = recipe_path

    else:
        # Single file save (image + sidecars)
        _save_figure_image(fig, path, dpi=dpi, **kwargs)
        result["image"] = path

        # Save CSV sidecar
        if include_csv and hasattr(fig, "export_as_csv"):
            try:
                csv_df = fig.export_as_csv()
                if not csv_df.empty:
                    csv_path = path.with_suffix(".csv")
                    csv_df.to_csv(csv_path, index=False)
                    result["csv"] = csv_path
            except Exception:
                pass

        # Save recipe sidecar
        if include_recipe:
            recipe_path = _save_recipe_to_path(
                fig, path.with_suffix(".yaml"), data_format
            )
            if recipe_path:
                result["recipe"] = recipe_path

    return result


def _save_figure_image(fig, path: Path, dpi: int = 300, **kwargs):
    """Save figure image using the best available method with facecolor support.

    Uses fig.savefig() when available (FigWrapper or RecordingFigure) to get
    the facecolor override fix for transparent figures.
    """
    # Check if this is a figrecipe RecordingFigure - use fr.save() for full support
    if FIGRECIPE_AVAILABLE:
        try:
            from figrecipe.utils import RecordingFigure

            if isinstance(fig, RecordingFigure):
                # Use figrecipe's save with facecolor support
                facecolor = kwargs.pop("facecolor", None)
                fr.save(
                    fig,
                    path,
                    save_recipe=False,  # Recipe saved separately
                    dpi=dpi,
                    facecolor=facecolor,
                    verbose=False,
                    **kwargs,
                )
                return
        except (ImportError, AttributeError):
            pass

    # Use fig.savefig() if available (FigWrapper has facecolor fix)
    if hasattr(fig, "savefig"):
        fig.savefig(path, dpi=dpi, **kwargs)
    else:
        # Fallback to matplotlib figure's savefig
        mpl_fig = fig._fig_mpl if hasattr(fig, "_fig_mpl") else fig
        mpl_fig.savefig(path, dpi=dpi, **kwargs)


def _save_recipe_to_path(
    fig,
    path: Path,
    data_format: str = "csv",
) -> Optional[Path]:
    """Save figrecipe recipe if available.

    Parameters
    ----------
    fig : FigWrapper
        Figure with optional _figrecipe_recorder attribute.
    path : Path
        Output path for recipe.yaml.
    data_format : str
        Format for data: 'csv', 'npz', or 'inline'.

    Returns
    -------
    Path or None
        Path to saved recipe, or None if not available.
    """
    if not FIGRECIPE_AVAILABLE:
        return None

    try:
        # Check if figure has figrecipe recorder
        if hasattr(fig, "_figrecipe_recorder") and fig._figrecipe_enabled:
            recorder = fig._figrecipe_recorder
            figure_record = recorder.figure_record

            # Capture current figure state into record
            _capture_figure_state(fig, figure_record)

            # Save using figrecipe's serializer
            _fr_save_recipe(
                figure_record, path, include_data=True, data_format=data_format
            )
            return path

        # Alternative: if figure was created with fr.subplots() directly
        if hasattr(fig, "save_recipe"):
            fig.save_recipe(path, include_data=True, data_format=data_format)
            return path

        # Diagram figures: d.render() attaches _figrecipe_diagram
        if hasattr(fig, "_figrecipe_diagram"):
            from figrecipe._diagram._diagram._io import save_diagram_recipe

            save_diagram_recipe(fig._figrecipe_diagram, path)
            return path

    except Exception:
        pass  # Recipe saving is optional

    return None


def _capture_figure_state(fig, figure_record):
    """Capture current figure state into the record.

    This syncs the matplotlib figure state with the figrecipe record,
    ensuring the recipe reflects the final figure appearance.
    """
    try:
        mpl_fig = fig._fig_mpl if hasattr(fig, "_fig_mpl") else fig

        # Update figure dimensions
        figsize = mpl_fig.get_size_inches()
        figure_record.figsize = list(figsize)
        figure_record.dpi = int(mpl_fig.dpi)

        # Capture style from scitex metadata if available
        if hasattr(mpl_fig, "_scitex_theme"):
            if not hasattr(figure_record, "style") or figure_record.style is None:
                figure_record.style = {}
            figure_record.style["theme"] = mpl_fig._scitex_theme

    except Exception:
        pass  # Non-critical


def load_recipe(
    path: Union[str, Path],
) -> Any:
    """Load figrecipe recipe from FTS bundle.

    Parameters
    ----------
    path : str or Path
        Path to bundle directory, zip file, or recipe.yaml.

    Returns
    -------
    tuple
        (fig, axes) reproduced from recipe.
    """
    if not FIGRECIPE_AVAILABLE:
        raise ImportError("figrecipe is required for loading recipes")

    path = Path(path)

    # Handle bundle paths
    if path.is_dir():
        recipe_path = path / "recipe.yaml"
    elif path.suffix == ".zip":
        # figrecipe can handle zip files directly
        recipe_path = path
    else:
        recipe_path = path

    return fr.reproduce(recipe_path)


def has_figrecipe() -> bool:
    """Check if figrecipe is available."""
    return FIGRECIPE_AVAILABLE


# EOF
