#!/usr/bin/env python3
# Timestamp: 2026-01-07
# File: src/scitex/io/bundle/_core.py

"""
SciTeX Bundle Core Operations.

Provides load, save, copy, pack, unpack, and validate operations for
.figure.zip, .plot.zip, .stats.zip bundle formats.

Each bundle can exist in two forms:
    - Directory: Figure1.figure/, plot.plot/, results.stats/
    - ZIP archive: Figure1.figure.zip, plot.plot.zip, results.stats.zip
"""

import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex_io.bundle._types import EXTENSIONS, BundleNotFoundError, BundleType, BundleValidationError

__all__ = [
    "load",
    "save",
    "copy",
    "pack",
    "unpack",
    "validate",
    "validate_spec",
    "is_bundle",
    "get_type",
    "dir_to_zip_path",
    "zip_to_dir_path",
]


def get_type(path: Union[str, Path]) -> Optional[str]:
    """Get bundle type from path.

    Checks manifest.json first for reliable type detection, then falls back
    to extension-based detection.

    Args:
        path: Path to bundle (directory or ZIP).

    Returns
    -------
        Bundle type string ('figure', 'plot', 'stats') or None if not a bundle.

    Example:
        >>> get_type("Figure1.figure.zip")
        'figure'
        >>> get_type("plot.plot")
        'plot'
    """
    p = Path(path)

    if not p.exists():
        # Fall back to extension-based detection for non-existent paths
        return _get_type_from_extension(p)

    # Try manifest.json first (most reliable)
    manifest_type = _get_type_from_manifest(p)
    if manifest_type:
        return manifest_type

    # Fall back to extension-based detection
    return _get_type_from_extension(p)


def _get_type_from_manifest(path: Path) -> Optional[str]:
    """Get bundle type from manifest.json.

    Args:
        path: Path to bundle (directory or ZIP).

    Returns
    -------
        Bundle type from manifest or None if not found.
    """
    import json

    from scitex_io.bundle._types import EXTENSIONS

    if path.is_dir():
        # Directory bundle - read manifest.json directly
        manifest_path = path / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                return manifest.get("scitex", {}).get("type")
            except (OSError, json.JSONDecodeError):
                pass
    elif path.is_file():
        # Check if it's a ZIP bundle by extension
        name = path.name.lower()
        is_zip_bundle = any(name.endswith(ext) for ext in EXTENSIONS)
        if is_zip_bundle:
            try:
                with zipfile.ZipFile(path, "r") as zf:
                    if "manifest.json" in zf.namelist():
                        content = zf.read("manifest.json")
                        manifest = json.loads(content)
                        return manifest.get("scitex", {}).get("type")
            except (zipfile.BadZipFile, OSError, json.JSONDecodeError):
                pass

    return None


def _get_type_from_extension(path: Path) -> Optional[str]:
    """Get bundle type from file extension (fallback method).

    Args:
        path: Path to bundle.

    Returns
    -------
        Bundle type from extension or None.
    """
    from scitex_io.bundle._types import DIR_EXTENSIONS, EXTENSIONS

    name = path.name.lower()

    # Check ZIP extensions (.figure.zip, .plot.zip, .stats.zip)
    for ext in EXTENSIONS:
        if name.endswith(ext):
            # Return type without dots: 'figure', 'plot', 'stats'
            return ext.split(".")[1]

    # Check directory extensions (.figure, .plot, .stats)
    for ext in DIR_EXTENSIONS:
        if name.endswith(ext) and (not path.exists() or path.is_dir()):
            return ext[1:]  # Remove leading dot

    return None


def is_bundle(path: Union[str, Path]) -> bool:
    """Check if path is a SciTeX bundle (directory or ZIP).

    Args:
        path: Path to check.

    Returns
    -------
        True if path is a bundle.

    Example:
        >>> is_bundle("Figure1.figure.zip")
        True
        >>> is_bundle("data.csv")
        False
    """
    return get_type(path) is not None


def dir_to_zip_path(dir_path: Path) -> Path:
    """Convert directory path to ZIP path.

    Example:
        >>> dir_to_zip_path(Path("Figure1.figure"))
        Path('Figure1.figure.zip')
    """
    # .figure -> .figure.zip, .plot -> .plot.zip, .stats -> .stats.zip
    return Path(str(dir_path) + ".zip")


def zip_to_dir_path(zip_path: Path) -> Path:
    """Convert ZIP path to directory path.

    Example:
        >>> zip_to_dir_path(Path("Figure1.figure.zip"))
        Path('Figure1.figure')
    """
    # .figure.zip -> .figure, .plot.zip -> .plot, .stats.zip -> .stats
    s = str(zip_path)
    if s.endswith(".zip"):
        return Path(s[:-4])
    return zip_path


