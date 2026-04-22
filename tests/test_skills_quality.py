"""Enforces SciTeX skills quality checklist §1–§4.
Canonical: src/scitex/_skills/general/21_scitex-package-quality-checklist.md
"""
from pathlib import Path
from scitex_dev._skills_quality_pytest import make_skill_quality_tests

test_skills_quality = make_skill_quality_tests(
    package_root=Path(__file__).resolve().parents[1]
)
