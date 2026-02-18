#!/usr/bin/env python3
# Timestamp: 2025-12-19
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_image_csv.py

"""Handle image file saving with optional CSV export and auto-cropping."""

import os

from scitex import logging

from ._figure_utils import get_figure_with_data
from ._legends import save_separate_legends

# Optional: plotly-dependent save_image
try:
    from ._image import save_image
except ImportError:
    save_image = None
from ._symlink import symlink, symlink_to

logger = logging.getLogger()


def handle_image_with_csv(
    obj,
    spath,
    verbose=False,
    no_csv=False,
    symlink_from_cwd=False,
    dry_run=False,
    symlink_to_path=None,
    auto_crop=True,
    crop_margin_mm=1.0,
    metadata_extra=None,
    json_schema="editable",
    **kwargs,
):
    """Handle image file saving with optional CSV export and auto-cropping."""
    if dry_run:
        return
    watermark = kwargs.pop("watermark", False)
    collected_metadata = _collect_metadata(
        obj, kwargs, verbose, json_schema, metadata_extra
    )
    save_image(obj, spath, verbose=verbose, **kwargs)
    _auto_crop_image(
        spath, auto_crop, crop_margin_mm, collected_metadata, kwargs, verbose
    )
    if watermark:
        try:
            from figrecipe._diagram._diagram._io import _add_watermark

            _add_watermark(str(spath), dpi=kwargs.get("dpi", 300))
        except Exception as e:
            logger.warning("watermark failed: %s", e)

    # Handle separate legend saving
    save_separate_legends(
        obj,
        spath,
        symlink_from_cwd=symlink_from_cwd,
        dry_run=dry_run,
        **kwargs,
    )

    # Export CSV data
    csv_path = None
    if not no_csv:
        csv_path = _export_csv_data(
            obj, spath, collected_metadata, symlink_from_cwd, symlink_to_path, dry_run
        )

    # Save metadata as JSON
    if collected_metadata is not None and not dry_run:
        _save_metadata_json(
            spath,
            collected_metadata,
            csv_path,
            json_schema,
            symlink_from_cwd,
            symlink_to_path,
            dry_run,
        )

    if not dry_run:
        try:
            from pathlib import Path

            from scitex.bridge._figrecipe import _save_recipe_to_path

            recipe_path = Path(spath).with_suffix(".yaml")
            _save_recipe_to_path(obj, recipe_path)
        except Exception:
            pass
        from ._figrecipe_hitmap import try_figrecipe_hitmap

        try_figrecipe_hitmap(obj, spath, kwargs)


def _collect_metadata(obj, kwargs, verbose, json_schema, metadata_extra):  # noqa: C901
    """Auto-collect metadata from scitex figures."""
    collected_metadata = None
    if "metadata" not in kwargs or kwargs["metadata"] is None:
        try:
            import matplotlib.figure

            fig_mpl = None
            if isinstance(obj, matplotlib.figure.Figure):
                fig_mpl = obj
            elif hasattr(obj, "_fig_mpl"):
                fig_mpl = obj._fig_mpl
            elif hasattr(obj, "figure") and isinstance(
                obj.figure, matplotlib.figure.Figure
            ):
                fig_mpl = obj.figure

            if fig_mpl is not None:
                ax = None
                if hasattr(obj, "axes"):
                    ax = obj.axes
                elif hasattr(fig_mpl, "axes") and len(fig_mpl.axes) > 0:
                    mpl_ax = fig_mpl.axes[0]
                    if hasattr(mpl_ax, "_scitex_wrapper"):
                        ax = mpl_ax._scitex_wrapper
                    else:
                        ax = mpl_ax

                try:
                    if json_schema == "editable":
                        from scitex.plt.utils.metadata import export_editable_figure

                        auto_metadata = export_editable_figure(fig_mpl)
                    elif json_schema == "recipe":
                        from scitex.plt.utils import collect_recipe_metadata

                        auto_metadata = collect_recipe_metadata(fig_mpl, ax)
                    else:
                        from scitex.plt.utils import collect_figure_metadata

                        auto_metadata = collect_figure_metadata(fig_mpl, ax)

                    if auto_metadata:
                        kwargs["metadata"] = auto_metadata
                        collected_metadata = auto_metadata
                        if verbose:
                            schema_names = {
                                "editable": "editable v0.3",
                                "recipe": "recipe",
                                "verbose": "verbose",
                            }
                            schema_name = schema_names.get(json_schema, json_schema)
                            logger.info(
                                f"  • Auto-collected metadata ({schema_name} schema)"
                            )
                except ImportError:
                    pass
                except Exception as e:
                    if verbose:
                        logger.warning(f"Could not auto-collect metadata: {e}")
        except Exception:
            pass
    else:
        collected_metadata = kwargs.get("metadata")

    # Merge metadata_extra with collected_metadata
    if metadata_extra is not None and collected_metadata is not None:
        import copy

        collected_metadata = copy.deepcopy(collected_metadata)
        if "plot_type" in metadata_extra:
            collected_metadata["plot_type"] = metadata_extra["plot_type"]
        if "style" in metadata_extra:
            collected_metadata["style"] = metadata_extra["style"]
        for key, value in metadata_extra.items():
            if key not in ["plot_type", "style"]:
                collected_metadata[key] = value
        kwargs["metadata"] = collected_metadata

    return collected_metadata


