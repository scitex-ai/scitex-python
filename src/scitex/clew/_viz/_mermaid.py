#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/verify/_viz/_mermaid.py
"""Mermaid diagram generation for verification DAG."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, Optional, Union

from .._chain import VerificationLevel, verify_chain, verify_run
from .._db import get_db
from ._json import file_to_node_id, format_path, generate_dag_json, verify_file_hash
from ._templates import get_html_template

PathMode = Literal["name", "relative", "absolute"]


def generate_mermaid_dag(
    session_id: Optional[str] = None,
    target_file: Optional[str] = None,
    max_depth: int = 10,
    show_files: bool = True,
    show_hashes: bool = False,
    path_mode: PathMode = "name",
) -> str:
    """
    Generate Mermaid diagram for verification DAG.

    Parameters
    ----------
    session_id : str, optional
        Start from this session
    target_file : str, optional
        Start from session that produced this file
    max_depth : int, optional
        Maximum chain depth
    show_files : bool, optional
        Whether to show input/output files as nodes (default: True)
    show_hashes : bool, optional
        Whether to show truncated file hashes (default: False)
    path_mode : str, optional
        How to display file paths: "name", "relative", or "absolute"

    Returns
    -------
    str
        Mermaid diagram code
    """
    db = get_db()
    lines = ["graph TD"]

    if target_file:
        chain = verify_chain(target_file)
        chain_ids = [run.session_id for run in chain.runs]
    elif session_id:
        chain_ids = db.get_chain(session_id)
    else:
        # Full project DAG: all runs
        all_runs = db.list_runs(limit=500)
        chain_ids = [r["session_id"] for r in all_runs]

    if not chain_ids:
        lines.append('    empty["No runs found"]')
        return "\n".join(lines)

    runs_data = _collect_runs_data(chain_ids, db)

    if show_files:
        _generate_detailed_dag(lines, runs_data, show_hashes, path_mode)
    else:
        _generate_simple_dag(lines, runs_data, chain_ids, path_mode)

    _append_class_definitions(lines)
    return "\n".join(lines)


def _collect_runs_data(chain_ids: list, db) -> list:
    """Collect run data for all sessions in chain."""
    runs_data = []
    for sid in chain_ids:
        run = db.get_run(sid)
        verification = verify_run(sid)

        # Check if there's a stored from-scratch verification result
        latest_verification = db.get_latest_verification(sid)
        if (
            latest_verification
            and latest_verification.get("level") == "rerun"
            and latest_verification.get("status") == "verified"
        ):
            # Apply from-scratch level to the verification
            verification.level = VerificationLevel.RERUN

        inputs = db.get_file_hashes(sid, role="input")
        outputs = db.get_file_hashes(sid, role="output")
        runs_data.append(
            {
                "session_id": sid,
                "run": run,
                "verification": verification,
                "inputs": inputs,
                "outputs": outputs,
            }
        )
    return runs_data


def _append_class_definitions(lines: list) -> None:
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


def _generate_simple_dag(
    lines: list, runs_data: list, chain_ids: list, path_mode: PathMode = "name"
) -> None:
    """Generate simple script-only DAG."""
    for data in runs_data:
        sid = data["session_id"]
        run = data["run"]
        verification = data["verification"]
        node_id = sid.replace("-", "_").replace(".", "_")
        status_class = "verified" if verification.is_verified else "failed"
        script_name = format_path(
            run.get("script_path", "unknown") if run else "unknown", path_mode
        )
        lines.append(f'    {node_id}["{script_name}"]:::{status_class}')

    for i in range(len(chain_ids) - 1):
        curr = chain_ids[i].replace("-", "_").replace(".", "_")
        parent = chain_ids[i + 1].replace("-", "_").replace(".", "_")
        lines.append(f"    {parent} --> {curr}")


def _generate_detailed_dag(
    lines: list,
    runs_data: list,
    show_hashes: bool = False,
    path_mode: PathMode = "name",
) -> None:
    """Generate detailed DAG with input/output files and verification status."""
    file_nodes = {}
    failed_files = set()  # Track failed files for propagation
    runs_data = list(reversed(runs_data))

    # First pass: identify all failed files
    for data in runs_data:
        inputs = data["inputs"]
        outputs = data["outputs"]
        for fpath, stored_hash in {**inputs, **outputs}.items():
            if not verify_file_hash(fpath, stored_hash):
                failed_files.add(fpath)

    # Second pass: propagate failures through chain
    for data in runs_data:
        inputs = data["inputs"]
        outputs = data["outputs"]
        # If any input is failed, all outputs are also failed
        has_failed_input = any(fpath in failed_files for fpath in inputs.keys())
        if has_failed_input:
            for fpath in outputs.keys():
                failed_files.add(fpath)

    for i, data in enumerate(runs_data):
        sid = data["session_id"]
        run = data["run"]
        verification = data["verification"]
        inputs = data["inputs"]
        outputs = data["outputs"]

        # Check if this script has failed inputs (propagated failure)
        has_failed_input = any(fpath in failed_files for fpath in inputs.keys())

        _add_script_node(
            lines, i, sid, run, verification, path_mode, show_hashes, has_failed_input
        )
        is_rerun = verification.is_verified_from_scratch
        _add_file_nodes(
            lines,
            f"script_{i}",
            inputs,
            file_nodes,
            show_hashes,
            path_mode,
            "input",
            False,
            failed_files,
        )
        _add_file_nodes(
            lines,
            f"script_{i}",
            outputs,
            file_nodes,
            show_hashes,
            path_mode,
            "output",
            is_rerun,
            failed_files,
        )


def _get_file_icon(filename: str) -> str:
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


def _add_script_node(
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

    # Determine status class with from-scratch distinction
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
    icon = _get_file_icon(script_path)
    short_id = sid.split("_")[-1][:4] if "_" in sid else sid[:8]
    badge = "✓✓" if is_from_scratch else ("✓" if script_verified else "✗")
    # Show script hash if requested
    script_hash = run.get("script_hash", "") if run else ""
    hash_display = f"<br/>{script_hash[:8]}..." if show_hashes and script_hash else ""
    lines.append(
        f'    {node_id}["{badge} {icon} {script_name}<br/>({short_id}){hash_display}"]:::{status_class}'
    )


def _add_file_nodes(
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
        icon = _get_file_icon(fpath)

        if file_id not in file_nodes:
            file_status = verify_file_hash(fpath, stored_hash)
            is_failed = fpath in failed_files or not file_status

            # Determine badge and class
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
                f'    {file_id}[("{badge} {icon} {display_name}{hash_display}")]:::{file_class}'
            )
            file_nodes[file_id] = (fpath, stored_hash)

        if role == "input":
            lines.append(f"    {file_id} --> {script_id}")
        else:
            lines.append(f"    {script_id} --> {file_id}")


def generate_html_dag(
    session_id: Optional[str] = None,
    target_file: Optional[str] = None,
    title: str = "Verification DAG",
    show_hashes: bool = False,
    path_mode: PathMode = "name",
) -> str:
    """Generate interactive HTML visualization for verification DAG."""
    mermaid_code = generate_mermaid_dag(
        session_id=session_id,
        target_file=target_file,
        show_hashes=show_hashes,
        path_mode=path_mode,
    )
    return get_html_template(title, mermaid_code)


def render_dag(
    output_path: Union[str, Path],
    session_id: Optional[str] = None,
    target_file: Optional[str] = None,
    title: str = "Verification DAG",
    show_hashes: bool = False,
    path_mode: PathMode = "name",
) -> Path:
    """
    Render verification DAG to file (HTML, PNG, SVG, JSON, or MMD).

    Parameters
    ----------
    output_path : str or Path
        Output file path. Extension determines format.
    session_id : str, optional
        Start from this session
    target_file : str, optional
        Start from session that produced this file
    title : str, optional
        Title for the visualization
    show_hashes : bool, optional
        Whether to show file hashes
    path_mode : str, optional
        Path display mode

    Returns
    -------
    Path
        Path to the generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ext = output_path.suffix.lower()

    if ext == ".html":
        content = generate_html_dag(
            session_id=session_id,
            target_file=target_file,
            title=title,
            show_hashes=show_hashes,
            path_mode=path_mode,
        )
        output_path.write_text(content)

    elif ext == ".mmd":
        content = generate_mermaid_dag(
            session_id=session_id,
            target_file=target_file,
            show_hashes=show_hashes,
            path_mode=path_mode,
        )
        output_path.write_text(content)

    elif ext == ".json":
        graph_json = generate_dag_json(
            session_id=session_id,
            target_file=target_file,
            path_mode=path_mode,
        )
        output_path.write_text(json.dumps(graph_json, indent=2))

    elif ext in [".png", ".svg"]:
        mermaid = generate_mermaid_dag(
            session_id=session_id,
            target_file=target_file,
            show_hashes=show_hashes,
            path_mode=path_mode,
        )
        # Write mermaid to temp file and compile with mmdc
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid)
            mmd_path = f.name

        try:
            subprocess.run(
                ["mmdc", "-i", mmd_path, "-o", str(output_path)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to mmd file if mmdc fails
            fallback_path = output_path.with_suffix(".mmd")
            fallback_path.write_text(mermaid)
            return fallback_path
        finally:
            Path(mmd_path).unlink(missing_ok=True)

    else:
        raise ValueError(
            f"Unsupported format: {ext}. Use .html, .png, .svg, .json, or .mmd"
        )

    return output_path


# EOF
