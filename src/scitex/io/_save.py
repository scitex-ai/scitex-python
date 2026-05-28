#!/usr/bin/env python3
# Timestamp: 2025-12-19
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save.py

"""
Save utilities for various data types to different file formats.

Supported formats include CSV, NPY, PKL, JOBLIB, PNG, HTML, TIFF, MP4, YAML,
JSON, HDF5, PTH, MAT, CBM, and SciTeX bundles (.zip or directory).
"""

import inspect
import os as _os
from pathlib import Path
from typing import Any, Union

from scitex import logging
from scitex.path import clean, getsize
from scitex.str import clean_path, color_text, readable_bytes

# Import save functions from the modular structure
from ._save_modules import (
    get_figure_with_data,
    handle_image_with_csv,
    save_bibtex,
    save_catboost,
    save_csv,
    save_excel,
    save_hdf5,
    save_html,
    save_joblib,
    save_json,
    save_matlab,
    save_mp4,
    save_npy,
    save_npz,
    save_pickle,
    save_pickle_compressed,
    save_tex,
    save_text,
    save_torch,
    save_yaml,
    save_zarr,
    symlink,
    symlink_to,
)
from ._sh import sh

logger = logging.getLogger()

_get_figure_with_data = get_figure_with_data
_symlink = symlink
_symlink_to = symlink_to
_handle_image_with_csv = handle_image_with_csv


def save(
    obj: Any,
    specified_path: Union[str, Path],
    makedirs: bool = True,
    verbose: bool = True,
    symlink_from_cwd: bool = False,
    symlink_to: Union[str, Path] = None,
    dry_run: bool = False,
    no_csv: bool = False,
    use_caller_path: bool = False,
    auto_crop: bool = True,
    crop_margin_mm: float = 1.0,
    metadata_extra: dict = None,
    json_schema: str = "editable",
    track: bool = True,
    register: bool = False,
    **kwargs,
) -> None:
    """Save an object to a file with the specified format.

    Parameters
    ----------
    obj : Any -- The object to be saved.
    specified_path : Union[str, Path] -- Target file path.
    makedirs : bool -- Create parent directories if missing.
    verbose : bool -- Log success message after saving.
    symlink_from_cwd : bool -- Create symlink from cwd.
    symlink_to : Union[str, Path] -- Create symlink at this path.
    dry_run : bool -- Simulate without writing.
    auto_crop : bool -- Auto-crop saved images.
    crop_margin_mm : float -- Crop margin in mm.
    use_caller_path : bool -- Resolve path via caller frame.
    metadata_extra : dict -- Extra metadata to merge.
    json_schema : str -- JSON metadata schema type.
    track : bool -- Track file in verification system.
    register : bool -- Register file hash with remote Clew Registry.
    **kwargs -- Passed to underlying save function.
    """
    try:
        # Handle file-like objects (BytesIO) directly
        if hasattr(specified_path, "write"):
            return _save(obj, specified_path, verbose=False, **kwargs) or specified_path

        if isinstance(specified_path, Path):
            specified_path = str(specified_path)
        specified_path = _parse_fstring_path(specified_path)  # Handle f-strings
        spath = _determine_save_path(specified_path, use_caller_path)
        spath_final = clean(spath)

        # Prepare symlink path from cwd
        spath_cwd = _os.getcwd() + "/" + specified_path
        spath_cwd = clean(spath_cwd)

        # Remove existing files (skip for CSV/HDF5 with key)
        _cleanup_existing_files(spath_final, spath_cwd, kwargs)

        if dry_run:
            _handle_dry_run(spath, verbose)
            return

        if makedirs:
            _os.makedirs(_os.path.dirname(spath_final), exist_ok=True)

        # Main save
        _save(
            obj,
            spath_final,
            verbose=verbose,
            symlink_from_cwd=symlink_from_cwd,
            symlink_to=symlink_to,
            dry_run=dry_run,
            no_csv=no_csv,
            auto_crop=auto_crop,
            crop_margin_mm=crop_margin_mm,
            metadata_extra=metadata_extra,
            json_schema=json_schema,
            **kwargs,
        )

        # Symbolic links
        _symlink(spath, spath_cwd, symlink_from_cwd, verbose)
        _symlink_to(spath_final, symlink_to, verbose)

        # Track output for verification (if session is active)
        try:
            from scitex.clew import on_io_save

            on_io_save(spath_final, track=track)
        except Exception as e:
            logger.debug("clew: failed to track output %s: %s", spath_final, e)

        # Register hash with remote Clew Registry (opt-in)
        if register:
            try:
                from scitex.clew import get_registry, hash_file

                file_hash = hash_file(spath_final)
                get_registry().register(file_hash, source_type="file")
            except Exception as e:
                logger.debug("clew: failed to register %s: %s", spath_final, e)

        return Path(spath)

    except AssertionError:
        raise
    except Exception as e:
        logger.error(f"Error occurred while saving: {str(e)}")
        return False


