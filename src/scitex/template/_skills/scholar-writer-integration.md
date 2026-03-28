---
description: Set up a symlink so scitex.scholar's bibliography file is shared directly with the LaTeX manuscript directory, eliminating bibliography duplication.
---

# Scholar-Writer Integration

When a project contains both a writer (LaTeX) directory and a scholar (bibliography management) directory, this integration creates a symlink so both components read from the same `.bib` file.

## Purpose

`scitex.scholar` writes enriched bibliography to `scholar/bib_files/merged_scholar.bib`. The LaTeX compiler reads bibliography from `00_shared/bib_files/`. Instead of copying or duplicating the file, a symlink is created so there is a single source of truth.

## setup_scholar_writer_integration

```python
def setup_scholar_writer_integration(
    project_path: Path,
    force: bool = False,
) -> Dict[str, any]
```

Returns:
```python
{
    "success": bool,
    "layout": "nested" | "standalone" | "unknown",
    "scholar_dir": str,          # absolute path to scholar bib_files
    "symlink_created": bool,
    "errors": list[str],
}
```

### Layout Detection

The function detects one of two project layouts by probing for the writer bib directory:

**Standalone layout** (flat clone of scitex-writer):
```
project/
├── 00_shared/bib_files/          <- detected here
└── scholar/bib_files/            <- created here
    └── merged_scholar.bib

project/00_shared/bib_files/merged_scholar.bib -> ../../scholar/bib_files/merged_scholar.bib
```

**Nested layout** (scitex ecosystem, writer under `scitex/`):
```
project/
├── scitex/writer/00_shared/bib_files/    <- detected here
└── scitex/scholar/bib_files/             <- created here
    └── merged_scholar.bib

project/scitex/writer/00_shared/bib_files/merged_scholar.bib
    -> ../../../../scitex/scholar/bib_files/merged_scholar.bib
```

If neither directory exists, returns `layout="unknown"` and skips silently.

### Behavior

1. Detects project layout
2. Creates `scholar/bib_files/` (or `scitex/scholar/bib_files/`)
3. Creates `merged_scholar.bib` placeholder if it does not exist
4. Creates relative symlink from writer bib_files to scholar bib_files
5. If `force=True`, removes and recreates the symlink even if it already exists

### Example

```python
from pathlib import Path
from scitex.template import setup_scholar_writer_integration

result = setup_scholar_writer_integration(Path("./my_project"))

if result["success"]:
    print(f"Layout: {result['layout']}")
    print(f"Scholar dir: {result['scholar_dir']}")
    if result["symlink_created"]:
        print("Bibliography symlink created")
else:
    print(f"Errors: {result['errors']}")
```

### Force Recreate

```python
# Recreate symlink even if it already exists
result = setup_scholar_writer_integration(
    Path("./my_project"),
    force=True,
)
```

## ensure_integration

Convenience wrapper that returns a single `bool`.

```python
def ensure_integration(project_path: Path) -> bool
```

```python
from scitex.template import ensure_integration

ok = ensure_integration(Path("./my_project"))
# True if integration is set up (or already existed), False on error
```

## Automatic Invocation During Clone

`setup_scholar_writer_integration` is called automatically as part of `clone_project` (step 8 of the clone pipeline). Explicit calls are only needed when:

- Creating a project manually without using a clone function
- The writer directory was added after initial project creation
- The symlink was accidentally deleted and needs to be recreated (`force=True`)

## Placeholder bib Content

When `merged_scholar.bib` is created fresh it contains a header comment:
```bibtex
% ============================================================
% SciTeX Scholar Bibliography
% ============================================================
% This file is automatically populated when you:
% 1. Upload BibTeX files through Scholar
% 2. Save papers from search results
% 3. Run bibliography merge
% ...
```
