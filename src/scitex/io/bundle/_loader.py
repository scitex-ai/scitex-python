#!/usr/bin/env python3
# Timestamp: 2025-12-20
# File: /home/ywatanabe/proj/scitex-code/src/scitex/fts/_bundle/_loader.py

"""SciTeX Bundle loading utilities.

Loads bundles using the new canonical/artifacts/payload/children structure.
Supports backwards compatibility with old flat structure (spec.json at root).

New structure:
    canonical/spec.json     (was node.json)
    canonical/encoding.json (was encoding.json)
    canonical/theme.json    (was theme.json)
    canonical/data_info.json (was data/data_info.json)
    payload/stats.json      (was stats/stats.json)
"""

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

from scitex_io.bundle._storage import get_storage

if TYPE_CHECKING:
    from scitex_io.bundle._dataclasses import DataInfo, Spec
    from .kinds._plot._dataclasses import Encoding, Theme
    from scitex_stats._dataclasses import Stats


def load_bundle_components(
    path: Path,
) -> Tuple[
    Optional["Spec"],
    Optional["Encoding"],
    Optional["Theme"],
    Optional["Stats"],
    Optional["DataInfo"],
]:
    """Load all bundle components from storage.

    Supports both new canonical/ structure and legacy flat structure.

    Args:
        path: Bundle path (directory or ZIP)

    Returns:
        Tuple of (spec, encoding, theme, stats, data_info)
    """
    from scitex_io.bundle._dataclasses import DataInfo, Spec
    from .kinds._plot._dataclasses import Encoding, Theme
    from scitex_stats._dataclasses import Stats

    storage = get_storage(path)

    spec = None
    encoding = None
    theme = None
    stats = None
    data_info = None

    # Detect structure: new (canonical/) or legacy (flat)
    # - New: canonical/spec.json
    # - Legacy v1: node.json at root
    # - Legacy sio.save(): spec.json at root
    if storage.exists("canonical/spec.json"):
        structure = "v2"  # New canonical/ structure
    elif storage.exists("spec.json"):
        structure = "sio"  # sio.save() structure
    else:
        structure = "v1"  # Legacy node.json structure
    is_new_structure = structure == "v2"

    # Spec / spec.json
    if structure == "v2":
        spec_data = storage.read_json("canonical/spec.json")
    elif structure == "sio":
        spec_data = storage.read_json("spec.json")
    else:
        spec_data = storage.read_json("node.json")
    if spec_data:
        spec = Spec.from_dict(spec_data)

    # Encoding
    if is_new_structure:
        encoding_data = storage.read_json("canonical/encoding.json")
    else:
        encoding_data = storage.read_json("encoding.json")
    if encoding_data:
        encoding = Encoding.from_dict(encoding_data)

    # Theme
    if is_new_structure:
        theme_data = storage.read_json("canonical/theme.json")
    else:
        theme_data = storage.read_json("theme.json")
    if theme_data:
        theme = Theme.from_dict(theme_data)

    # Stats (payload for kind=stats, or legacy stats/)
    if is_new_structure:
        stats_data = storage.read_json("payload/stats.json")
    else:
        stats_data = storage.read_json("stats/stats.json")
    if stats_data:
        stats = Stats.from_dict(stats_data)

    # Data info
    if is_new_structure:
        data_info_data = storage.read_json("canonical/data_info.json")
    else:
        data_info_data = storage.read_json("data/data_info.json")
    if data_info_data:
        data_info = DataInfo.from_dict(data_info_data)

    return spec, encoding, theme, stats, data_info


def get_bundle_structure_version(path: Path) -> str:
    """Detect bundle structure version.

    Args:
        path: Bundle path

    Returns:
        "v2" for new canonical/ structure, "v1" for legacy flat structure
    """
    storage = get_storage(path)
    if storage.exists("canonical/spec.json"):
        return "v2"
    return "v1"


__all__ = ["load_bundle_components", "get_bundle_structure_version"]

# EOF
