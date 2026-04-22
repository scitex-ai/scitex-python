---
name: interface-mcp
description: MCP server standards for SciTeX packages — scitex-specific tool examples, skills integration, reference implementations.
---

> General patterns: see [programming-common/interface-mcp.md](../../commands/.claude/skills/programming-common/interface-mcp.md)

# MCP Server (SciTeX)

## Skills Integration (Standard for All SciTeX Packages)

Every SciTeX package MCP server must expose skills tools via `scitex_dev`:

```python
# Skills tools (standard, every package)
@mcp.tool()
def io_skills_list() -> dict:
    """List available skill pages."""
    from scitex_dev.skills import list_skills
    return list_skills(package="scitex-io")

@mcp.tool()
def io_skills_get(name: str = None) -> dict:
    """Get skill page content."""
    from scitex_dev.skills import get_skill
    return get_skill(package="scitex-io", name=name)
```

## Reference Implementation

- `~/proj/scitex-audio` — cleanest MCP implementation in the ecosystem
- Lessons learned: `~/proj/scitex-audio/GITIGNORED/LESSONS.md`

## SciTeX Tool Naming Examples

- `io_save`, `io_load`, `io_list_formats`, `io_skills_list`, `io_skills_get`
- `audio_speak`, `audio_list_voices`
- `stats_run_test`, `stats_recommend_tests`
- `plt_plot`, `plt_compose`, `plt_crop`
