#!/usr/bin/env python3
"""MCP tools for skills aggregation across the SciTeX ecosystem."""

from typing import Optional


def register_skills_tools(mcp) -> None:
    """Register skills discovery MCP tools."""

    @mcp.tool()
    async def skills_list(package: Optional[str] = None) -> str:
        """Enumerate every `SKILL.md` + sub-skill reference page the installed SciTeX ecosystem ships — core + per-package + per-topic leaves. Drop-in replacement for `find ~/.claude/skills -name SKILL.md` or manually walking `site-packages/*/scitex_*/_skills/`. Use when the user asks "what SciTeX skills do I have?", "list skill pages for scitex-stats", "show everything under scitex-writer", or is orienting before `skills_get`.

        Args:
            package: Filter to a specific package (e.g. "scitex-stats").
                     None returns all packages.
        """
        from scitex_dev._mcp import wrap_as_mcp
        from scitex_dev.skills import list_skills

        return wrap_as_mcp(
            list_skills,
            idempotent=True,
            package=package,
        )

    @mcp.tool()
    async def skills_get(
        package: str,
        name: Optional[str] = None,
    ) -> str:
        """Read the markdown content of a specific SciTeX skill page (main `SKILL.md` or a named reference leaf). Drop-in replacement for hand-walking `~/.claude/skills/scitex/<pkg>/<name>.md`. Use when the user asks "show me the scitex-stats skill", "get the figrecipe plot-types reference", "read the skill for X", or when an agent needs deep guidance beyond what the auto-loaded frontmatter description conveyed.

        Args:
            package: Package name (e.g. "scitex-stats").
            name: Reference name (e.g. "test-selection").
                  None returns the main SKILL.md.
        """
        from scitex_dev._mcp import wrap_as_mcp
        from scitex_dev.skills import get_skill

        return wrap_as_mcp(
            get_skill,
            idempotent=True,
            package=package,
            name=name,
        )
