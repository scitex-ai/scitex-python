---
name: interfaces-overview
description: Every SciTeX package exposes five interfaces — Python API, CLI, MCP, Skills, and (optional) HTTP API. Overview and links to detailed sub-skills.
---

# Five Interfaces (Required per Package)

Every SciTeX package exposes up to five interfaces. No logic duplication — all delegate to the Python API (the single source of truth).

| # | Interface | Audience | Delegates to | Required |
|---|-----------|----------|--------------|----------|
| 1 | **Python API** | Scripts, notebooks | — (source of truth) | ✅ |
| 2 | **CLI** | Terminal, shell | Python API | ✅ |
| 3 | **MCP Server** | AI agents (actions) | CLI commands | ✅ |
| 4 | **Skills** | AI agents (discovery) | Static markdown | ✅ |
| 5 | **HTTP API** | Web clients | Python API | ⚪ Optional |

## Sub-skills

* [02_interface-python-api.md](02_interface-python-api.md) — Minimal API design, no logic duplication
* [03_interface-cli.md](03_interface-cli.md) — Required sub-commands, flags, consistency rules
* [04_interface-mcp.md](04_interface-mcp.md) — fastmcp patterns, reproducibility, standard commands
* [05_interface-skills.md](05_interface-skills.md) — `_skills/` layout, SKILL.md format, registration, export
* [06_interface-http-api.md](06_interface-http-api.md) — Optional FastAPI, delegation rules
