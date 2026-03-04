#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/verify/_viz/_mermaid.py
"""Mermaid diagram generation for verification DAG."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Literal, Optional, Union

from .._chain import verify_chain
from .._db import get_db
from ._json import generate_dag_json
from ._mermaid_dag import (
    collect_runs_data,
    generate_detailed_dag,
    generate_multi_target_dag,
    generate_simple_dag,
)
from ._mermaid_nodes import append_class_definitions
from ._templates import get_html_template

PathMode = Literal["name", "relative", "absolute"]


def generate_mermaid_dag(
    session_id: Optional[str] = None,
    target_file: Optional[str] = None,
    target_files: Optional[List[str]] = None,
    claims: bool = False,
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
    target_files : list of str, optional
        Start from sessions that produced these files (multi-target DAG)
    claims : bool, optional
        Use registered claims to build DAG (default: False)
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
    # Multi-target DAG mode
    if target_files or claims:
        return generate_multi_target_dag(
            target_files=target_files,
            claims=claims,
            show_files=show_files,
            show_hashes=show_hashes,
            path_mode=path_mode,
        )

    db = get_db()
    lines = ["graph TD"]

    if target_file:
        chain = verify_chain(target_file)
        chain_ids = [run.session_id for run in chain.runs]
    elif session_id:
        chain_ids = db.get_chain(session_id)
    else:
        all_runs = db.list_runs(limit=500)
        chain_ids = [r["session_id"] for r in all_runs]

    if not chain_ids:
        lines.append('    empty["No runs found"]')
        return "\n".join(lines)

    runs_data = collect_runs_data(chain_ids, db)

    if show_files:
        generate_detailed_dag(lines, runs_data, show_hashes, path_mode)
    else:
        generate_simple_dag(lines, runs_data, chain_ids, path_mode)

    append_class_definitions(lines)
    return "\n".join(lines)


def generate_html_dag(
    session_id: Optional[str] = None,
    target_file: Optional[str] = None,
    target_files: Optional[List[str]] = None,
    claims: bool = False,
    title: str = "Verification DAG",
    show_hashes: bool = False,
    path_mode: PathMode = "name",
) -> str:
    """Generate interactive HTML visualization for verification DAG."""
    mermaid_code = generate_mermaid_dag(
        session_id=session_id,
        target_file=target_file,
        target_files=target_files,
        claims=claims,
        show_hashes=show_hashes,
        path_mode=path_mode,
    )
    return get_html_template(title, mermaid_code)


def render_dag(
    output_path: Union[str, Path],
    session_id: Optional[str] = None,
    target_file: Optional[str] = None,
    target_files: Optional[List[str]] = None,
    claims: bool = False,
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
    target_files : list of str, optional
        Start from sessions that produced these files (multi-target DAG)
    claims : bool, optional
        Use registered claims to build DAG (default: False)
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
            target_files=target_files,
            claims=claims,
            title=title,
            show_hashes=show_hashes,
            path_mode=path_mode,
        )
        output_path.write_text(content)

    elif ext == ".mmd":
        content = generate_mermaid_dag(
            session_id=session_id,
            target_file=target_file,
            target_files=target_files,
            claims=claims,
            show_hashes=show_hashes,
            path_mode=path_mode,
        )
        output_path.write_text(content)

    elif ext == ".json":
        graph_json = generate_dag_json(
            session_id=session_id,
            target_file=target_file,
            target_files=target_files,
            claims=claims,
            path_mode=path_mode,
        )
        output_path.write_text(json.dumps(graph_json, indent=2))

    elif ext in [".png", ".svg"]:
        mermaid = generate_mermaid_dag(
            session_id=session_id,
            target_file=target_file,
            target_files=target_files,
            claims=claims,
            show_hashes=show_hashes,
            path_mode=path_mode,
        )
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
