---
name: four-interfaces
description: Every SciTeX package exposes four interfaces — Python API, CLI, MCP, Skills. Overview and links to detailed sub-skills.
---

# Four Interfaces (Required per Package)

Every SciTeX package exposes four interfaces. No logic duplication — all delegate to Python API.

| Interface | Audience | Delegates to |
|-----------|----------|-------------|
| **Python API** | Scripts, notebooks | — (source of truth) |
| **CLI** | Terminal, shell | Python API |
| **MCP Server** | AI agents (actions) | CLI commands |
| **Skills** | AI agents (discovery) | Static markdown |
| **HTTP API** | Web clients (optional) | Python API |

## Sub-skills

* [interface-python-api.md](interface-python-api.md) — Minimal API design, no logic duplication
* [interface-cli.md](interface-cli.md) — Required sub-commands, flags, consistency rules
* [interface-mcp.md](interface-mcp.md) — fastmcp patterns, reproducibility, standard commands
* [interface-skills.md](interface-skills.md) — `_skills/` layout, SKILL.md format, registration, export
* [interface-http-api.md](interface-http-api.md) — Optional FastAPI, delegation rules
