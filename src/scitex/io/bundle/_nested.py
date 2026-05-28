#!/usr/bin/env python3
# Timestamp: 2026-01-07
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/bundle/_nested.py

"""
SciTeX Nested Bundle Access - Transparent access to nested bundles.

Provides unified API to access nested bundles (plot inside figure) regardless
of whether they are stored as:
    - ZIP files (.figure.zip, .plot.zip)
    - Directories (.figure, .plot)
    - Nested paths (Figure1.figure.zip/A.plot or Figure1.figure/A.plot)

Usage:
    from scitex.io.bundle import nested

    # Get plot bundle from inside figure (works with both ZIP and directory)
    plot_data = nested.resolve("Figure1.figure.zip/A.plot")
    plot_data = nested.resolve("Figure1.figure/A.plot")

    # Get specific file from nested bundle
    png_bytes = nested.get_file("Figure1.figure/A.plot/exports/plot.png")
    spec = nested.get_json("Figure1.figure/A.plot/spec.json")

    # Get preview image (common use case)
    preview_bytes = nested.get_preview("Figure1.figure/A.plot")
"""

import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from scitex_io.bundle._types import NestedBundleNotFoundError

__all__ = [
    "resolve",
    "get_file",
    "get_json",
    "get_preview",
    "put_file",
    "put_json",
    "list_files",
    "parse_path",
]


def parse_path(
    path: Union[str, Path],
) -> Tuple[Optional[Path], Optional[str], Optional[str]]:
    """Parse a path to identify parent bundle, nested bundle, and file.

    Handles paths like:
        - Figure1.figure/A.plot
        - Figure1.figure.zip/A.plot
        - Figure1.figure/A.plot/exports/plot.png
        - A.plot (standalone directory)
        - A.plot.zip (standalone ZIP)

    Args:
        path: Path to parse. Can be absolute or relative.

    Returns:
        Tuple of (parent_bundle_path, nested_bundle_name, file_path_within_nested):
        - parent_bundle_path: Path to .figure or .figure.zip, or None if standalone
        - nested_bundle_name: Name of nested bundle (e.g., "A.plot"), or None
        - file_path_within_nested: Path within nested bundle, or None
    """
    p = Path(path)
    parts = p.parts

    parent_bundle = None
    nested_bundle = None
    file_within = None

    # Find the first .figure.zip or .figure component
    figure_idx = None
    for i, part in enumerate(parts):
        if part.endswith(".figure.zip") or part.endswith(".figure"):
            figure_idx = i
            break

    if figure_idx is not None:
        parent_bundle = Path(*parts[: figure_idx + 1])
        remaining = parts[figure_idx + 1 :]

        if remaining:
            if remaining[0].endswith(".plot") or remaining[0].endswith(".plot.zip"):
                nested_bundle = remaining[0]
                if len(remaining) > 1:
                    file_within = str(Path(*remaining[1:]))
            else:
                file_within = str(Path(*remaining))
    else:
        for i, part in enumerate(parts):
            if part.endswith(".plot") or part.endswith(".plot.zip"):
                nested_bundle = part
                parent_bundle = Path(*parts[:i]) if i > 0 else None
                if i + 1 < len(parts):
                    file_within = str(Path(*parts[i + 1 :]))
                break
        else:
            return None, None, str(p)

    return parent_bundle, nested_bundle, file_within


def _find_bundle_path(base_path: Path, prefer_directory: bool = True) -> Optional[Path]:
    """Find the actual bundle path (ZIP or directory).

    Args:
        base_path: Path to search for (with or without .zip extension).
        prefer_directory: If True, prefer directory over ZIP when both exist.
            This is important for figure bundles where panels may be in the directory
            while the ZIP is an older export.

    Returns:
        Path to the bundle (directory or ZIP), or None if not found.
    """
    # Check for ZIP extension (.figure.zip, .plot.zip, .stats.zip)
    name = base_path.name
    if (
        name.endswith(".figure.zip")
        or name.endswith(".plot.zip")
        or name.endswith(".stats.zip")
    ):
        # ZIP path provided - check for directory variant
        dir_path = Path(str(base_path)[:-4])  # Remove .zip
        if prefer_directory and dir_path.exists():
            return dir_path
        if base_path.exists():
            return base_path
        if dir_path.exists():
            return dir_path

    # Check for directory extension (.figure, .plot, .stats)
    if name.endswith(".figure") or name.endswith(".plot") or name.endswith(".stats"):
        zip_path = Path(str(base_path) + ".zip")
        if not prefer_directory and zip_path.exists():
            return zip_path
        if base_path.exists():
            return base_path
        if zip_path.exists():
            return zip_path

    # Direct path
    if base_path.exists():
        return base_path

    return None


