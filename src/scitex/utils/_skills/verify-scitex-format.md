---
description: Scan Python files and report compliance with the SciTeX script template format.
---

# stx.utils._verify_scitex_format

CLI tool that scans Python source files and checks whether each file follows the SciTeX template convention. Generates a human-readable compliance report.

> This module is not exported via `stx.utils` public API. Run it with `python -m scitex.utils._verify_scitex_format`.

## What it checks

### Required components (all must be present for full compliance)

| Check | Pattern |
|-------|---------|
| `main()` function | `def main(` at line start |
| `parse_args()` function | `def parse_args(` at line start |
| `run_main()` function | `def run_main(` at line start |
| `if __name__ == "__main__":` guard | exact string match |
| `run_main()` body unchanged | 10 specific patterns must be present (see below) |

### Optional components (scored but not required)

| Check | Pattern |
|-------|---------|
| Module docstring | any `"""..."""` |
| `"""Imports"""` section marker | exact string |
| `"""Functions & Classes"""` section marker | exact string |
| `stx.session.start` call | scitex session usage |
| `verbose` parameter | `verbose\s*[:=]\s*(?:bool|True|False)` |

### run_main() template patterns

The `run_main()` body is considered unchanged only when all of these patterns exist in the file:

```
def run_main() -> None:
"""Initialize scitex framework, run main function, and cleanup."""
global CONFIG, CC, sys, plt, rng
import sys
import matplotlib.pyplot as plt
import scitex as stx
args = parse_args()
CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
exit_status = main(args)
stx.session.close(
```

## Compliance score

Each file receives a score from 0.0 to 1.0: `(number of checks passed) / 10`. A file is considered **fully compliant** only when all five required checks pass.

## CLI usage

```bash
# Check current directory
python -m scitex.utils._verify_scitex_format

# Check a specific directory
python -m scitex.utils._verify_scitex_format src/scitex/browser

# Check multiple paths
python -m scitex.utils._verify_scitex_format src/scitex/browser src/scitex/io

# Check a single file
python -m scitex.utils._verify_scitex_format src/scitex/browser/automation/CookieHandler.py

# Save report to file
python -m scitex.utils._verify_scitex_format src/scitex/browser -o report.txt

# Specify base directory for relative path display
python -m scitex.utils._verify_scitex_format src/scitex -b src/scitex
```

## CLI flags

| Flag | Short | Description |
|------|-------|-------------|
| `paths` | positional | Files or directories to scan (default: cwd) |
| `--base-dir` | `-b` | Base for relative path display (default: cwd) |
| `--output` | `-o` | Write report to this file instead of stdout |

## Report format

```
================================================================================
TEMPLATE COMPLIANCE REPORT
================================================================================

Total Python files analyzed: 12
Fully compliant files: 8 (66.7%)
Average compliance score: 78.3%

================================================================================
DETAILED RESULTS (sorted by compliance score)
================================================================================

✗ NON-COMPLIANT [30%] src/scitex/browser/automation/CookieHandler.py
  Lines: 142, Size: 4821 bytes
  ❌ REQUIRED Missing: main(), parse_args(), run_main(), run_main() template format
  ⚠️  OPTIONAL Missing: 'Imports' section, 'Functions & Classes' section, scitex session

⚠ PARTIAL [70%] src/scitex/io/_load.py
  Lines: 88, Size: 2943 bytes
  ❌ REQUIRED Missing: run_main() template format

✓ COMPLIANT [100%] src/scitex/io/_save.py
  Lines: 201, Size: 6871 bytes
```

## Python API (internal)

```python
from scitex.utils._verify_scitex_format import (
    scan_python_files,    # Path list -> Dict[str, FileInfo]
    check_compliance,     # file content str -> TemplateCompliance
    generate_report,      # results dict -> str report
)
from pathlib import Path

files = scan_python_files([Path("src/scitex/io")], base_dir=Path("src/scitex"))
results = {path: (info, check_compliance(info.content)) for path, info in files.items()}
print(generate_report(results))
```

### FileInfo dataclass fields

| Field | Type |
|-------|------|
| `relative_path` | str |
| `content` | str |
| `size` | int (bytes) |
| `lines` | int |

### TemplateCompliance dataclass fields

| Field | Type | Required |
|-------|------|----------|
| `has_main` | bool | yes |
| `has_parse_args` | bool | yes |
| `has_run_main` | bool | yes |
| `has_main_guard` | bool | yes |
| `is_run_main_unchanged` | bool | yes |
| `has_docstring` | bool | optional |
| `has_imports_section` | bool | optional |
| `has_functions_classes_section` | bool | optional |
| `uses_scitex_session` | bool | optional |
| `has_verbose_param` | bool | optional |
| `is_compliant` (property) | bool | — |
| `compliance_score` (property) | float 0–1 | — |
