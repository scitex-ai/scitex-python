<!-- ---
!-- Timestamp: 2025-09-01 08:14:57
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/USER_PHILOSOPHY/01_DEVELOPMENT_CYCLE.md
!-- --- -->

# Key Principles

-   Tests based on **specifications and acceptance criteria**, not just architecture
-   **Quality gates** beyond coverage (linting, type checking)
-   **Git strategy** with `--fixup` commits during red phase
-   **Code quality checks** before commits
-   **Documentation updates** when APIs change


# Development Cycle Steps

01. Accomplish tree-like architecture agreement with behavioral specifications
02. Plan modular cycles with descriptive phase allocation (e.g., Phase 01: Config Development)
03. Create feature branch from develop branch
04. Implement red tests based on **specifications and acceptance criteria** for the scope
05. Verify tests fail for the right reasons (Red Testing)
06. Implement source code to satisfy specifications (understanding intent)
07. Tests with pytest-testmon (only for affected tests from source code change)
08. Run ruff check/format to ensure code quality before commit
09. Git commit with appropriate strategy (`--fixup` while red, logical when green)
10. Repeat 04 -> 09 until quality gates passed:
    -   All tests passing
    -   Coverage meets threshold (not always 100%)
    -   No linting errors
    -   Type checking passes
11. Squash git commits if cluttered (`rebase -i --autosquash`)
12. Run full test suite and quality validation
13. Update documentation if APIs changed
14. Merge back to develop branch
15. Repeat 03 -> 14 until project completion


# Quality Gates

-   All tests passing
-   Coverage meets threshold
-   No linting errors (ruff)
-   Type checking passes (mypy)
-   Documentation updated for API changes

<!-- EOF -->
