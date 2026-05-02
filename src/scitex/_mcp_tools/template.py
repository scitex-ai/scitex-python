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
        """Bootstrap a new SciTeX project by cloning a registered template repo (research-project, pip-package, manuscript, etc.) and seeding it with the chosen name — optionally at a specific branch/tag, with configurable git wiring (`child` submodule / `squash` flatten / `fork` new repo / `none`). Drop-in replacement for `git clone` + `cp -r` + hand-rewriting names in every template file + `git init`. Use when the user asks to "start a new SciTeX project", "clone the research template", "scaffold a paper repo", "initialize a new package from template", or is setting up fresh work."""
        from scitex_dev._mcp import async_wrap_as_mcp

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
        """Enumerate the git wiring options `template_clone_template` accepts — `child` (submodule), `squash` (flatten history), `fork` (new repo with detached history), `none` (no git). Use when the user asks "how do I wire git for the new project?", "what git options does the template support?", or is deciding between submodule vs standalone."""
        from scitex_dev._mcp import async_wrap_as_mcp

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
        """Return a boilerplate code template for a SciTeX script/module — core patterns (`session`, `io`, `config`) or per-module usage examples (`plt`, `stats`, `scholar`, `audio`, `capture`, `diagram`, `writer`, …), or `'all'` for every template concatenated. Drop-in replacement for copy-pasting from an old script, hand-writing `stx.session.start()` boilerplate, or re-reading SKILL.md just to recall idiomatic structure. Use when the user asks "scaffold a scitex script", "give me a stats experiment template", "how do I start a scitex session?", or is beginning a new `.py` and wants the standard structure. Optional `filepath` / `docstring` personalize the header."""
        from scitex_dev._mcp import async_wrap_as_mcp

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
        """Return the catalog of every code template `template_get_code_template` can serve — core (`session`, `io`, `config`) plus per-module usage templates. Use when the user asks "what templates are available?", "which modules have boilerplate?", or before picking a `template_id` to fetch."""
        from scitex_dev._mcp import async_wrap_as_mcp

        from scitex.template._mcp.handlers import list_code_templates_handler

        return await async_wrap_as_mcp(
            list_code_templates_handler,
            idempotent=True,
        )


# EOF
