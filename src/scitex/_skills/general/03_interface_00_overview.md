---
name: interfaces-overview
description: Every SciTeX package exposes five interfaces — Python API, CLI, MCP, Skills, and (optional) HTTP API. Overview and links to detailed sub-skills.
---

# Five Interfaces (Required per Package)

Every SciTeX package exposes up to five interfaces. No logic duplication — all delegate to the Python API (the single source of truth).

| # | Interface | Audience | Delegates to | Required |
|---|-----------|----------|--------------|----------|
| 1 | **Python API** | Scripts, notebooks | — (source of truth) | ✅ Required |
| 2 | **CLI** | Terminal, shell | Python API | Recommended when package has a user-facing surface; optional for pure library utilities |
| 3 | **MCP Server** | AI agents (actions) | CLI commands | Recommended when package has a user-facing surface; optional for pure library utilities |
| 4 | **Skills** | AI agents (discovery) | Static markdown | ✅ Required |
| 5 | **HTTP API** | Web clients | Python API | ⚪ Optional |

## Sub-skills

* [03_interface_01_python-api.md](03_interface_01_python-api.md) — Minimal API design, no logic duplication
* [03_interface_02_cli.md](03_interface_02_cli.md) — Required sub-commands, flags, consistency rules
* [03_interface_03_mcp.md](03_interface_03_mcp.md) — fastmcp patterns, reproducibility, standard commands
* [03_interface_04_skills.md](03_interface_04_skills.md) — `_skills/` layout, SKILL.md format, registration, export
* [03_interface_05_http-api.md](03_interface_05_http-api.md) — Optional FastAPI, delegation rules