def _try_scitex_io_provider(obj, spath, **kwargs) -> bool:
    """Delegate to scitex_io's registry (which knows about optional providers).

    Returns ``True`` when an ecosystem provider handled the save (e.g.
    figrecipe for ``.plt.zip`` / ``.fig.zip``, scitex_stats for
    ``.stats.zip``), ``False`` when no provider matched and the caller
    should surface "Unsupported file format" itself.
    """
    try:
        import scitex_io
        from scitex_io._optional_providers import OPTIONAL_COMPOUND_EXTS
        from scitex_io._registry import get_saver
    except Exception:
        return False

    # Match against the declared compound extensions (e.g. ".plt.zip"),
    # not just the trailing ".zip" splitext gives us.
    matched_ext = None
    spath_lower = str(spath).lower()
    for compound in OPTIONAL_COMPOUND_EXTS:
        if spath_lower.endswith(compound):
            matched_ext = compound
            break
    if matched_ext is None:
        return False

    saver = get_saver(matched_ext)
    if saver is None:
        return False

    saver(obj, spath, **kwargs)
    return True


def _parse_fstring_path(specified_path):
    """Parse f-string expressions in path."""
    if not (specified_path.startswith('f"') or specified_path.startswith("f'")):
        return specified_path

    import re

    path_content = specified_path[2:-1]
    frame = inspect.currentframe().f_back.f_back
    try:
        variables = re.findall(r"\{([^}]+)\}", path_content)
        format_dict = {}
        for var in variables:
            if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
                if var in frame.f_locals:
                    format_dict[var] = frame.f_locals[var]
                elif var in frame.f_globals:
                    format_dict[var] = frame.f_globals[var]
            else:
                raise ValueError(f"Invalid variable name in f-string: {var}")
        return path_content.format(**format_dict)
    finally:
        del frame


def _determine_save_path(specified_path, use_caller_path):
    """Determine the full save path based on environment."""
    if specified_path.startswith("/"):
        return specified_path

    from scitex.context import detect_environment, get_notebook_info_simple

    env_type = detect_environment()

    if env_type == "jupyter":
        notebook_name, notebook_dir = get_notebook_info_simple()
        if notebook_name:
            notebook_base = _os.path.splitext(notebook_name)[0]
            sdir = _os.path.join(notebook_dir or _os.getcwd(), f"{notebook_base}_out")
        else:
            sdir = _os.path.join(_os.getcwd(), "notebook_out")
        return _os.path.join(sdir, specified_path)

    elif env_type == "script":
        if use_caller_path:
            script_path = _find_caller_script_path()
        else:
            script_path = inspect.stack()[2].filename
        sdir = clean_path(_os.path.splitext(script_path)[0] + "_out")
        return _os.path.join(sdir, specified_path)

    else:
        script_path = inspect.stack()[2].filename
        if (
            ("ipython" in script_path)
            or ("<stdin>" in script_path)
            or env_type in ["ipython", "interactive"]
        ):
            sdir = f"/tmp/{_os.getenv('USER')}"
        else:
            sdir = _os.path.join(_os.getcwd(), "output")
        return _os.path.join(sdir, specified_path)


def _find_caller_script_path():
    """Find the first non-scitex frame in the call stack."""
    scitex_src_path = _os.path.abspath(
        _os.path.join(_os.path.dirname(__file__), "..", "..")
    )
    for frame_info in inspect.stack()[3:]:
        frame_path = _os.path.abspath(frame_info.filename)
        if not frame_path.startswith(scitex_src_path):
            return frame_path
    return inspect.stack()[2].filename


def _cleanup_existing_files(spath_final, spath_cwd, kwargs):
    """Remove existing files to prevent circular links."""
    should_skip = spath_final.endswith(".csv") or (
        (spath_final.endswith(".hdf5") or spath_final.endswith(".h5"))
        and "key" in kwargs
    )
    if not should_skip:
        for path in [spath_final, spath_cwd]:
            sh(["rm", "-f", f"{path}"], verbose=False)