def pack(
    dir_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None
) -> Path:
    """Pack a bundle directory into a ZIP archive.

    Args:
        dir_path: Path to bundle directory (e.g., Figure1.figure/).
        output_path: Output ZIP path. Auto-generated if None.

    Returns
    -------
        Path to created ZIP archive.

    Example:
        >>> pack("plot.plot")
        Path('plot.plot.zip')
    """
    dir_path = Path(dir_path)

    if not dir_path.is_dir():
        raise ValueError(f"Not a directory: {dir_path}")

    if output_path is None:
        output_path = dir_to_zip_path(dir_path)
    else:
        output_path = Path(output_path)

    # Get the directory name to use as top-level folder in ZIP
    dir_name = dir_path.name

    # Create ZIP archive with directory structure preserved
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(dir_path)
                arcname = Path(dir_name) / rel_path
                zf.write(file_path, arcname)

    return output_path


def unpack(
    zip_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None
) -> Path:
    """Unpack a bundle ZIP archive into a directory.

    Args:
        zip_path: Path to bundle ZIP (e.g., Figure1.figure.zip).
        output_path: Output directory path. Auto-generated if None.

    Returns
    -------
        Path to created directory.

    Example:
        >>> unpack("plot.plot.zip")
        Path('plot.plot')
    """
    zip_path = Path(zip_path)

    if not zip_path.is_file():
        raise ValueError(f"Not a file: {zip_path}")

    if output_path is None:
        extract_to = zip_path.parent
        expected_dir = zip_to_dir_path(zip_path)
    else:
        output_path = Path(output_path)
        extract_to = output_path.parent
        expected_dir = output_path

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)

    return expected_dir


def validate_spec(
    spec: Dict[str, Any], bundle_type: str, strict: bool = False
) -> List[str]:
    """Validate a bundle specification against its schema.

    Args:
        spec: The specification dictionary to validate.
        bundle_type: Bundle type ('figure', 'plot', 'stats').
        strict: If True, raise BundleValidationError on failure.

    Returns
    -------
        List of validation warning/error messages (empty if valid).

    Raises
    ------
        BundleValidationError: If strict=True and validation fails.
    """
    errors = []

    # Basic schema validation
    if "schema" not in spec:
        errors.append("Missing required field: schema")
    elif not isinstance(spec["schema"], dict):
        errors.append("'schema' field must be a dictionary")
    else:
        schema = spec["schema"]
        if "name" not in schema:
            errors.append("schema.name is required")
        if "version" not in schema:
            errors.append("schema.version is required")

    # Delegate to domain-specific validators
    if bundle_type == BundleType.FIGURE:
        from scitex.io.bundle.kinds._figure import validate_figure_spec

        errors.extend(validate_figure_spec(spec))
    elif bundle_type == BundleType.PLOT:
        # validate_plot_spec was a 16-line stub in scitex.plt.io._bundle. Inlined
        # here so the umbrella bundle dispatcher doesn't reach back into plt/io
        # while we retire that subpackage (figrecipe owns figure I/O via Pltz/Figz;
        # see GITIGNORED/tasks/RESUME.md).
        if "axes" in spec and not isinstance(spec["axes"], (dict, list)):
            errors.append("'axes' must be a dictionary or list")
    elif bundle_type == BundleType.STATS:
        from scitex_stats.io import validate_stats_spec

        errors.extend(validate_stats_spec(spec))
    else:
        errors.append(f"Unknown bundle type: {bundle_type}")

    if strict and errors:
        raise BundleValidationError("; ".join(errors))

    return errors


def validate(path: Union[str, Path], strict: bool = False) -> Dict[str, Any]:
    """Validate a bundle and return validation results.

    Args:
        path: Path to bundle (directory or ZIP).
        strict: If True, raise BundleValidationError on failure.

    Returns
    -------
        Dictionary with:
        - 'valid': bool
        - 'errors': list of error messages
        - 'bundle_type': detected bundle type
        - 'spec': parsed spec (if available)

    Raises
    ------
        BundleValidationError: If strict=True and validation fails.
    """
    result = {
        "valid": True,
        "errors": [],
        "bundle_type": None,
        "spec": None,
    }

    p = Path(path)

    bundle_type = get_type(p)
    if bundle_type is None:
        result["valid"] = False
        result["errors"].append(f"Not a valid bundle path: {path}")
        if strict:
            raise BundleValidationError(result["errors"][0])
        return result

    result["bundle_type"] = bundle_type

    try:
        bundle = load(path)
        spec = bundle.get("spec")
        result["spec"] = spec

        if spec is not None:
            errors = validate_spec(spec, bundle_type, strict=False)
            if errors:
                result["valid"] = False
                result["errors"].extend(errors)
        else:
            result["valid"] = False
            result["errors"].append("Bundle has no spec")

    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Failed to load bundle: {e}")

    if strict and not result["valid"]:
        raise BundleValidationError("; ".join(result["errors"]))

    return result