def _auto_crop_image(
    spath, auto_crop, crop_margin_mm, collected_metadata, kwargs, verbose
):
    """Auto-crop image if requested."""
    crop_offset = None
    if auto_crop:
        ext = spath.lower()
        if ext.endswith((".png", ".jpg", ".jpeg", ".tiff", ".tif")):
            try:
                from figrecipe import crop

                dpi = kwargs.get("dpi", 300)
                margin_px = int(crop_margin_mm * dpi / 25.4)

                _, crop_offset = crop(
                    spath,
                    output_path=spath,
                    margin_px=margin_px,
                    overwrite=True,
                    verbose=False,
                    return_offset=True,
                )

                # Adjust metadata for crop offset
                if crop_offset and collected_metadata:
                    _adjust_metadata_for_crop(collected_metadata, crop_offset)

                if verbose:
                    logger.info(
                        f"  • Auto-cropped with {crop_margin_mm}mm margin ({margin_px}px at {dpi} DPI)"
                    )

            except Exception as e:
                logger.warning(f"Auto-crop failed: {e}. Image saved without cropping.")

    return crop_offset


def _adjust_metadata_for_crop(collected_metadata, crop_offset):
    """Adjust metadata coordinates for crop offset."""
    if "axes_bbox_px" in collected_metadata:
        bbox = collected_metadata["axes_bbox_px"]
        left_offset = crop_offset["left"]
        upper_offset = crop_offset["upper"]
        bbox["x0"] = bbox.get("x0", 0) - left_offset
        bbox["x1"] = bbox.get("x1", 0) - left_offset
        bbox["y0"] = bbox.get("y0", 0) - upper_offset
        bbox["y1"] = bbox.get("y1", 0) - upper_offset

    if "figure" in collected_metadata:
        fig_meta = collected_metadata["figure"]
        if "size_px" in fig_meta:
            fig_meta["size_px"] = [
                crop_offset["new_width"],
                crop_offset["new_height"],
            ]
    if "dimensions" in collected_metadata:
        dim_meta = collected_metadata["dimensions"]
        if "figure_size_px" in dim_meta:
            dim_meta["figure_size_px"] = [
                crop_offset["new_width"],
                crop_offset["new_height"],
            ]


