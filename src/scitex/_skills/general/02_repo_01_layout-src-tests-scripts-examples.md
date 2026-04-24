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
