---
description: LaTeX compilation — Writer class, compile_manuscript/supplementary/revision, CompilationResult dataclass, project creation.
---

# Compilation

## Writer class

```python
Writer(
    project_dir,           # Path — project directory (created if absent)
    name=None,             # str — project name (used only when creating)
    git_strategy='child',  # 'child' | 'parent' | 'origin' | None
    branch=None,           # str — template branch to clone
    tag=None,              # str — template tag to clone
)
```

`git_strategy` values:
- `'child'` — isolated git inside project directory (default)
- `'parent'` — use parent repository's git
- `'origin'` — preserve template's original git history
- `None` / `'none'` — no git initialization

If `project_dir` already exists, Writer attaches without modification. If it does not exist, the writer template is cloned from the scitex-writer repository.

### Basic usage

```python
from scitex.writer import Writer
from pathlib import Path

writer = Writer(Path("my_paper"))

# Compile manuscript → PDF
result = writer.compile_manuscript()
if result.success:
    print(f"PDF: {result.output_pdf}")
else:
    print(result.stderr)
    for err in result.errors:
        print(err)
```

## compile_manuscript

```python
Writer.compile_manuscript(
    timeout=300,           # int — max seconds (default 300)
    log_callback=None,     # callable(line: str) — live log
    progress_callback=None # callable(pct: int, msg: str) — progress
) -> CompilationResult
```

Runs `scripts/shell/compile_manuscript.sh` inside the project. Supports live streaming via callbacks.

### Options (module-level via `compile` submodule)

```python
result = writer.compile_manuscript()
# Equivalent low-level control:
import scitex.writer as sw
result = sw.compile.manuscript(
    project_dir,
    timeout=300,
    no_figs=False,    # exclude figures
    no_tables=False,  # exclude tables
    draft=False,      # draft mode (fast, lower quality)
    dark_mode=False,  # dark color scheme
    quiet=False,      # suppress stdout
)
```

## compile_supplementary

```python
Writer.compile_supplementary(
    timeout=300,
    log_callback=None,
    progress_callback=None,
) -> CompilationResult
```

Runs `scripts/shell/compile_supplementary.sh`. Same return type and callback contract as `compile_manuscript`.

```python
result = writer.compile_supplementary()
if result.success:
    print(f"Supplementary PDF: {result.output_pdf}")
```

## compile_revision

```python
Writer.compile_revision(
    track_changes=False,   # bool — enable latexdiff change marks
    timeout=300,
    log_callback=None,
    progress_callback=None,
) -> CompilationResult
```

Runs `scripts/shell/compile_revision.sh`. When `track_changes=True`, a diff PDF is also produced and stored in `result.diff_pdf`.

```python
result = writer.compile_revision(track_changes=True)
if result.success:
    print(f"Revision PDF: {result.output_pdf}")
    if result.diff_pdf:
        print(f"Diff PDF:     {result.diff_pdf}")
```

## CompilationResult dataclass

```python
@dataclass
class CompilationResult:
    success: bool           # True if exit_code == 0
    exit_code: int
    stdout: str
    stderr: str
    output_pdf: Optional[Path] = None   # main compiled PDF
    diff_pdf:   Optional[Path] = None   # tracked-changes PDF
    log_file:   Optional[Path] = None   # .log file path
    duration:   float        = 0.0      # wall time in seconds
    errors:     list         = field(default_factory=list)   # LaTeXIssue objects
    warnings:   list         = field(default_factory=list)
```

`str(result)` produces a human-readable summary. `result.errors` contains parsed LaTeX errors as `LaTeXIssue` objects with line number and message.

## ensure_workspace

```python
stx.writer.ensure_workspace(
    project_dir,           # str or Path — root project directory
    git_strategy='child',  # forwarded to Writer
    **kwargs,              # branch, tag, etc.
) -> pathlib.Path
```

Idempotent helper: creates `{project_dir}/scitex/writer/` if absent, returns the path. Uses the conventional sub-path so all projects have a consistent layout.

```python
import scitex as stx

ws = stx.writer.ensure_workspace("~/research/paper1")
writer = stx.writer.Writer(ws)
```

## Document trees

`ManuscriptTree`, `SupplementaryTree`, `RevisionTree` are dataclasses exposing structured paths inside a project:

```python
from scitex.writer import ManuscriptTree

tree = ManuscriptTree(root=Path("my_paper"))
tree.verify_structure()   # raises if required files missing
print(tree.contents)      # path to sections directory
print(tree.archive)       # path to archive directory
print(tree.git_root)      # path to .git root
```

## MCP

```
writer_compile_manuscript  project_dir=./my-paper
writer_compile_supplementary  project_dir=./my-paper
writer_compile_revision  project_dir=./my-paper  track_changes=true
writer_compile_content  content="\\documentclass{article}..."
writer_get_pdf  project_dir=./my-paper  doc_type=manuscript
writer_list_document_types
writer_get_project_info  project_dir=./my-paper
writer_clone_project  project_dir=./new-paper
writer_update_project  project_dir=./my-paper
```

## CLI

```bash
scitex writer compile manuscript ./my-paper
scitex writer compile supplementary ./my-paper
scitex writer compile revision ./my-paper --track-changes
scitex writer compile revision ./my-paper   # no change marks
```