def _export_csv_data(
    obj, spath, collected_metadata, symlink_from_cwd, symlink_to_path, dry_run
):
    """Export CSV data from figure."""
    image_extensions = ["png", "jpg", "jpeg", "gif", "tiff", "tif", "svg", "pdf"]
    parent_dir = os.path.dirname(spath)
    parent_name = os.path.basename(parent_dir)
    filename_without_ext = os.path.splitext(os.path.basename(spath))[0]

    csv_path = None
    try:
        fig_obj = get_figure_with_data(obj)

        if fig_obj is not None and hasattr(fig_obj, "export_as_csv"):
            csv_data = fig_obj.export_as_csv()
            if csv_data is not None and not csv_data.empty:
                # Determine CSV path
                if parent_name.lower() in image_extensions:
                    grandparent_dir = os.path.dirname(parent_dir)
                    csv_dir = os.path.join(grandparent_dir, "csv")
                    csv_path = os.path.join(csv_dir, filename_without_ext + ".csv")
                else:
                    csv_path = os.path.splitext(spath)[0] + ".csv"

                os.makedirs(os.path.dirname(csv_path), exist_ok=True)

                # Import here to avoid circular import
                from . import save_csv

                save_csv(csv_data, csv_path)

                # Update metadata with CSV info
                if collected_metadata is not None:
                    _update_metadata_with_csv(collected_metadata, csv_data, csv_path)

                # Handle symlinks for CSV
                _create_csv_symlinks(
                    csv_path, spath, symlink_from_cwd, symlink_to_path, image_extensions
                )

        # Also export SigmaPlot format if available
        if fig_obj is not None and hasattr(fig_obj, "export_as_csv_for_sigmaplot"):
            _export_sigmaplot_csv(
                fig_obj,
                spath,
                parent_name,
                parent_dir,
                filename_without_ext,
                symlink_from_cwd,
                symlink_to_path,
                image_extensions,
                dry_run,
            )

    except Exception as e:
        logger.warning(f"CSV export failed: {e}")

    return csv_path


def _update_metadata_with_csv(collected_metadata, csv_data, csv_path):
    """Update metadata with actual CSV info."""
    try:
        from scitex.plt.utils._collect_figure_metadata import _compute_csv_hash

        if "data" not in collected_metadata:
            collected_metadata["data"] = {}

        actual_columns = list(csv_data.columns)
        collected_metadata["data"]["csv_path"] = os.path.basename(csv_path)
        collected_metadata["data"]["columns_actual"] = actual_columns
        collected_metadata["data"]["csv_hash"] = _compute_csv_hash(csv_data)
    except Exception:
        pass


def _create_csv_symlinks(
    csv_path, spath, symlink_from_cwd, symlink_to_path, image_extensions
):
    """Create symlinks for CSV file."""
    if symlink_to_path:
        symlink_parent_dir = os.path.dirname(symlink_to_path)
        symlink_parent_name = os.path.basename(symlink_parent_dir)
        symlink_filename_without_ext = os.path.splitext(
            os.path.basename(symlink_to_path)
        )[0]

        if symlink_parent_name.lower() in image_extensions:
            symlink_grandparent_dir = os.path.dirname(symlink_parent_dir)
            csv_symlink_to = os.path.join(
                symlink_grandparent_dir, "csv", symlink_filename_without_ext + ".csv"
            )
        else:
            csv_symlink_to = os.path.splitext(symlink_to_path)[0] + ".csv"

        symlink_to(csv_path, csv_symlink_to, True)

    if symlink_from_cwd:
        import inspect

        frame_info = inspect.stack()
        for frame in frame_info:
            if "specified_path" in frame.frame.f_locals:
                original_path = frame.frame.f_locals["specified_path"]
                if isinstance(original_path, str):
                    orig_parent_dir = os.path.dirname(original_path)
                    orig_parent_name = os.path.basename(orig_parent_dir)
                    orig_filename_without_ext = os.path.splitext(
                        os.path.basename(original_path)
                    )[0]

                    if orig_parent_name.lower() in image_extensions:
                        orig_grandparent_dir = os.path.dirname(orig_parent_dir)
                        csv_relative = os.path.join(
                            orig_grandparent_dir,
                            "csv",
                            orig_filename_without_ext + ".csv",
                        )
                    else:
                        csv_relative = original_path.replace(
                            os.path.splitext(original_path)[1], ".csv"
                        )

                    csv_cwd = os.path.join(os.getcwd(), csv_relative)
                    symlink(csv_path, csv_cwd, True, True)
                    break
        else:
            csv_cwd = os.getcwd() + "/" + os.path.basename(csv_path)
            symlink(csv_path, csv_cwd, True, True)


