---
description: Compile a .tex file to PDF using pdflatex, xelatex, lualatex, or latexmk. Returns a structured CompileResult with success flag, PDF path, and parsed errors/warnings from the log.
---

# compile_tex / CompileResult

Invoke a system LaTeX compiler on a `.tex` file and return a structured result.

## compile_tex

```python
compile_tex(
    tex_path: str | Path,
    output_dir: str | Path | None = None,
    compiler: str = "pdflatex",
    runs: int = 2,
    clean: bool = True,
    timeout: int = 120,
) -> CompileResult
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tex_path` | `str \| Path` | required | Path to the `.tex` file |
| `output_dir` | `str \| Path \| None` | `None` | Destination for the PDF; defaults to the same directory as the `.tex` file |
| `compiler` | `str` | `"pdflatex"` | Compiler binary: `"pdflatex"`, `"xelatex"`, `"lualatex"`, or `"latexmk"` |
| `runs` | `int` | `2` | Number of passes (needed for cross-references and ToC); ignored when `compiler="latexmk"` |
| `clean` | `bool` | `True` | Remove auxiliary files (`.aux`, `.log`, `.out`, `.toc`, `.lof`, `.lot`, `.bbl`, `.blg`, `.fls`, `.fdb_latexmk`, `.synctex.gz`) after compilation |
| `timeout` | `int` | `120` | Per-pass timeout in seconds |

**Returns** `CompileResult`

**Compiler flags used internally**

- `pdflatex` / `xelatex` / `lualatex`: `-interaction=nonstopmode -halt-on-error -output-directory=<dir>`
- `latexmk`: `-pdf -interaction=nonstopmode -output-directory=<dir>` (single pass, handles multi-pass internally)

**Error cases that return a failed CompileResult without raising**

- `tex_path` does not exist
- `compiler` binary not on `PATH` (exit code 127)
- Compilation times out (exit code 124)
- Any unexpected exception during `subprocess.run`

---

## CompileResult

Dataclass returned by `compile_tex`.

```python
@dataclass
class CompileResult:
    success: bool           # True if exit_code == 0 AND PDF file exists
    pdf_path: Path | None   # Absolute path to generated PDF, or None
    exit_code: int          # Shell exit code of the last compiler run
    stdout: str             # Combined stdout from all passes (labelled "=== Pass N ===")
    stderr: str             # Combined stderr from all passes
    log_content: str        # Raw content of the .log file (empty if clean=True or not found)
    errors: list[str]       # Lines starting with "!" or containing "Error:" / "Fatal error"
    warnings: list[str]     # Lines containing "Warning:", "Underfull", "Overfull"
```

Note: when `clean=True` (default) the `.log` file is deleted before it can be read, so `log_content` will be empty. Set `clean=False` to retain logs.

---

## Examples

```python
from scitex.tex import compile_tex

# Basic compilation — pdflatex, 2 passes, clean auxiliary files
result = compile_tex("manuscript.tex")
if result.success:
    print(f"PDF at: {result.pdf_path}")
else:
    print("Compilation failed")
    for err in result.errors:
        print(" ", err)

# latexmk (handles all passes, bibliography, etc.)
result = compile_tex("manuscript.tex", compiler="latexmk")

# XeLaTeX, custom output directory, keep log for inspection
result = compile_tex(
    "manuscript.tex",
    compiler="xelatex",
    output_dir="./build",
    clean=False,
)
if not result.success:
    print(result.log_content)   # Full .log available because clean=False

# Three passes for complex cross-references
result = compile_tex("thesis.tex", runs=3, clean=False)
print(result.warnings)

# Access raw output
result = compile_tex("draft.tex")
print(result.stdout)    # "=== Pass 1 ===\n...\n=== Pass 2 ===\n..."
print(result.stderr)
print(result.exit_code) # 0 on success
```

## Requirements

A LaTeX distribution must be installed (TeX Live, MiKTeX, MacTeX, etc.) and the chosen compiler binary must be on `PATH`.

Check availability before calling:

```python
import shutil
if shutil.which("pdflatex") is None:
    print("pdflatex not found — install texlive-latex-base")
```
