<!-- ---
!-- Timestamp: 2025-09-01 08:20:12
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/USER_PHILOSOPHY/04_ARCHITECTURE_PREDEFINED.md
!-- --- -->


# Agreed, Predefined Architecture

# External Data Storage

## Confiurations
-   `config/` - Configuration YAML files

## Project Data
-   `data/` - Project data files (datasets, sample data); gitignored

## Documentaitons
-   `docs/` - Documentations for users in general
-   `docs/to_claude` - Guidelines for Claude Code
-   `docs/from_user` - User messages
-   `docs/from_agents` - Agents can write any documents here

## Minimal Experiments
-   `.dev/` - Development sandbox for miniature tests; gitignored
-   But not included in final product
-   Need to incorporate successful code into `src` for permanent use

## Examples
-   `examples/` - For most important usages in the project
-   Use `ipynb` is a better practice for rendering in GitHub
-   But the user is not a notebook person but more of a person with `.py` scripts

## Makefile
-   install, test-changed, test-full, coverage-html, ci-container, ci-act, ci-local,
    lint, clean, build, upload-pypi-test, upload-pypi, release, and so on

## Project Management Derectory
-   `mgmt` for searchability
-   `mgmt/PROJECT_DESCRIPTION_v01.md`
-   `mgmt/ARCHITECTURE_v01.md`
-   `mgmt/BULLETIN_BOARD_v01.md`

## pyproject.toml
No need to conventional files such as `setup.py`, `requirements.txt`, `MANIFEST.in`

## Test code

**Test files for source code**

- For pip package:
    -   `tests/pip_package_name/test_public_function_name.py`
    -   `tests/pip_package_name/test__private_function_name.py`
    -   `tests/pip_package_name/test_PublicClassName.py`
    -   `tests/pip_package_name/test__PrivateClassName.py`

- For scientific projects:
    -   `tests/scripts/test_public_function_name.py`
    -   `tests/scripts/test__private_function_name.py`
    -   `tests/scripts/test_PublicClassName.py`
    -   `tests/scripts/test__PrivateClassName.py`

**Test files except for source code**

-   `tests/custom/`

**Scripts for running GitHub actions locally**

-   `tests/github_actions/`

**Test Results Summary**

-   `tests/reports/` - Natural location for test outputs

#+END_SRC

<!-- EOF -->