def _handle_dry_run(spath, verbose):
    """Handle dry run mode."""
    if verbose:
        try:
            rel_path = _os.path.relpath(spath, _os.getcwd())
        except ValueError:
            rel_path = spath
        logger.success(color_text(f"(dry run) Saved to: ./{rel_path}", c="yellow"))


def _save(
    obj,
    spath,
    verbose=True,
    symlink_from_cwd=False,
    dry_run=False,
    no_csv=False,
    symlink_to=None,
    auto_crop=False,
    crop_margin_mm=1.0,
    metadata_extra=None,
    json_schema="editable",
    **kwargs,
):
    """Core dispatcher for saving objects to various formats."""
    # Handle file-like objects (BytesIO, etc.)
    is_file_like = hasattr(spath, "write")
    ext = (
        f".{kwargs.get('format', 'png').lower()}"
        if is_file_like
        else _os.path.splitext(spath)[1].lower()
    )

    # Check if matplotlib figure for SciTeX bundle (zip or no-ext directory)
    if _is_matplotlib_figure(obj) and not is_file_like:
        if ext == ".zip" or (ext == "" and not spath.endswith("/")):
            as_zip = kwargs.pop("as_zip", ext == ".zip")
            _save_scitex_bundle(
                obj, spath, as_zip, verbose, symlink_from_cwd, symlink_to, **kwargs
            )
            return

    # Dispatch to format handlers
    if ext in _FILE_HANDLERS:
        _dispatch_handler(
            ext,
            obj,
            spath,
            verbose,
            no_csv,
            symlink_from_cwd,
            symlink_to,
            dry_run,
            auto_crop,
            crop_margin_mm,
            metadata_extra,
            json_schema,
            kwargs,
        )
    elif not is_file_like and spath.endswith(".csv"):
        save_csv(obj, spath, **kwargs)
    elif not is_file_like and spath.endswith(".pkl.gz"):
        save_pickle_compressed(obj, spath, **kwargs)
    elif not is_file_like and _try_scitex_io_provider(obj, spath, **kwargs):
        # Compound extensions contributed by ecosystem optional providers
        # (figrecipe → .plt.zip/.fig.zip, scitex_stats → .stats.zip, …).
        # Delegate to scitex_io's registry so the umbrella inherits every
        # provider the standalone package knows about.
        pass
    else:
        logger.warning(f"Unsupported file format. {spath} was not saved.")
        return

    if verbose and not is_file_like and _os.path.exists(spath):
        file_size = readable_bytes(getsize(spath))
        try:
            rel_path = _os.path.relpath(spath, _os.getcwd())
        except ValueError:
            rel_path = spath
        dim = ""
        try:
            from PIL import Image

            w, h = Image.open(spath).size
            d = kwargs.get("dpi", 300)
            dim = f" [W: {w / d * 25.4:.1f}mm, H: {h / d * 25.4:.1f}mm]"
        except Exception:
            pass
        logger.success(f"Saved to: ./{rel_path} ({file_size}){dim}")


def _is_matplotlib_figure(obj):
    """Check if object is a matplotlib figure or a wrapped figure.

    Handles both raw matplotlib.figure.Figure and SciTeX FigWrapper objects.
    """
    try:
        import matplotlib.figure

        # Direct matplotlib figure
        if isinstance(obj, matplotlib.figure.Figure):
            return True

        # Wrapped figure (e.g., FigWrapper from scitex.plt)
        if hasattr(obj, "figure") and isinstance(obj.figure, matplotlib.figure.Figure):
            return True

        return False
    except ImportError:
        return False


