#!/usr/bin/env python3
# Timestamp: 2026-01-07
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/bundle/_children.py

"""Child embedding for composite bundles.

This module handles embedding child bundles into composite containers.
Children are stored in the children/ directory with UUID-based names to avoid
collisions, while labels and positions are stored in layout.panels.

Design principles:
- Use child's own spec.id (from canonical/spec.json) for naming
- Handle collisions with _2, _3, etc. suffixes
- Return (child_name, child_id) tuple for identity tracking
- Always validate child is valid bundle
"""

import tempfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Tuple, Union

from scitex_io.bundle._storage import Storage, get_storage

if TYPE_CHECKING:
    from ._Bundle import Bundle


class ValidationError(Exception):
    """Error raised when bundle validation fails."""

    pass


def embed_child(
    container_storage: Storage,
    child_path: Union[str, Path],
    validate: bool = False,  # Default False for WIP workflows
) -> Tuple[str, str]:
    """Embed a child bundle into container's children/ directory.

    Uses the child's own spec.id (from canonical/spec.json) for naming to
    preserve identity. Handles collisions with _2, _3, etc. suffixes.

    Args:
        container_storage: Storage for the container bundle
        child_path: Path to child bundle (.zip or directory)
        validate: Validate child is valid bundle (default False for WIP)

    Returns:
        (child_name, child_id):
            child_name: Filename in children/ (e.g., "690b1931.zip" or "690b1931_2.zip")
            child_id: Full UUID from child's spec.json (for identity tracking)

    Raises:
        ValidationError: If validate=True and child is invalid bundle
        FileNotFoundError: If child path doesn't exist
    """
    child_path = Path(child_path)
    if not child_path.exists():
        raise FileNotFoundError(f"Child bundle not found: {child_path}")

    # Load child bundle to get its spec.id and optionally validate
    from ._Bundle import Bundle

    child_bundle = Bundle(child_path)

    if validate:
        errors = child_bundle.validate()
        if errors:
            raise ValidationError(f"Invalid child bundle: {errors}")

    # Get child's identity
    full_child_id = child_bundle.spec.id
    short_id = full_child_id[:8]

    # Determine child filename with collision handling
    child_name = f"{short_id}.zip"
    suffix = 2
    while container_storage.exists(f"children/{child_name}"):
        child_name = f"{short_id}_{suffix}.zip"
        suffix += 1

    # Copy child bundle into children/ directory
    _copy_child_to_storage(container_storage, child_path, child_name)

    return child_name, full_child_id


def _copy_child_to_storage(
    container_storage: Storage,
    child_path: Path,
    child_name: str,
) -> None:
    """Copy child bundle into container's children/ directory.

    Handles both ZIP and directory child bundles, always storing as ZIP.
    The child ZIP uses a prefix matching its name (for proper unzip behavior).
    """
    import io

    dest_path = f"children/{child_name}"
    # Use child_name (e.g., "6352df06.zip") stem as prefix
    child_prefix = child_name.replace(".zip", "") + "/"

    if child_path.suffix == ".zip":
        # Read ZIP contents and copy to container
        with zipfile.ZipFile(child_path, "r") as zf:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out_zf:
                # Get original prefix (e.g., "my_plot/" from "my_plot.zip")
                orig_prefix = child_path.stem + "/"
                for item in zf.namelist():
                    if item.endswith("/"):  # Skip directory entries
                        continue
                    data = zf.read(item)
                    # Strip original prefix and add new prefix
                    if item.startswith(orig_prefix):
                        rel_path = item[len(orig_prefix) :]
                    else:
                        rel_path = item
                    out_zf.writestr(child_prefix + rel_path, data)

            container_storage.write(dest_path, buf.getvalue())
    else:
        # Directory bundle: create ZIP from directory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out_zf:
            for item in child_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(child_path)
                    out_zf.writestr(child_prefix + str(rel_path), item.read_bytes())

        container_storage.write(dest_path, buf.getvalue())


def load_embedded_children(
    container_path: Union[str, Path],
) -> Dict[str, "Bundle"]:
    """Load all embedded children from children/ directory.

    Args:
        container_path: Path to container bundle

    Returns:
        Dict mapping child_name -> Bundle object
    """

    container_path = Path(container_path)
    storage = get_storage(container_path)

    children = {}
    for item in storage.list():
        if item.startswith("children/") and item.endswith(".zip"):
            child_name = item.split("/", 1)[1]
            # Extract child to temp and load
            child_bundle = _load_child_from_storage(storage, child_name)
            if child_bundle:
                children[child_name] = child_bundle

    return children


def _load_child_from_storage(
    storage: Storage,
    child_name: str,
) -> "Bundle":
    """Load a single child bundle from storage.

    Extracts child ZIP to temp directory and loads as Bundle.
    The temp file name matches the prefix inside the ZIP.

    NOTE: Temp files are kept alive because Bundle.validate() needs to
    access storage for file existence checks. The OS will clean up
    temp files eventually, or they can be cleaned up explicitly.
    """
    from ._Bundle import Bundle

    child_path = f"children/{child_name}"

    # Check if child exists
    if not storage.exists(child_path):
        return None

    # Read child ZIP data
    child_data = storage.read(child_path)

    # Create temp directory and use matching filename
    # The child ZIP has files prefixed with child_name stem (e.g., "6352df06/canonical/...")
    # ZipStorage uses the file stem as prefix, so temp file must match
    tmp_dir = Path(tempfile.mkdtemp())
    tmp_path = tmp_dir / child_name  # Use same name to match internal prefix

    tmp_path.write_bytes(child_data)
    bundle = Bundle(tmp_path)
    # Store temp path reference on Bundle object for potential cleanup
    bundle._temp_path = tmp_path
    bundle._temp_dir = tmp_dir
    return bundle


__all__ = [
    "embed_child",
    "load_embedded_children",
    "ValidationError",
]

# EOF
