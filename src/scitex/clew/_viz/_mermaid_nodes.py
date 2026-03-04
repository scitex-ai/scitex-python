#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_viz/_mermaid_nodes.py
"""Node-building helpers for Mermaid DAG diagrams."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from ._json import file_to_node_id, format_path, verify_file_hash

PathMode = Literal["name", "relative", "absolute"]


def get_file_icon(filename: str) -> str:
    """Get icon emoji for file type."""
    ext = Path(filename).suffix.lower()
    icons = {
        ".py": "🐍",
        ".csv": "📊",
        ".json": "📋",
        ".yaml": "⚙️",
        ".yml": "⚙️",
        ".png": "🖼️",
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".svg": "🖼️",
        ".pdf": "📄",
        ".html": "🌐",
        ".txt": "📝",
        ".md": "📝",
        ".npy": "🔢",
        ".npz": "🔢",
        ".pkl": "📦",
        ".pickle": "📦",
        ".h5": "💾",
        ".hdf5": "💾",
        ".mat": "🔬",
        ".sh": "🖥️",
    }
    return icons.get(ext, "📄")


def append_class_definitions(lines: list) -> None:
    """Append Mermaid class definitions for styling."""
    lines.append("")
    lines.append("    classDef script fill:#87CEEB,stroke:#4169E1,stroke-width:2px")
    lines.append("    classDef verified fill:#90EE90,stroke:#228B22")
    lines.append(
        "    classDef verified_scratch fill:#90EE90,stroke:#228B22,stroke-width:4px"
    )
    lines.append("    classDef failed fill:#FFB6C1,stroke:#DC143C")
    lines.append("    classDef file fill:#FFF8DC,stroke:#DAA520")
    lines.append("    classDef file_ok fill:#90EE90,stroke:#228B22")
    lines.append("    classDef file_rerun fill:#90EE90,stroke:#228B22,stroke-width:4px")
    lines.append("    classDef file_bad fill:#FFB6C1,stroke:#DC143C")


def add_script_node(
    lines: list,
    idx: int,
    sid: str,
    run: dict,
    verification,
    path_mode: PathMode,
    show_hashes: bool = False,
    has_failed_input: bool = False,
) -> None:
    """Add a script node to the diagram."""
    node_id = f"script_{idx}"
    script_verified = verification.is_verified and not has_failed_input
    is_from_scratch = verification.is_verified_from_scratch and not has_failed_input

    if has_failed_input:
        status_class = "failed"
    elif is_from_scratch:
        status_class = "verified_scratch"
    elif script_verified:
        status_class = "verified"
    else:
        status_class = "failed"

    script_path = run.get("script_path", "unknown") if run else "unknown"
    script_name = format_path(script_path, path_mode)
    icon = get_file_icon(script_path)
    short_id = sid.split("_")[-1][:4] if "_" in sid else sid[:8]
    badge = "✓✓" if is_from_scratch else ("✓" if script_verified else "✗")
    script_hash = run.get("script_hash", "") if run else ""
    hash_display = f"<br/>{script_hash[:8]}..." if show_hashes and script_hash else ""
    lines.append(
        f'    {node_id}["{badge} {icon} {script_name}'
        f'<br/>({short_id}){hash_display}"]:::{status_class}'
    )


def add_file_nodes(
    lines: list,
    script_id: str,
    files: dict,
    file_nodes: dict,
    show_hashes: bool,
    path_mode: PathMode,
    role: str,
    is_script_rerun_verified: bool = False,
    failed_files: set = None,
) -> None:
    """Add file nodes and connections to the diagram."""
    failed_files = failed_files or set()

    for fpath, stored_hash in files.items():
        display_name = format_path(fpath, path_mode)
        file_id = file_to_node_id(Path(fpath).name)
        icon = get_file_icon(fpath)

        if file_id not in file_nodes:
            file_status = verify_file_hash(fpath, stored_hash)
            is_failed = fpath in failed_files or not file_status

            if is_failed:
                file_class = "file_bad"
                badge = "✗"
            elif role == "output" and is_script_rerun_verified:
                file_class = "file_rerun"
                badge = "✓✓"
            else:
                file_class = "file_ok"
                badge = "✓"

            hash_display = f"<br/>{stored_hash[:8]}..." if show_hashes else ""
            lines.append(
                f'    {file_id}[("{badge} {icon} {display_name}'
                f'{hash_display}")]:::{file_class}'
            )
            file_nodes[file_id] = (fpath, stored_hash)

        if role == "input":
            lines.append(f"    {file_id} --> {script_id}")
        else:
            lines.append(f"    {script_id} --> {file_id}")


# EOF