def _read_from_zip(zip_path: Path, internal_path: str) -> bytes:
    """Read file from ZIP archive, dynamically searching for nested bundles."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()

        if internal_path in namelist:
            return zf.read(internal_path)

        for name in namelist:
            if name.endswith("/" + internal_path) or name.endswith(internal_path):
                return zf.read(name)

        if ".plot/" in internal_path:
            plot_dir_name, file_in_plot = internal_path.split(".plot/", 1)
            plot_dir = plot_dir_name + ".plot"

            for name in namelist:
                if f"/{plot_dir}/" in name or name.startswith(plot_dir + "/"):
                    if name.endswith("/" + file_in_plot) or name.endswith(file_in_plot):
                        return zf.read(name)

            base_name = plot_dir_name
            for name in namelist:
                if name.endswith(".plot.zip") and base_name in name:
                    plot_data = zf.read(name)
                    return _read_from_nested_zip(plot_data, file_in_plot, name)

        raise NestedBundleNotFoundError(
            f"File not found in {zip_path}: {internal_path}\n"
            f"Available: {namelist[:10]}{'...' if len(namelist) > 10 else ''}"
        )


def _read_from_nested_zip(
    zip_data: bytes, internal_path: str, zip_name: str = ""
) -> bytes:
    """Read file from a ZIP archive stored as bytes (nested ZIP)."""
    import io

    with zipfile.ZipFile(io.BytesIO(zip_data), "r") as nested_zf:
        namelist = nested_zf.namelist()

        if internal_path in namelist:
            return nested_zf.read(internal_path)

        base_name = (
            zip_name.replace(".plot.zip", "").replace(".plot", "") if zip_name else ""
        )
        dir_prefix = f"{base_name}.plot/"

        full_path = dir_prefix + internal_path
        if full_path in namelist:
            return nested_zf.read(full_path)

        for name in namelist:
            if name.endswith("/" + internal_path) or name.endswith(internal_path):
                return nested_zf.read(name)

        raise NestedBundleNotFoundError(
            f"File not found in nested ZIP {zip_name}: {internal_path}\n"
            f"Available: {namelist[:10]}{'...' if len(namelist) > 10 else ''}"
        )


def _read_from_directory(dir_path: Path, internal_path: str) -> bytes:
    """Read file from directory structure."""
    file_path = dir_path / internal_path
    if file_path.exists():
        return file_path.read_bytes()

    # Try alternate form: .plot.zip -> .plot directory
    if ".plot.zip/" in internal_path:
        alt_path = internal_path.replace(".plot.zip/", ".plot/")
        alt_file_path = dir_path / alt_path
        if alt_file_path.exists():
            return alt_file_path.read_bytes()

    raise NestedBundleNotFoundError(f"File not found: {file_path}")


def get_file(path: Union[str, Path]) -> bytes:
    """Get file bytes from a nested bundle path.

    Transparently handles both ZIP and directory bundles.

    Args:
        path: Full path to file, e.g.:
            - "Figure1.figure/A.plot/exports/plot.png"
            - "Figure1.figure.zip/A.plot/exports/plot.png"
            - "/abs/path/Figure1.figure/A.plot/spec.json"

    Returns:
        File contents as bytes.

    Raises:
        NestedBundleNotFoundError: If file or bundle not found.
    """
    parent_bundle, nested_bundle, file_within = parse_path(path)

    if parent_bundle is None and nested_bundle is None:
        p = Path(path)
        if p.exists():
            return p.read_bytes()
        raise NestedBundleNotFoundError(f"File not found: {path}")

    if parent_bundle:
        actual_parent = _find_bundle_path(parent_bundle)
        if actual_parent is None:
            raise NestedBundleNotFoundError(f"Parent bundle not found: {parent_bundle}")

        if nested_bundle and file_within:
            internal_path = f"{nested_bundle}/{file_within}"
        elif nested_bundle:
            internal_path = nested_bundle
        else:
            internal_path = file_within or ""

        if actual_parent.is_file():
            return _read_from_zip(actual_parent, internal_path)
        else:
            return _read_from_directory(actual_parent, internal_path)

    if nested_bundle:
        bundle_path = _find_bundle_path(Path(nested_bundle))
        if bundle_path is None:
            raise NestedBundleNotFoundError(f"Bundle not found: {nested_bundle}")

        if file_within:
            if bundle_path.is_file():
                return _read_from_zip(bundle_path, file_within)
            else:
                return _read_from_directory(bundle_path, file_within)

    raise NestedBundleNotFoundError(f"Cannot resolve path: {path}")


def get_json(path: Union[str, Path]) -> Dict[str, Any]:
    """Get JSON from a nested bundle path.

    Args:
        path: Path to JSON file within bundle.

    Returns:
        Parsed JSON as dictionary.
    """
    data = get_file(path)
    return json.loads(data.decode("utf-8"))


def put_file(path: Union[str, Path], data: bytes) -> None:
    """Write file bytes to a nested bundle path.

    Transparently handles both ZIP and directory bundles.

    Args:
        path: Full path to file, e.g.:
            - "Figure1.figure/A.plot/exports/plot.png"
            - "Figure1.figure.zip/A.plot/exports/plot.png"
        data: File contents as bytes.

    Raises:
        NestedBundleNotFoundError: If bundle not found.
    """
    parent_bundle, nested_bundle, file_within = parse_path(path)

    if parent_bundle is None and nested_bundle is None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return

    if parent_bundle:
        actual_parent = _find_bundle_path(parent_bundle)
        if actual_parent is None:
            raise NestedBundleNotFoundError(f"Parent bundle not found: {parent_bundle}")

        if nested_bundle and file_within:
            internal_path = f"{nested_bundle}/{file_within}"
        elif nested_bundle:
            internal_path = nested_bundle
        else:
            internal_path = file_within or ""

        if actual_parent.is_file():
            _write_to_zip(actual_parent, internal_path, data)
        else:
            _write_to_directory(actual_parent, internal_path, data)
        return

    if nested_bundle:
        bundle_path = _find_bundle_path(Path(nested_bundle))
        if bundle_path is None:
            raise NestedBundleNotFoundError(f"Bundle not found: {nested_bundle}")

        if file_within:
            if bundle_path.is_file():
                _write_to_zip(bundle_path, file_within, data)
            else:
                _write_to_directory(bundle_path, file_within, data)
            return

    raise NestedBundleNotFoundError(f"Cannot resolve path for writing: {path}")


def put_json(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """Write JSON to a nested bundle path.

    Args:
        path: Path to JSON file within bundle.
        data: Dictionary to write as JSON.
    """
    json_bytes = json.dumps(data, indent=2).encode("utf-8")
    put_file(path, json_bytes)


def _write_to_zip(zip_path: Path, internal_path: str, data: bytes) -> None:
    """Write file to a ZIP archive."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        contents = {name: zf.read(name) for name in namelist}

    target_path = None
    for name in namelist:
        if name.endswith("/" + internal_path) or name == internal_path:
            target_path = name
            break
        if f"/{internal_path.split('/')[0]}/" in name:
            idx = name.find(f"/{internal_path.split('/')[0]}/")
            prefix = name[: idx + 1]
            candidate = prefix + internal_path
            if candidate in namelist:
                target_path = candidate
                break

    if target_path is None:
        for name in namelist:
            if internal_path.split("/")[0] + "/" in name:
                idx = name.find(internal_path.split("/")[0] + "/")
                if idx > 0:
                    target_path = name[:idx] + internal_path
                    break
        if target_path is None:
            target_path = internal_path

    contents[target_path] = data

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, file_data in contents.items():
            zf.writestr(name, file_data)


