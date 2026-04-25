---
name: repo-layout-src-tests-scripts-examples
description: Canonical top-level repo layout for every SciTeX package and every research project using SciTeX — what belongs in `src/` (shipped code, versioned), `tests/` (pytest, one-test-file-per-module mirror), `scripts/` (reproducible pipelines invoked with `@stx.session`), `examples/` (runnable doctest-backed snippets), `references/` (third-party paper PDFs, datasets, external API dumps — gitignored if heavy), and what must NOT live at the top level. Use when scaffolding a new repo or auditing a stray file.
canonical-location: scitex-python/src/scitex/_skills/general/02_repo_01_layout-src-tests-scripts-examples.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

## Code Organization

### ./src
- ./src is mainly for python packages
  - Minimal dependency for other scitex packages
- e.g., <scitex-package>/src/<scitex_package>/path/to/file.py

### ./scripts
- scripts is mainly for project maintenance and research experiments
  - e.g., <scitex-package>/scripts/... <FIXME>

### ./examples
- Use scitex packages, especially for scitex.{session,io,plt}
- Ensure to have numbered prefix
  - e.g., <scitex-package>/examples/01_<descriptive-filename>.py
  - e.g., <scitex-package>/examples/01_<descriptive-filename>_out/
- Git track and push example outputs 
  - This allows users to see outputs on GitHub
- Some outputs of example code will be directly linked/rendered in README.md as assets
- All example code must actually work
  - To ensure this, ./tests should include tests for examples to ensure this
    - e.g., ./tests/examples/test_01_<descriptive-filename>.py
- Examples should include agentic demonstrations
  - e.g., MCP and prompt
  - e.g., Skills and prompt

### ./tests
- Control by pyproject.toml
- Use pytest wisely
- For large tests, consider using computational remote hosts
  - e.g., <scitex-package>/tests/<scitex_package>/path/to/test_file.py

### ./references
- External/upstream material kept verbatim for provenance and reproducibility
  - e.g., specs, third-party docs, benchmark datasets, paper PDFs
- Read-only — do NOT edit contents; only add/remove files
- Pin with explicit version/commit/DOI in filename or sidecar README
  - e.g., <scitex-package>/references/<source>_<version-or-sha>/
- Never imported from `src/`; consumed by tests, scripts, or examples as fixtures
- Large binaries → prefer Git LFS or fetch-on-demand script, not committed blobs
- Each subdir should have a one-line `README.md` stating source URL + retrieval date

### ./templates / ./assets — wheel-vs-git payload separation

Some packages ship **bulky content** that's part of the project source-of-truth on GitHub but should NOT bloat the PyPI wheel:

- `scitex-template/templates/<id>/` — six project scaffolds (~22 MB)
- assets/data/example outputs that exceed a few hundred KB

The pattern: vendor the content in git, exclude it from the wheel via hatch, fetch it on first use into the package's `~/.scitex/<pkg-short>/` cache.

```toml
# pyproject.toml
[tool.hatch.build.targets.wheel]
packages = ["src/<pkg>"]
# templates/ is NOT in the wheel — populated at runtime by a shallow
# clone of this repo into ~/.scitex/<pkg-short>/cache/ on first use.

[tool.hatch.build.targets.sdist]
include = ["src/<pkg>", "README.md", "LICENSE", "pyproject.toml"]
```

```python
# src/<pkg>/_cache.py
MONOREPO_URL = "https://github.com/<org>/<pkg>.git"
CACHE_ROOT = Path.home() / ".scitex" / "<pkg-short>" / "cache"

def ensure_cache(branch="main", force_refresh=False):
    if not (CACHE_ROOT / ".git").is_dir() or force_refresh:
        subprocess.run(["git", "clone", "--depth", "1", "--branch", branch,
                        MONOREPO_URL, str(CACHE_ROOT)], check=True)
    else:
        subprocess.run(["git", "-C", str(CACHE_ROOT), "pull",
                        "--ff-only", "--depth", "1"])
    return CACHE_ROOT
```

When to use:
- Wheel size approaching or exceeding 1 MB and most users won't need the bulk.
- Content that updates more frequently than the package release cadence.
- Symlinks / OS-specific binaries that `hatchling` won't ship cleanly anyway.

When NOT to use:
- Anything imported directly by `src/` Python code (must be in the wheel).
- Small (<100 KB) static data — just include it in the wheel.
- Content the package can't function without — air-gapped environments.

Verify the wheel after building:

```bash
python -m build
python -m zipfile -l dist/<pkg>-<ver>-py3-none-any.whl | head -20
ls -la dist/                         # wheel should be <500 KB for cloner-style packages
```
