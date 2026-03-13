#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/template.py
"""Template module tools for FastMCP unified server."""

from typing import Optional


def register_template_tools(mcp) -> None:
    """Register template tools with FastMCP server."""

    @mcp.tool()
    async def template_clone_template(
        template_id: str,
        project_name: str,
        target_dir: Optional[str] = None,
        git_strategy: str = "child",
        branch: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> str:
        """Create a new project by cloning a template."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.template._mcp.handlers import clone_template_handler

        return await async_wrap_as_mcp(
            clone_template_handler,
            side_effects=["file_create: new project directory from template"],
            template_id=template_id,
            project_name=project_name,
            target_dir=target_dir,
            git_strategy=git_strategy,
            branch=branch,
            tag=tag,
        )

    @mcp.tool()
    async def template_list_git_strategies() -> str:
        """List available git initialization strategies for template cloning."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.template._mcp.handlers import list_git_strategies_handler

        return await async_wrap_as_mcp(
            list_git_strategies_handler,
            idempotent=True,
        )

    @mcp.tool()
    async def template_get_code_template(
        template_id: str,
        filepath: Optional[str] = None,
        docstring: Optional[str] = None,
    ) -> str:
        """Get a code template for scripts and modules. Core: session, io, config. Module usage: plt, stats, scholar, audio, capture, diagram, canvas, writer. Use 'all' for all templates combined."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.template._mcp.handlers import get_code_template_handler

        return await async_wrap_as_mcp(
            get_code_template_handler,
            idempotent=True,
            template_id=template_id,
            filepath=filepath,
            docstring=docstring,
        )

    @mcp.tool()
    async def template_list_code_templates() -> str:
        """List all available code templates for scripts and modules."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.template._mcp.handlers import list_code_templates_handler

        return await async_wrap_as_mcp(
            list_code_templates_handler,
            idempotent=True,
        )


# EOF
