#!/usr/bin/env python3
"""Parse Jupyter notebook files using stdlib json (no nbformat dependency)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Union


def parse_notebook(path: Union[str, Path]) -> List[Dict]:
    """Parse a .ipynb file and extract code cells.

    Parameters
    ----------
    path : str or Path
        Path to the .ipynb file.

    Returns
    -------
    list of dict
        Code cells with keys: index, source, cell_id, cell_type.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Notebook not found: {path}")
    if path.suffix != ".ipynb":
        raise ValueError(f"Not a notebook file: {path}")

    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    result = []
    for idx, cell in enumerate(cells):
        cell_type = cell.get("cell_type", "")
        source_lines = cell.get("source", [])
        source = (
            "".join(source_lines) if isinstance(source_lines, list) else source_lines
        )
        cell_id = cell.get("id", f"cell_{idx}")

        result.append(
            {
                "index": idx,
                "source": source,
                "cell_id": cell_id,
                "cell_type": cell_type,
            }
        )

    return result


def get_code_cells(path: Union[str, Path]) -> List[Dict]:
    """Parse notebook and return only code cells.

    Parameters
    ----------
    path : str or Path
        Path to the .ipynb file.

    Returns
    -------
    list of dict
        Code cells only.
    """
    return [c for c in parse_notebook(path) if c["cell_type"] == "code"]


def get_notebook_name(path: Union[str, Path]) -> str:
    """Return the notebook stem name without extension."""
    return Path(path).stem


# EOF
