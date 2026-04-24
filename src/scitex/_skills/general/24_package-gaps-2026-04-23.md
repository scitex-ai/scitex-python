# Package-level gaps (2026-04-23)

*Sibling of `23_remediation-log.md` — engineering debt distinct from skill-documentation issues.*


*Engineering debt distinct from skill-documentation issues — track here until each package closes its row.*

### Scope of this sweep
- Missing `examples/` directory (or empty/stub)
- Missing `tests/test_examples.py`
- Empty or stub `__init__.py`
- Placeholder / thin README

Note: `singularity-template` not present locally (skipped). README size thresholds: FULL ≥ 2000 B, THIN 500–1999 B, PLACEHOLDER < 500 B. `__init__.py`: FULL ≥ 200 B, STUB < 200 B. TODO strings in socialia/scitex-orochi READMEs are content (not template placeholders) — treated as FULL.

### scitex-io
- examples/ — PRESENT (5 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (3796 B)
- README.md — FULL (12982 B)

### scitex-stats
- examples/ — PRESENT (3 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (4315 B)
- README.md — FULL (11832 B)

### scitex-clew
- examples/ — PRESENT (3 .py)
- tests/test_examples.py — PRESENT (test__examples.py)
- __init__.py — FULL (10197 B)
- README.md — FULL (11181 B)

### scitex-cloud
- examples/ — PRESENT (2 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (2333 B)
- README.md — FULL (15207 B)

### figrecipe
- examples/ — PRESENT (29 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (3972 B)
- README.md — FULL (14236 B)

### openalex-local
- examples/ — PRESENT (9 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (1121 B)
- README.md — FULL (9217 B)

### crossref-local
- examples/ — PRESENT (7 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (4811 B)
- README.md — FULL (10178 B)

### scitex-writer
- examples/ — PRESENT (1 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (3490 B)
- README.md — FULL (18425 B)

### scitex-linter
- examples/ — PRESENT (2 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (856 B)
- README.md — FULL (15073 B)

### scitex-dataset
- examples/ — PRESENT (3 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (1589 B)
- README.md — FULL (7362 B)

### socialia
- examples/ — PRESENT (6 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (785 B)
- README.md — FULL (10071 B)

### automated-research-demo
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — EMPTY (no src module)
- README.md — FULL (2969 B)

### scitex-research-template
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — EMPTY (no src module)
- README.md — FULL (18573 B)

### pip-project-template
- examples/ — PRESENT (0 .py, 2 files)
- tests/test_examples.py — MISSING
- __init__.py — STUB (189 B)
- README.md — FULL (12088 B)

### scitex-container
- examples/ — PRESENT (2 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (325 B)
- README.md — FULL (7925 B)

### scitex-tunnel
- examples/ — PRESENT (0 .py, 4 files)
- tests/test_examples.py — MISSING
- __init__.py — FULL (4107 B)
- README.md — FULL (13682 B)

### scitex-ui
- examples/ — PRESENT (2 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (1676 B)
- README.md — FULL (7845 B)

### scitex-app
- examples/ — PRESENT (2 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (2182 B)
- README.md — FULL (9391 B)

### scitex-audio
- examples/ — PRESENT (3 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (5650 B)
- README.md — FULL (12846 B)

### scitex-parallel
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — STUB (195 B)
- README.md — PLACEHOLDER (272 B)

### scitex-types
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (338 B)
- README.md — THIN (567 B)

### scitex-path
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (1189 B)
- README.md — THIN (1722 B)

### scitex-repro
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (1437 B)
- README.md — PLACEHOLDER (125 B)

### scitex-compat
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (2542 B)
- README.md — PLACEHOLDER (323 B)

### scitex-etc
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (325 B)
- README.md — PLACEHOLDER (292 B)

### scitex-gists
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (363 B)
- README.md — PLACEHOLDER (365 B)

### scitex-audit
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (421 B)
- README.md — THIN (623 B)

### scitex-core
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (1025 B)
- README.md — FULL (3421 B)

### scitex-db
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (1274 B)
- README.md — FULL (3266 B)

### scitex-scholar
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (1710 B)
- README.md — FULL (6951 B)

### scitex-dev
- examples/ — PRESENT (3 .py)
- tests/test_examples.py — MISSING
- __init__.py — FULL (5376 B)
- README.md — FULL (8168 B)

### scitex-agent-container
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (1653 B)
- README.md — FULL (15016 B)

### scitex-orochi
- examples/ — PRESENT (0 .py, 1 file)
- tests/test_examples.py — MISSING
- __init__.py — FULL (373 B)
- README.md — FULL (9363 B)

### scitex-str
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (2500 B)
- README.md — FULL (2967 B)

### scitex-logging
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (5495 B)
- README.md — THIN (776 B)

### scitex-dict
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (451 B)
- README.md — THIN (907 B)

### scitex-browser
- examples/ — MISSING
- tests/test_examples.py — MISSING
- __init__.py — FULL (3150 B)
- README.md — THIN (1025 B)

### scitex-python (umbrella)
- examples/ — PRESENT (512 .py; 360 small <200 B — many are module-level stubs but examples/ itself is dense)
- tests/test_examples.py — PARTIAL (per-module test__examples.py files exist under tests/scitex/*/, no single top-level test_examples.py)
- __init__.py — FULL (12219 B)
- README.md — FULL (18605 B)

## Aggregate
- Packages missing examples/: 19
- Packages missing tests/test_examples.py: 36 (only scitex-clew has it; scitex-python has partial per-module coverage)
- Packages with stub/empty __init__.py: 3 (pip-project-template STUB; automated-research-demo & scitex-research-template have no src module)
- Packages with placeholder/thin README: 10 (placeholder: scitex-parallel, scitex-repro, scitex-compat, scitex-etc, scitex-gists; thin: scitex-types, scitex-path, scitex-audit, scitex-logging, scitex-dict, scitex-browser)

### Priority order (packages with all 4 gaps first)

4-gap packages (examples MISSING + no test_examples + stub/empty init + placeholder/thin README):
1. scitex-parallel — MISSING examples, MISSING test_examples, STUB init (195 B), PLACEHOLDER README (272 B)

3-gap packages (examples MISSING + no test_examples + placeholder/thin README, init ok):
2. scitex-repro — PLACEHOLDER README (125 B)
3. scitex-compat — PLACEHOLDER README (323 B)
4. scitex-etc — PLACEHOLDER README (292 B)
5. scitex-gists — PLACEHOLDER README (365 B)
6. scitex-types — THIN README (567 B)
7. scitex-audit — THIN README (623 B)
8. scitex-path — THIN README (1722 B)
9. scitex-logging — THIN README (776 B)
10. scitex-dict — THIN README (907 B)
11. scitex-browser — THIN README (1025 B)

2-gap packages (examples MISSING + no test_examples, init & README ok):
12. automated-research-demo (no src module; template-ish)
13. scitex-research-template (no src module; template-ish)
14. scitex-core
15. scitex-db
16. scitex-scholar
17. scitex-agent-container
18. scitex-str

1-gap packages (only missing tests/test_examples.py; everything else OK):
19. scitex-io, scitex-stats, scitex-cloud, figrecipe, openalex-local, crossref-local, scitex-writer, scitex-linter, scitex-dataset, socialia, pip-project-template, scitex-container, scitex-tunnel, scitex-ui, scitex-app, scitex-audio, scitex-dev, scitex-orochi, scitex-python

0-gap packages:
- scitex-clew (the only package that passes all four checks)
