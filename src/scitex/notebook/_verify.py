#!/usr/bin/env python3
"""Verify notebook sessions and check for untracked IO."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Union

from ._parse import get_code_cells

# Patterns for scitex.io calls
_IO_LOAD_RE = re.compile(r"(?:scitex|stx)\.io\.load\s*\(")
_IO_SAVE_RE = re.compile(r"(?:scitex|stx)\.io\.save\s*\(")
_SESSION_RE = re.compile(r"@(?:scitex|stx)\.session")


def verify_notebook(path: Union[str, Path]) -> List[Dict]:
    """Verify all clew sessions associated with a notebook.

    Finds all runs in the clew DB whose metadata contains this notebook's
    path, then runs L1 (cache) verification on each.

    Parameters
    ----------
    path : str or Path
        Path to the .ipynb file.

    Returns
    -------
    list of dict
        Verification results per session.
    """
    from scitex.clew import get_db, verify_run

    path = Path(path).resolve()
    db = get_db()
    runs = _get_runs_for_notebook(db, str(path))

    results = []
    for run in runs:
        try:
            verification = verify_run(run["session_id"])
            results.append(
                {
                    "session_id": run["session_id"],
                    "status": verification.status.value,
                    "is_verified": verification.is_verified,
                    "started_at": run.get("started_at"),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "session_id": run["session_id"],
                    "status": "error",
                    "is_verified": False,
                    "error": str(exc),
                }
            )

    return results


def check_notebook(path: Union[str, Path]) -> List[Dict]:
    """Find cells with scitex.io calls not wrapped in @scitex.session.

    Parameters
    ----------
    path : str or Path
        Path to the .ipynb file.

    Returns
    -------
    list of dict
        Cells with untracked IO: {index, has_load, has_save, has_session}.
    """
    cells = get_code_cells(path)
    issues = []

    for cell in cells:
        source = cell["source"]
        has_load = bool(_IO_LOAD_RE.search(source))
        has_save = bool(_IO_SAVE_RE.search(source))
        has_session = bool(_SESSION_RE.search(source))

        if (has_load or has_save) and not has_session:
            issues.append(
                {
                    "index": cell["index"],
                    "has_load": has_load,
                    "has_save": has_save,
                    "has_session": has_session,
                }
            )

    return issues


def _get_runs_for_notebook(db, notebook_path: str) -> List[Dict]:
    """Query clew DB for runs associated with a notebook path."""
    runs = db.list_runs(limit=1000)
    result = []
    for run in runs:
        meta_str = run.get("metadata")
        if not meta_str:
            # Also check script_path for notebook path
            sp = run.get("script_path", "")
            if sp and sp.endswith(".ipynb"):
                if str(Path(sp).resolve()) == notebook_path:
                    result.append(run)
            continue
        try:
            meta = json.loads(meta_str)
            nb_path = meta.get("notebook_path")
            if nb_path and str(Path(nb_path).resolve()) == notebook_path:
                result.append(run)
        except (json.JSONDecodeError, TypeError):
            continue

    return sorted(result, key=lambda r: r.get("started_at", ""))


# EOF