def load(path: Union[str, Path], in_memory: bool = True) -> Dict[str, Any]:
    """Load bundle from directory or ZIP transparently.

    Args:
        path: Path to bundle (directory or ZIP).
        in_memory: If True, load ZIP contents in-memory without extracting.
                   If False, extract to temp directory (legacy behavior).

    Returns
    -------
        Bundle data as dictionary with:
        - 'type': Bundle type ('figure', 'plot', 'stats')
        - 'spec': Parsed JSON specification
        - 'path': Original path
        - 'is_zip': Whether loaded from ZIP
        - Additional fields based on bundle type

    Example:
        >>> bundle = load("Figure1.figure.zip")
        >>> bundle['type']
        'figure'
        >>> bundle['spec']['schema']['name']
        'scitex.canvas'
    """
    p = Path(path)
    bundle_type = get_type(p)

    if bundle_type is None:
        raise BundleNotFoundError(f"Not a valid bundle: {path}")

    result = {
        "type": bundle_type,
        "path": p,
        "is_zip": False,
    }

    # Handle ZIP vs directory
    if p.is_file() and any(str(p).lower().endswith(ext) for ext in EXTENSIONS):
        result["is_zip"] = True

        if in_memory:
            from scitex_io.bundle._zip import ZipBundle

            with ZipBundle(p, mode="r") as zb:
                result["_zip_bundle"] = zb
                try:
                    result["spec"] = zb.read_json("spec.json")
                except FileNotFoundError:
                    result["spec"] = None
                try:
                    result["style"] = zb.read_json("style.json")
                except FileNotFoundError:
                    result["style"] = None
                try:
                    result["data"] = zb.read_csv("data.csv")
                except FileNotFoundError:
                    result["data"] = None

                result["files"] = zb.namelist()

            return result
        else:
            import tempfile

            temp_dir = Path(tempfile.mkdtemp())
            with zipfile.ZipFile(p, "r") as zf:
                zf.extractall(temp_dir)
            bundle_dir = temp_dir
    else:
        bundle_dir = p

    # Delegate to domain-specific loaders
    if bundle_type == BundleType.FIGURE:
        from scitex.io.bundle.kinds._figure import load_figure_bundle

        result.update(load_figure_bundle(bundle_dir))
    elif bundle_type == BundleType.PLOT:
        from scitex.io.bundle.kinds._plot._legacy import load_plot_bundle

        result.update(load_plot_bundle(bundle_dir))
    elif bundle_type == BundleType.STATS:
        from scitex_stats.io import load_stats_bundle

        result.update(load_stats_bundle(bundle_dir))

    return result