def _write_to_directory(dir_path: Path, internal_path: str, data: bytes) -> None:
    """Write file to directory structure."""
    file_path = dir_path / internal_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)


def get_preview(
    bundle_path: Union[str, Path],
    filename: str = None,
) -> bytes:
    """Get preview PNG from a nested plot bundle.

    Handles .plot and .plot.zip interchangeably. Does not assume the PNG
    filename matches the bundle name.

    Search order:
        1. Specific filename if provided
        2. exports/{basename}.png (bundle name)
        3. exports/plot.png
        4. {basename}.png
        5. plot.png
        6. Any PNG in exports/ not containing 'hitmap' or 'overview'
        7. Any PNG in bundle not containing 'hitmap' or 'overview'

    Args:
        bundle_path: Path to plot bundle (can be nested in figure).
            Handles both .plot and .plot.zip extensions interchangeably.
        filename: Specific filename to look for (optional).

    Returns:
        PNG image bytes.
    """
    parent_bundle, nested_bundle, file_within = parse_path(bundle_path)

    # Build base path, handling .plot ↔ .plot.zip interchangeably
    if parent_bundle and nested_bundle:
        base_path = f"{parent_bundle}/{nested_bundle}"
    elif nested_bundle:
        base_path = nested_bundle
    else:
        base_path = str(bundle_path)

    # Try alternate extension if list_files fails
    def try_with_fallback(path: str) -> List[str]:
        """Try to list files, with .plot ↔ .plot.zip fallback."""
        try:
            return list_files(path)
        except NestedBundleNotFoundError:
            # Try alternate extension
            if path.endswith(".plot"):
                alt_path = path + ".zip"
            elif path.endswith(".plot.zip"):
                alt_path = path[:-4]  # Remove .zip
            else:
                raise
            return list_files(alt_path)

    # Find actual working path
    working_path = base_path
    try:
        files = try_with_fallback(base_path)
        # Determine which path worked
        if base_path.endswith(".plot") and not base_path.endswith(".plot.zip"):
            alt_path = base_path + ".zip"
            try:
                list_files(base_path)
            except NestedBundleNotFoundError:
                working_path = alt_path
        elif base_path.endswith(".plot.zip"):
            alt_path = base_path[:-4]
            try:
                list_files(base_path)
            except NestedBundleNotFoundError:
                working_path = alt_path
    except NestedBundleNotFoundError:
        files = []

    bundle_name = Path(working_path).stem.replace(".plot", "")

    # Standard locations to try
    locations = [
        f"exports/{bundle_name}.png",
        "exports/plot.png",
        f"{bundle_name}.png",
        "plot.png",
    ]

    if filename:
        locations.insert(0, filename)

    # Try standard locations first
    for loc in locations:
        try:
            return get_file(f"{working_path}/{loc}")
        except NestedBundleNotFoundError:
            continue

    # Fallback: find ANY suitable PNG in the bundle
    # Prioritize exports/ directory, then root
    exports_pngs = []
    root_pngs = []

    for f in files:
        if f.endswith(".png") and "hitmap" not in f and "overview" not in f:
            if f.startswith("exports/"):
                exports_pngs.append(f)
            else:
                root_pngs.append(f)

    # Try exports/ PNGs first
    for f in exports_pngs:
        try:
            return get_file(f"{working_path}/{f}")
        except NestedBundleNotFoundError:
            continue

    # Then try root PNGs
    for f in root_pngs:
        try:
            return get_file(f"{working_path}/{f}")
        except NestedBundleNotFoundError:
            continue

    raise NestedBundleNotFoundError(
        f"No preview image found in {bundle_path}. "
        f"Tried: {locations}, then searched {len(files)} files"
    )