def _export_sigmaplot_csv(
    fig_obj,
    spath,
    parent_name,
    parent_dir,
    filename_without_ext,
    symlink_from_cwd,
    symlink_to_path,
    image_extensions,
    dry_run,
):
    """Export SigmaPlot-formatted CSV."""
    sigmaplot_data = fig_obj.export_as_csv_for_sigmaplot()
    if sigmaplot_data is not None and not sigmaplot_data.empty:
        if parent_name.lower() in image_extensions:
            grandparent_dir = os.path.dirname(parent_dir)
            csv_dir = os.path.join(grandparent_dir, "csv")
            csv_sigmaplot_path = os.path.join(
                csv_dir, filename_without_ext + "_for_sigmaplot.csv"
            )
        else:
            ext = os.path.splitext(spath)[1].lower().replace(".", "")
            csv_sigmaplot_path = spath.replace(ext, "csv").replace(
                ".csv", "_for_sigmaplot.csv"
            )

        os.makedirs(os.path.dirname(csv_sigmaplot_path), exist_ok=True)
        from . import save_csv

        save_csv(sigmaplot_data, csv_sigmaplot_path)


def _save_metadata_json(
    spath,
    collected_metadata,
    csv_path,
    json_schema,
    symlink_from_cwd,
    symlink_to_path,
    dry_run,
):
    """Save metadata as JSON file."""
    try:
        image_extensions = ["png", "jpg", "jpeg", "gif", "tiff", "tif", "svg", "pdf"]
        parent_dir = os.path.dirname(spath)
        parent_name = os.path.basename(parent_dir)
        filename_without_ext = os.path.splitext(os.path.basename(spath))[0]

        if parent_name.lower() in image_extensions:
            grandparent_dir = os.path.dirname(parent_dir)
            json_dir = os.path.join(grandparent_dir, "json")
            json_path = os.path.join(json_dir, filename_without_ext + ".json")
        else:
            json_path = os.path.splitext(spath)[0] + ".json"

        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        from . import save_json

        save_json(collected_metadata, json_path)

        # Verify CSV/JSON consistency for verbose schema
        if csv_path and not dry_run and json_schema == "verbose":
            from scitex.plt.utils._collect_figure_metadata import (
                assert_csv_json_consistency,
            )

            assert_csv_json_consistency(csv_path, json_path)

        # Create symlinks for JSON
        _create_json_symlinks(
            json_path, symlink_from_cwd, symlink_to_path, image_extensions
        )

    except AssertionError:
        raise
    except Exception as e:
        logger.warning(f"JSON metadata export failed: {e}")


def _create_json_symlinks(
    json_path, symlink_from_cwd, symlink_to_path, image_extensions
):
    """Create symlinks for JSON file."""
    if symlink_to_path:
        symlink_parent_dir = os.path.dirname(symlink_to_path)
        symlink_parent_name = os.path.basename(symlink_parent_dir)
        symlink_filename_without_ext = os.path.splitext(
            os.path.basename(symlink_to_path)
        )[0]

        if symlink_parent_name.lower() in image_extensions:
            symlink_grandparent_dir = os.path.dirname(symlink_parent_dir)
            json_symlink_to = os.path.join(
                symlink_grandparent_dir, "json", symlink_filename_without_ext + ".json"
            )
        else:
            json_symlink_to = os.path.splitext(symlink_to_path)[0] + ".json"

        symlink_to(json_path, json_symlink_to, True)

    if symlink_from_cwd:
        import inspect

        frame_info = inspect.stack()
        for frame in frame_info:
            if "specified_path" in frame.frame.f_locals:
                original_path = frame.frame.f_locals["specified_path"]
                if isinstance(original_path, str):
                    orig_parent_dir = os.path.dirname(original_path)
                    orig_parent_name = os.path.basename(orig_parent_dir)
                    orig_filename_without_ext = os.path.splitext(
                        os.path.basename(original_path)
                    )[0]

                    if orig_parent_name.lower() in image_extensions:
                        orig_grandparent_dir = os.path.dirname(orig_parent_dir)
                        json_relative = os.path.join(
                            orig_grandparent_dir,
                            "json",
                            orig_filename_without_ext + ".json",
                        )
                    else:
                        json_relative = original_path.replace(
                            os.path.splitext(original_path)[1], ".json"
                        )

                    json_cwd = os.path.join(os.getcwd(), json_relative)
                    symlink(json_path, json_cwd, True, True)
                    break
        else:
            json_cwd = os.getcwd() + "/" + os.path.basename(json_path)
            symlink(json_path, json_cwd, True, True)