def save(
    data: Dict[str, Any],
    path: Union[str, Path],
    bundle_type: Optional[str] = None,
    as_zip: bool = False,
    atomic: bool = True,
) -> Path:
    """Save data as a bundle.

    Args:
        data: Bundle data dictionary.
        path: Output path (e.g., 'plot.plot' or 'plot.plot.zip').
        bundle_type: Bundle type ('figure', 'plot', 'stats'). Auto-detected if None.
        as_zip: If True, save as ZIP archive.
        atomic: If True, use atomic write (temp file + rename) for ZIP.

    Returns
    -------
        Path to saved bundle.

    Example:
        >>> save({"spec": {...}, "data": df}, "plot.plot.zip", as_zip=True)
        Path('plot.plot.zip')
    """
    p = Path(path)

    if bundle_type is None:
        bundle_type = get_type(p)
        if bundle_type is None:
            raise ValueError(f"Cannot determine bundle type from path: {path}")

    # Determine if saving as directory or ZIP
    from scitex_io.bundle._types import DIR_EXTENSIONS

    path_str = str(p).lower()
    is_zip_path = any(path_str.endswith(ext) for ext in EXTENSIONS)
    is_dir_path = any(path_str.endswith(ext) for ext in DIR_EXTENSIONS)

    if as_zip or is_zip_path:
        save_as_zip = True
        if is_dir_path:
            zip_path = dir_to_zip_path(p)
        else:
            zip_path = p
        dir_path = zip_to_dir_path(zip_path)
    else:
        save_as_zip = False
        dir_path = p

    # Normalize bundle type for manifest (use new names: plot, figure, stats)
    manifest_type = BundleType.normalize(bundle_type)

    # For direct ZIP saving with atomic writes
    if save_as_zip and atomic and bundle_type != BundleType.FIGURE:
        from scitex_io.bundle._manifest import create_manifest
        from scitex_io.bundle._zip import ZipBundle

        with ZipBundle(zip_path, mode="w") as zb:
            # Write manifest.json first
            manifest = create_manifest(manifest_type)
            zb.write_json("manifest.json", manifest)

            if "spec" in data:
                zb.write_json("spec.json", data["spec"])

            if "style" in data:
                zb.write_json("style.json", data["style"])

            if "data" in data and data["data"] is not None:
                import pandas as pd

                if isinstance(data["data"], pd.DataFrame):
                    zb.write_csv("data.csv", data["data"])

            for key in ["png", "svg", "pdf"]:
                if key in data and data[key] is not None:
                    export_data = data[key]
                    if isinstance(export_data, bytes):
                        zb.write_bytes(f"exports/figure.{key}", export_data)

        return zip_path

    dir_path.mkdir(parents=True, exist_ok=True)

    # Delegate to domain-specific savers
    if bundle_type == BundleType.FIGURE:
        from scitex.io.bundle.kinds._figure import save_figure_bundle

        save_figure_bundle(data, dir_path)
    elif bundle_type == BundleType.PLOT:
        from scitex.io.bundle.kinds._plot._legacy import save_plot_bundle

        save_plot_bundle(data, dir_path)
    elif bundle_type == BundleType.STATS:
        from scitex_stats.io import save_stats_bundle

        save_stats_bundle(data, dir_path)
    else:
        raise ValueError(f"Unknown bundle type: {bundle_type}")

    # Write manifest.json for directory bundles
    from scitex_io.bundle._manifest import write_manifest

    write_manifest(dir_path, manifest_type)

    if save_as_zip:
        pack(dir_path, zip_path)
        shutil.rmtree(dir_path)
        return zip_path

    return dir_path


def copy(
    src: Union[str, Path],
    dst: Union[str, Path],
    overwrite: bool = False,
) -> Path:
    """Copy a bundle from source to destination.

    Handles both directory (.d) and ZIP formats transparently.
    If source is ZIP, extracts to destination directory.
    If source is directory, copies to destination directory.

    Args:
        src: Source bundle path (directory or ZIP).
        dst: Destination path (will be created as directory).
        overwrite: If True, overwrite existing destination.

    Returns
    -------
        Path to copied bundle (directory form).

    Raises
    ------
        BundleNotFoundError: If source bundle doesn't exist.
        FileExistsError: If destination exists and overwrite=False.

    Example:
        >>> copy("gallery/line/plot.plot", "my_project/A.plot")
        >>> copy("template.plot.zip", "output/panel.plot")
    """
    from scitex_io.bundle._types import DIR_EXTENSIONS

    src_path = Path(src)
    dst_path = Path(dst)
    src_str = str(src_path).lower()

    # Check if path is a ZIP or directory bundle
    is_zip_path = any(src_str.endswith(ext) for ext in EXTENSIONS)
    is_dir_path = any(src_str.endswith(ext) for ext in DIR_EXTENSIONS)

    # Validate source exists
    if not src_path.exists():
        # Try alternate form (ZIP <-> directory)
        if is_zip_path:
            alt_path = zip_to_dir_path(src_path)
            if alt_path.exists():
                src_path = alt_path
            else:
                raise BundleNotFoundError(
                    f"Bundle not found: {src} (also tried {alt_path})"
                )
        elif is_dir_path:
            alt_path = dir_to_zip_path(src_path)
            if alt_path.exists():
                src_path = alt_path
            else:
                raise BundleNotFoundError(
                    f"Bundle not found: {src} (also tried {alt_path})"
                )
        else:
            raise BundleNotFoundError(f"Bundle not found: {src}")

    # Handle destination
    if dst_path.exists():
        if overwrite:
            if dst_path.is_dir():
                shutil.rmtree(dst_path)
            else:
                dst_path.unlink()
        else:
            raise FileExistsError(f"Destination exists: {dst}")

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy based on source type
    if src_path.is_dir():
        shutil.copytree(src_path, dst_path)
    elif any(
        str(src_path).lower().endswith(ext) for ext in EXTENSIONS
    ) or zipfile.is_zipfile(src_path):
        unpack(src_path, dst_path)
    else:
        raise ValueError(f"Unknown bundle format: {src_path}")

    return dst_path


# EOF