def list_files(bundle_path: Union[str, Path]) -> List[str]:
    """List files in a nested bundle.

    Args:
        bundle_path: Path to bundle (nested or standalone).

    Returns:
        List of file paths relative to bundle root.
    """
    parent_bundle, nested_bundle, _ = parse_path(bundle_path)

    if parent_bundle:
        actual_parent = _find_bundle_path(parent_bundle)
        if actual_parent is None:
            raise NestedBundleNotFoundError(f"Bundle not found: {parent_bundle}")

        if actual_parent.is_file():
            with zipfile.ZipFile(actual_parent, "r") as zf:
                namelist = zf.namelist()

                if nested_bundle:
                    files = []

                    for name in namelist:
                        if f"/{nested_bundle}/" in name or name.startswith(
                            nested_bundle + "/"
                        ):
                            if name.startswith(nested_bundle + "/"):
                                rel = name[len(nested_bundle) + 1 :]
                            else:
                                idx = name.find(f"/{nested_bundle}/")
                                rel = name[idx + len(nested_bundle) + 2 :]
                            if rel and not rel.endswith("/"):
                                files.append(rel)

                    if files:
                        return files

                    if nested_bundle.endswith(".plot"):
                        base_name = nested_bundle[:-5]
                        for name in namelist:
                            if name.endswith(".plot.zip") and base_name in name:
                                plot_data = zf.read(name)
                                return _list_nested_zip_files(plot_data, name)

                    return files
                else:
                    return [n for n in namelist if not n.endswith("/")]
        else:
            target = actual_parent
            if nested_bundle:
                # Prefer directory over ZIP when both exist
                if nested_bundle.endswith(".plot.zip"):
                    dir_target = actual_parent / nested_bundle[:-4]  # Remove .zip
                    if dir_target.exists():
                        target = dir_target
                    else:
                        target = actual_parent / nested_bundle
                elif nested_bundle.endswith(".plot"):
                    target = actual_parent / nested_bundle
                    if not target.exists():
                        # Try with .zip
                        zip_target = actual_parent / (nested_bundle + ".zip")
                        if zip_target.exists():
                            target = zip_target
                else:
                    target = actual_parent / nested_bundle

            if not target.exists():
                raise NestedBundleNotFoundError(f"Bundle not found: {target}")

            return [
                str(f.relative_to(target)) for f in target.rglob("*") if f.is_file()
            ]

    bundle = Path(bundle_path)
    actual = _find_bundle_path(bundle)
    if actual is None:
        raise NestedBundleNotFoundError(f"Bundle not found: {bundle_path}")

    if actual.is_file():
        with zipfile.ZipFile(actual, "r") as zf:
            return [n for n in zf.namelist() if not n.endswith("/")]
    else:
        return [str(f.relative_to(actual)) for f in actual.rglob("*") if f.is_file()]


