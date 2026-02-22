#!/usr/bin/env python3
"""Convert Jupyter notebooks to SciTeX-compatible Python scripts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Union

from ._compile import compile_notebook
from ._parse import get_code_cells

# IPython magic patterns to strip
_MAGIC_RE = re.compile(r"^\s*[%!].*$", re.MULTILINE)


def convert_notebook(
    path: Union[str, Path],
    output: Union[str, Path, None] = None,
    order: str = "cell",
) -> str:
    """Convert a .ipynb notebook to a .py script with @scitex.session.

    Parameters
    ----------
    path : str or Path
        Path to the .ipynb file.
    output : str or Path, optional
        Output .py file path. If None, returns string only.
    order : str
        Cell ordering: "cell" (notebook order) or "dag" (execution order
        from clew DB timestamps).

    Returns
    -------
    str
        The generated Python script content.
    """
    path = Path(path)

    if order == "cell":
        script = _convert_cell_order(path)
    elif order == "dag":
        script = _convert_dag_order(path)
    else:
        raise ValueError(f"Invalid order: {order!r}. Must be 'cell' or 'dag'.")

    if output is not None:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(script, encoding="utf-8")

    return script


def _convert_cell_order(path: Path) -> str:
    """Convert notebook in cell index order."""
    cells = get_code_cells(path)
    lines = _script_header(path)

    for cell in cells:
        source = _clean_source(cell["source"])
        if not source.strip():
            continue

        idx = cell["index"]
        func_name = f"cell_{idx:02d}"

        lines.append("")
        lines.append("@stx.session")
        lines.append(f"def {func_name}():")
        for line in source.splitlines():
            lines.append(f"    {line}" if line.strip() else "")
        lines.append("    return 0")
        lines.append("")
        lines.append(f"{func_name}()")
        lines.append("")

    return "\n".join(lines)


def _convert_dag_order(path: Path) -> str:
    """Convert notebook in DAG execution order from clew DB."""
    compiled = compile_notebook(path)

    if not compiled.execution_order:
        # No execution history; fall back to cell order
        return _convert_cell_order(path)

    return compiled.to_script()


def _clean_source(source: str) -> str:
    """Strip IPython magics and clean up source code."""
    return _MAGIC_RE.sub("", source)


def _script_header(path: Path) -> List[str]:
    """Generate script header."""
    return [
        "#!/usr/bin/env python3",
        f'"""Converted from {path.name}."""',
        "",
        "import scitex as stx",
        "",
    ]


# EOF
