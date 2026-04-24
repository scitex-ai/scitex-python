<!-- ---
!-- Timestamp: 2026-04-23 09:00:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/_skills/general/13_repo-layout-src-tests-scripts-examples.md
!-- --- -->

---
name: repo-layout-src-tests-scripts-examples
description: Layout boundaries between src/, tests/, scripts/, examples/, and references/ in every SciTeX package.
---

## Code Organization

#### src
- src is mainly for python packages
  - Minimal dependency for other scitex packages
- e.g., <scitex-package>/src/<scitex_package>/path/to/file.py

#### scripts
- scripts is mainly for project maintenance and research experiments
  - e.g., <scitex-package>/scripts/... <FIXME>

#### examples
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

#### tests
- Control by pyproject.toml
- Use pytest wisely
- For large tests, consider using computational remote hosts
  - e.g., <scitex-package>/tests/<scitex_package>/path/to/test_file.py

#### references
- External/upstream material kept verbatim for provenance and reproducibility
  - e.g., specs, third-party docs, benchmark datasets, paper PDFs
- Read-only — do NOT edit contents; only add/remove files
- Pin with explicit version/commit/DOI in filename or sidecar README
  - e.g., <scitex-package>/references/<source>_<version-or-sha>/
- Never imported from `src/`; consumed by tests, scripts, or examples as fixtures
- Large binaries → prefer Git LFS or fetch-on-demand script, not committed blobs
- Each subdir should have a one-line `README.md` stating source URL + retrieval date

<!-- EOF -->