def _save_scitex_bundle(
    obj, spath, as_zip, verbose, symlink_from_cwd, symlink_to_path, **kwargs
):
    """Save matplotlib figure as SciTeX bundle (.zip or directory).

    Delegates to scitex.io.bundle.from_matplotlib as the single source of truth
    for bundle structure (canonical/artifacts/payload/children).

    When figrecipe is available and enabled on the figure, also saves
    recipe.yaml for reproducibility.
    """
    # Get the actual matplotlib figure
    import matplotlib.figure

    from scitex.io.bundle import from_matplotlib

    if isinstance(obj, matplotlib.figure.Figure):
        fig = obj
        fig_wrapper = None
    elif hasattr(obj, "figure") and isinstance(obj.figure, matplotlib.figure.Figure):
        fig = obj.figure
        fig_wrapper = obj  # Keep wrapper for figrecipe access
    else:
        raise TypeError(f"Expected matplotlib figure, got {type(obj)}")

    # Extract optional parameters
    # Support both "csv_df" and "data" parameter names for user convenience
    csv_df = kwargs.get("csv_df") or kwargs.get("data")
    dpi = kwargs.get("dpi", 300)
    name = kwargs.get("name") or Path(spath).stem

    # CSV via AxisWrapper removed (figrecipe migration); csv_df from explicit kwarg only

    # Delegate to Bundle (single source of truth)
    # Encoding is built from CSV columns directly for consistency
    from_matplotlib(fig, spath, name=name, csv_df=csv_df, dpi=dpi)

    # Save figrecipe recipe.yaml if available
    try:
        from scitex.bridge._figrecipe import _save_recipe_to_path

        bundle_path = Path(spath)
        if bundle_path.suffix != ".zip":  # Skip zip for now
            _save_recipe_to_path(fig_wrapper or obj, bundle_path / "recipe.yaml")
    except (ImportError, Exception):
        pass  # figrecipe is optional

    bundle_path = spath
    if verbose and _os.path.exists(bundle_path):
        file_size = readable_bytes(getsize(bundle_path))
        try:
            rel_path = _os.path.relpath(bundle_path, _os.getcwd())
        except ValueError:
            rel_path = bundle_path
        logger.success(f"Saved to: ./{rel_path} ({file_size})")

    if symlink_from_cwd and _os.path.exists(bundle_path):
        bundle_basename = _os.path.basename(bundle_path)
        bundle_cwd = _os.path.join(_os.getcwd(), bundle_basename)
        _symlink(bundle_path, bundle_cwd, symlink_from_cwd, verbose)

    if symlink_to_path and _os.path.exists(bundle_path):
        _symlink_to(bundle_path, symlink_to_path, verbose)


def _dispatch_handler(
    ext,
    obj,
    spath,
    verbose,
    no_csv,
    symlink_from_cwd,
    symlink_to_path,
    dry_run,
    auto_crop,
    crop_margin_mm,
    metadata_extra,
    json_schema,
    kwargs,
):
    """Dispatch to the appropriate file handler."""
    image_exts = [".png", ".jpg", ".jpeg", ".gif", ".tiff", ".tif", ".svg", ".pdf"]
    if ext in image_exts:
        _handle_image_with_csv(
            obj,
            spath,
            verbose=verbose,
            no_csv=no_csv,
            symlink_from_cwd=symlink_from_cwd,
            symlink_to_path=symlink_to_path,
            dry_run=dry_run,
            auto_crop=auto_crop,
            crop_margin_mm=crop_margin_mm,
            metadata_extra=metadata_extra,
            json_schema=json_schema,
            **kwargs,
        )
    elif ext in [".hdf5", ".h5", ".zarr"]:
        _FILE_HANDLERS[ext](obj, spath, **kwargs)
    else:
        _FILE_HANDLERS[ext](obj, spath, **kwargs)


# Dispatch dictionary for O(1) file format lookup
_FILE_HANDLERS = {
    ".xlsx": save_excel,
    ".xls": save_excel,
    ".npy": save_npy,
    ".npz": save_npz,
    ".pkl": save_pickle,
    ".pickle": save_pickle,
    ".pkl.gz": save_pickle_compressed,
    ".joblib": save_joblib,
    ".pth": save_torch,
    ".pt": save_torch,
    ".mat": save_matlab,
    ".cbm": save_catboost,
    ".json": save_json,
    ".yaml": save_yaml,
    ".yml": save_yaml,
    ".txt": save_text,
    ".md": save_text,
    ".py": save_text,
    ".css": save_text,
    ".js": save_text,
    ".tex": save_tex,
    ".bib": save_bibtex,
    ".html": save_html,
    ".hdf5": save_hdf5,
    ".h5": save_hdf5,
    ".zarr": save_zarr,
    ".mp4": save_mp4,
    ".png": handle_image_with_csv,
    ".jpg": handle_image_with_csv,
    ".jpeg": handle_image_with_csv,
    ".gif": handle_image_with_csv,
    ".tiff": handle_image_with_csv,
    ".tif": handle_image_with_csv,
    ".svg": handle_image_with_csv,
    ".pdf": handle_image_with_csv,
}

# EOF
