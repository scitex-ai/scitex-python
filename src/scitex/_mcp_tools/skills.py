#!/usr/bin/env python3
"""MCP tools for skills aggregation across the SciTeX ecosystem."""

from typing import Optional


def register_skills_tools(mcp) -> None:
    """Register skills discovery MCP tools."""

    @mcp.tool()
    async def skills_list(package: Optional[str] = None) -> str:
        """List available skill pages across the SciTeX ecosystem.

        Args:
            package: Filter to a specific package (e.g. "scitex-stats").
                     None returns all packages.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp
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
        """Get a skill page content.

        Args:
            package: Package name (e.g. "scitex-stats").
            name: Reference name (e.g. "test-selection").
                  None returns the main SKILL.md.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp
        from scitex_dev.skills import get_skill

        return wrap_as_mcp(
            get_skill,
            idempotent=True,
            package=package,
            name=name,
        )
