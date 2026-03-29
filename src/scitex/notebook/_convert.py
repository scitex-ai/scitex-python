#!/usr/bin/env python3
"""Convert Jupyter notebooks to SciTeX-compatible Python scripts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Union

from ._compile import compile_notebook
from ._parse import get_code_cells, parse_notebook

# IPython magic patterns to strip
_MAGIC_RE = re.compile(r"^\s*[%!].*$", re.MULTILINE)

# Import statement pattern (matches: import x, import x as y, import x.y.z as w, from x import y)
_IMPORT_RE = re.compile(
    r"^(?:import\s+\S+(?:\s+as\s+\S+)?|from\s+\S+\s+import\s+.+)$", re.MULTILINE
)

# Common notebook patterns to convert to SciTeX equivalents
_CONVERSIONS = [
    # plt.show() → stx.io.save(fig, "figure.png")
    (re.compile(r"plt\.show\(\)"), '# stx.io.save(fig, "figure.png")  # was: plt.show()'),
    # plt.savefig("...") → stx.io.save(fig, "...")
    (
        re.compile(r'plt\.savefig\((["\'].*?["\'])\)'),
        r"stx.io.save(fig, \1)  # was: plt.savefig",
    ),
    # df.to_csv("...") → stx.io.save(df, "...")
    (
        re.compile(r'(\w+)\.to_csv\((["\'].*?["\'])\)'),
        r"stx.io.save(\1, \2)  # was: .to_csv",
    ),
    # pd.read_csv("...") → stx.io.load("...")
    (
        re.compile(r'pd\.read_csv\((["\'].*?["\'])\)'),
        r'stx.io.load(\1)  # was: pd.read_csv',
    ),
    # np.save("...", arr) → stx.io.save(arr, "...")
    (
        re.compile(r'np\.save\((["\'].*?["\'])\s*,\s*(.+?)\)'),
        r"stx.io.save(\2, \1)  # was: np.save",
    ),
    # np.load("...") → stx.io.load("...")
    (
        re.compile(r'np\.load\((["\'].*?["\'])\)'),
        r'stx.io.load(\1)  # was: np.load',
    ),
]


def convert_notebook(
    path: Union[str, Path],
    output: Union[str, Path, None] = None,
    order: str = "cell",
    mode: str = "per_cell",
) -> str:
    """Convert a .ipynb notebook to a .py script with @stx.session.

    Parameters
    ----------
    path : str or Path
        Path to the .ipynb file.
    output : str or Path, optional
        Output .py file path. If None, returns string only.
    order : str
        Cell ordering: "cell" (notebook order) or "dag" (execution order
        from clew DB timestamps).
    mode : str
        Conversion mode:
        - "per_cell": Each code cell becomes a separate @stx.session function (default).
        - "unified": All cells merged into a single @stx.session main() function.
          Markdown cells become comments, imports are hoisted, and common
          notebook patterns (plt.show, pd.read_csv, etc.) are converted to
          SciTeX equivalents (stx.io.save/load).

    Returns
    -------
    str
        The generated Python script content.
    """
    path = Path(path)

    if mode == "unified":
        script = _convert_unified(path)
    elif order == "cell":
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


def _convert_unified(path: Path) -> str:
    """Convert notebook into a single @stx.session main() function.

    - Markdown cells become block comments
    - Imports are hoisted to module level
    - Code is merged into main() body
    - Common IO patterns are converted to stx.io equivalents
    """
    all_cells = parse_notebook(path)
    imports: List[str] = []
    body_lines: List[str] = []
    has_plt = False

    for cell in all_cells:
        if cell["cell_type"] == "markdown":
            # Convert markdown to comments
            md_text = cell["source"].strip()
            if not md_text:
                continue
            body_lines.append("")
            for md_line in md_text.splitlines():
                body_lines.append(f"    # {md_line}")
            body_lines.append("")

        elif cell["cell_type"] == "code":
            source = _clean_source(cell["source"])
            if not source.strip():
                continue

            # Separate imports from body code
            cell_imports, cell_body = _separate_imports(source)
            imports.extend(cell_imports)

            if cell_body.strip():
                # Apply SciTeX conversions
                cell_body = _apply_conversions(cell_body)
                body_lines.append("")
                for line in cell_body.splitlines():
                    body_lines.append(f"    {line}" if line.strip() else "")

            # Track matplotlib usage
            if "plt." in source or "matplotlib" in source:
                has_plt = True

    # Deduplicate imports
    seen = set()
    unique_imports = []
    for imp in imports:
        if imp not in seen:
            seen.add(imp)
            unique_imports.append(imp)

    # Filter out imports that stx.session provides (plt is injected)
    filtered_imports = [
        imp
        for imp in unique_imports
        if not imp.startswith("import matplotlib")
        and not imp.startswith("from matplotlib")
        and "matplotlib.pyplot" not in imp
    ]

    # Build script
    lines = [
        "#!/usr/bin/env python3",
        f'"""Converted from {path.name} using scitex notebook convert --mode unified."""',
        "",
        "import scitex as stx",
    ]

    # Add non-scitex imports
    for imp in filtered_imports:
        if "scitex" not in imp:
            lines.append(imp)

    lines.append("")
    lines.append("")

    # Build injected parameters
    injected = ["    CONFIG=stx.INJECTED,", "    logger=stx.INJECTED,"]
    if has_plt:
        injected.append("    plt=stx.INJECTED,")

    lines.append("@stx.session(seed=42)")
    lines.append("def main(")
    lines.extend(injected)
    lines.append("):")
    lines.append(f'    """Analysis pipeline converted from {path.name}."""')

    # Add body
    lines.extend(body_lines)

    lines.append("")
    lines.append("    return 0")
    lines.append("")
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    main()")
    lines.append("")
    lines.append("# EOF")
    lines.append("")

    return "\n".join(lines)


def _separate_imports(source: str) -> tuple:
    """Separate import statements from body code."""
    imports = []
    body_lines = []

    for line in source.splitlines():
        stripped = line.strip()
        if _IMPORT_RE.match(stripped):
            imports.append(stripped)
        else:
            body_lines.append(line)

    return imports, "\n".join(body_lines)


def _apply_conversions(source: str) -> str:
    """Apply SciTeX pattern conversions to source code."""
    for pattern, replacement in _CONVERSIONS:
        source = pattern.sub(replacement, source)
    return source


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