def _list_nested_zip_files(zip_data: bytes, zip_name: str = "") -> List[str]:
    """List files in a nested ZIP archive."""
    import io

    with zipfile.ZipFile(io.BytesIO(zip_data), "r") as nested_zf:
        namelist = nested_zf.namelist()

        base_name = (
            zip_name.replace(".plot.zip", "").replace(".plot", "") if zip_name else ""
        )
        dir_prefix = f"{base_name}.plot/"

        files = []
        for name in namelist:
            if name.startswith(dir_prefix):
                rel = name[len(dir_prefix) :]
                if rel and not rel.endswith("/"):
                    files.append(rel)
            elif not name.endswith("/"):
                files.append(name)

        return files


def resolve(
    bundle_path: Union[str, Path],
    extract_to: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load a nested bundle's data.

    Transparently handles:
        - Standalone .plot or .plot.zip
        - Nested .plot inside .figure
        - Nested .plot inside .figure.zip

    Args:
        bundle_path: Path to bundle, e.g.:
            - "Figure1.figure/A.plot"
            - "Figure1.figure.zip/A.plot"
            - "A.plot"
            - "A.plot.zip"
        extract_to: If provided, extract ZIP contents to this directory.

    Returns:
        Dictionary with bundle data:
            - 'spec': Parsed spec.json
            - 'style': Parsed style.json (if exists)
            - 'data': CSV data as DataFrame (if exists)
            - 'path': Original path
            - 'is_nested': Whether bundle is nested in another
            - 'files': List of files in bundle
    """
    result = {
        "path": str(bundle_path),
        "is_nested": False,
        "spec": None,
        "style": None,
        "data": None,
        "files": [],
    }

    parent_bundle, nested_bundle, _ = parse_path(bundle_path)
    result["is_nested"] = parent_bundle is not None and nested_bundle is not None

    try:
        result["files"] = list_files(bundle_path)
    except Exception:
        result["files"] = []

    try:
        result["spec"] = get_json(f"{bundle_path}/spec.json")
    except NestedBundleNotFoundError:
        bundle_name = Path(bundle_path).stem.replace(".plot", "")
        try:
            result["spec"] = get_json(f"{bundle_path}/{bundle_name}.json")
        except NestedBundleNotFoundError:
            pass

    try:
        result["style"] = get_json(f"{bundle_path}/style.json")
    except NestedBundleNotFoundError:
        pass

    try:
        import io

        import pandas as pd

        csv_bytes = get_file(f"{bundle_path}/data.csv")
        result["data"] = pd.read_csv(io.BytesIO(csv_bytes))
    except (NestedBundleNotFoundError, ImportError):
        bundle_name = Path(bundle_path).stem.replace(".plot", "")
        try:
            import io

            import pandas as pd

            csv_bytes = get_file(f"{bundle_path}/{bundle_name}.csv")
            result["data"] = pd.read_csv(io.BytesIO(csv_bytes))
        except (NestedBundleNotFoundError, ImportError):
            pass

    return result


# EOF
