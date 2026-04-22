---
name: readme-organization
description: Standard README.md template structure for SciTeX packages — sections, badges, collapsible blocks, Four Freedoms footer.
---

> General patterns: see [programming-common/readme-organization.md](../../commands/.claude/skills/programming-common/readme-organization.md)

# README Organization (SciTeX)

## Standard Section Order

Every SciTeX package README follows this structure:

```markdown
# package-name

[Centered SciTeX logo]

**One-line tagline**

[Badges: PyPI, Docs, Tests, License — centered]

[Quick links: Documentation · pip install — centered]

---

## Problem
## Solution
<details><summary>Supported Formats / Feature Table</summary></details>
## Installation
## Quickstart
## Four Interfaces
## Lint Rules (if applicable)
## Part of SciTeX
[Four Freedoms blockquote]

---

[Centered SciTeX icon footer]

```

## Badge Row (SciTeX Style)

```markdown
<p align="center">
  <a href="https://badge.fury.io/py/PACKAGE"><img src="https://badge.fury.io/py/PACKAGE.svg" alt="PyPI version"></a>
  <a href="https://PACKAGE.readthedocs.io/"><img src="https://readthedocs.org/projects/PACKAGE/badge/?version=latest" alt="Documentation"></a>
  <a href="https://github.com/ywatanabe1989/PACKAGE/actions/workflows/ci.yml"><img src="https://github.com/ywatanabe1989/PACKAGE/actions/workflows/ci.yml/badge.svg" alt="Tests"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
</p>
```

## Four Interfaces (Collapsible)

Each interface in its own `<details>` block:

```markdown
<details>
<summary><strong>Python API</strong></summary>
[Code examples]
</details>

<details>
<summary><strong>CLI Commands</strong></summary>
[Command examples]
</details>

<details>
<summary><strong>MCP Server — for AI Agents</strong></summary>
[Tool table + start command]
</details>

<details>
<summary><strong>Skills — for AI Agent Discovery</strong></summary>
[Skill table + CLI commands]
</details>
```

## Four Freedoms Footer

```markdown
## Part of SciTeX

PACKAGE is part of [**SciTeX**](https://scitex.ai).

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

```

## SciTeX-Specific Rules

- **No `ywatanabe@scitex.ai`** in footer — community project
- **Use `import scitex`** in examples, not `import scitex as stx`
- **Verify all format/feature claims** against actual `_builtin_handlers.py` or source code
- **Match quickstart.rst** — README Quickstart and Sphinx quickstart should show the same examples
