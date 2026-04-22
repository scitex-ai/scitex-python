<!-- ---
!-- Timestamp: 2026-04-23 07:54:35
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/_skills/general/src-vs-tests-vs-scripts.md
!-- --- -->

## Code Organization
- src is mainly for python packages
  - Minimal dependency for other scitex packages
- e.g., <scitex-package>/src/<scitex_package>/path/to/file.py
- scripts is mainly for project maintenance and research experiments
  - e.g., <scitex-package>/scripts/... <FIXME>
- tests is for tests
  - e.g., <scitex-package>/tests/<scitex_package>/path/to/test_file.py
- examples
  - Use scitex packages, especially for scitex.{io,plt,session}
  - Always ensure to have numbered prefix
    - e.g., <scitex-package>/examples/01_<descriptive-filename>.py
    - e.g., <scitex-package>/examples/01_<descriptive-filename>_out/

<!-- EOF -->