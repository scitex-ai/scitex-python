#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/_umbrella_tools.py
"""Umbrella compatibility MCP adapters over explicitly owned operations.

These retain historical tool IDs while delegating to leaf or umbrella helpers.
Registration requires both the umbrella adapter preference and its delegated
owner preference; no handler executes during discovery.

Namespaces here: browser, capture, docs, skills, usage, template, tunnel.
The larger ``introspect_*`` and ``notification_*`` families live in sibling
modules to keep each file focused.
"""

from __future__ import annotations

from typing import Optional

from ._introspect_tools import register_introspect_tools
from ._notification_tools import register_notification_tools

__all__ = ["register_umbrella_tools"]


def register_umbrella_tools(mcp, *, package_policy=None) -> None:
    """Admit existing compatibility tools without duplicating leaf operations."""
    from ._exposure import is_exposed, load_package_policy

    package_policy = load_package_policy(package_policy)

    def owned_tool(owner, namespace):
        def register(function):
            if is_exposed("scitex", "scitex", package_policy) and is_exposed(
                owner, namespace, package_policy
            ):
                return mcp.tool()(function)
            return function
        return register

    # -- browser ---------------------------------------------------------
    @owned_tool("scitex-browser", "browser")
    async def browser_save_as_pdf(
        url: str,
        output_path: str,
        wait_seconds: float = 3,
        print_background: bool = True,
        format: str = "A4",
        margin: str = "10mm",
    ) -> str:
        """Render any URL to a print-style PDF via headless Chromium — full-page, JS-rendered, with configurable paper size + margins + background graphics. Drop-in replacement for Chrome's "Print -> Save as PDF" dialog, `wkhtmltopdf`, `weasyprint`, and `playwright.page.pdf()` boilerplate. Use when the user asks to "save this page as PDF", "archive this article", "generate a PDF from the dashboard", "download the rendered HTML report", or is capturing a JS-heavy page that static scrapers miss. `wait_seconds` gives JS time to finish rendering.

        Args:
            url: URL to save as PDF.
            output_path: Path to save the PDF file.
            wait_seconds: Extra seconds to wait after page load for JS rendering.
            print_background: Whether to print background graphics.
            format: Paper format (A4, Letter, etc.).
            margin: Page margins (e.g., 10mm, 1in).
        """
        from scitex_dev.ecosystem import async_wrap_as_mcp

        from scitex.browser.pdf._save_as_pdf import save_as_pdf_async

        return await async_wrap_as_mcp(
            save_as_pdf_async,
            side_effects=["file_create: PDF file"],
            url=url,
            output_path=output_path,
            wait_seconds=wait_seconds,
            print_background=print_background,
            format=format,
            margin_top=margin,
            margin_bottom=margin,
            margin_left=margin,
            margin_right=margin,
        )

    # -- capture ---------------------------------------------------------
    @owned_tool("scitex-capture", "capture")
    async def capture_screenshot(
        monitor_id: int = 0,
        all: bool = False,
        quality: int = 85,
        message: Optional[str] = None,
        return_base64: bool = False,
        url: Optional[str] = None,
        app: Optional[str] = None,
    ) -> str:
        """Take a JPEG screenshot of a chosen target — a specific monitor (`monitor_id=N`), every monitor at once (`all=True`), a live browser tab (`url=...`), or an X11 application window (`app='emacs'`). Drop-in replacement for `scrot`, `gnome-screenshot`, `maim`, `mss.mss().shot()`, and ad-hoc `playwright.screenshot()`. Use when the user asks to "take a screenshot", "capture my screen", "grab a picture of the browser", "screenshot that app window", "prove visually this is fixed", or is attaching UI evidence to a bug report / review. `return_base64=True` inlines instead of saving."""
        from scitex_dev.ecosystem import async_wrap_as_mcp

        from scitex.capture._mcp.handlers import capture_screenshot_handler

        return await async_wrap_as_mcp(
            capture_screenshot_handler,
            side_effects=["file_create: screenshot image file"],
            idempotent=True,
            monitor_id=monitor_id,
            all=all,
            quality=quality,
            message=message,
            return_base64=return_base64,
            url=url,
            app=app,
        )

    # -- docs (scitex-dev aggregation) -----------------------------------
    @owned_tool("scitex-dev", "docs")
    async def docs_list() -> str:
        """Enumerate every installed SciTeX package that ships bundled Sphinx docs — each entry includes version, manifest path, and docs URL. Use when the user asks "what SciTeX packages are installed?", "which ones have docs?", or before calling `docs_get` / `docs_search`."""
        from scitex_dev import get_docs
        from scitex_dev.ecosystem import wrap_as_mcp

        return wrap_as_mcp(get_docs, idempotent=True)

    @owned_tool("scitex-dev", "docs")
    async def docs_get(
        package: str,
        format: Optional[str] = None,
        page: Optional[str] = None,
    ) -> str:
        """Fetch a SciTeX package's bundled Sphinx docs — manifest (default), parsed JSON body, or a path to the built HTML. Use when the user asks "show scitex-writer docs", "open the manual for X", "get the Sphinx output for Y".

        Args:
            package: Package name (e.g. "scitex-writer").
            format: None for manifest, "json" for structured, "html" for path.
            page: Specific documentation page name.
        """
        from scitex_dev import get_docs
        from scitex_dev.ecosystem import wrap_as_mcp

        return wrap_as_mcp(
            get_docs, idempotent=True, package=package, format=format, page=page
        )

    @owned_tool("scitex-dev", "docs")
    async def docs_build(
        package: Optional[str] = None,
        formats: Optional[list[str]] = None,
    ) -> str:
        """Trigger `sphinx-build` on one or every installed SciTeX package, producing HTML/JSON under each package's `_docs/_build/`. Use when the user asks to "rebuild docs", "regenerate Sphinx HTML", or after editing docstrings / `.rst` source.

        Args:
            package: Package name. None = build all.
            formats: List of builders ("html", "json"). Default: ["html"].
        """
        from scitex_dev import build_docs
        from scitex_dev.ecosystem import wrap_as_mcp

        return wrap_as_mcp(
            build_docs,
            side_effects=["file_create: Sphinx HTML output in _build directory"],
            package=package,
            formats=formats,
        )

    @owned_tool("scitex-dev", "docs")
    async def docs_search(
        query: str,
        scope: str = "all",
        package: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Search installed documentation, Python APIs, CLI references and source-level MCP references. This searches source documentation, not the host's admitted runtime tool catalog. Use whenever the user asks to "search the ecosystem for X", "find anything about figures / stats / writing", "which module does Y?". Use `scope='api'|'cli'|'mcp'|'docs'` to narrow; `+required` / `-excluded` operators supported.

        Args:
            query: Search query string.
            scope: What to search: "all", "api", "cli", "mcp", or "docs".
            package: Limit search to a single package.
            max_results: Maximum number of results.
        """
        from scitex_dev import search
        from scitex_dev.ecosystem import wrap_as_mcp

        return wrap_as_mcp(
            search,
            idempotent=True,
            query=query,
            scope=scope,
            package=package,
            max_results=max_results,
        )

    # -- skills (scitex-dev aggregation) ---------------------------------
    @owned_tool("scitex-dev", "skills")
    async def skills_list(package: Optional[str] = None) -> str:
        """List enabled installed skill namespaces and pages with their owning distributions. Use when the user asks "what SciTeX skills do I have?", "list skill pages for scitex-stats", or is orienting before `skills_get`.

        Args:
            package: Filter to a specific package. None returns all packages.
        """
        from scitex_dev.ecosystem import list_skills, wrap_as_mcp

        return wrap_as_mcp(list_skills, idempotent=True, package=package)

    @owned_tool("scitex-dev", "skills")
    async def skills_get(
        package: str, name: Optional[str] = None, owner: Optional[str] = None
    ) -> str:
        """Read the markdown content of a specific SciTeX skill page (main `SKILL.md` or a named reference leaf). Use when the user asks "show me the scitex-stats skill", "get the figrecipe plot-types reference", "read the skill for X".

        Args:
            package: Registered namespace (e.g. "scitex-stats").
            owner: Listed distribution owner; never fall back to a different owner.
            name: Reference name (e.g. "test-selection"). None = main SKILL.md.
        """
        from scitex_dev.ecosystem import get_skill, wrap_as_mcp

        return wrap_as_mcp(
            get_skill, idempotent=True, package=package, name=name, owner=owner
        )

    # -- usage -----------------------------------------------------------
    @owned_tool("scitex", "usage")
    def usage_show(topic: str = "") -> str:
        """Return a runnable code example for a SciTeX topic (`plt`, `stats`, `session`, `io`, `scholar`, ...) — short, copy-pasteable snippets showing idiomatic usage. Use when the user asks "how do I use scitex.plt?", "show me a t-test example", "give me a session boilerplate"."""
        from scitex_dev.ecosystem import wrap_as_mcp

        from scitex.usage import show

        return wrap_as_mcp(show, idempotent=True, topic=topic or None)

    @owned_tool("scitex", "usage")
    def usage_list() -> str:
        """List every topic `usage_show` can serve (`plt`, `stats`, `session`, `io`, `scholar`, `audio`, `writer`, ...). Use when the user asks "what examples are available?", "which modules have usage snippets?"."""
        from scitex_dev.ecosystem import wrap_as_mcp

        from scitex.usage import topics

        return wrap_as_mcp(topics, idempotent=True)

    # -- template --------------------------------------------------------
    @owned_tool("scitex-template", "template")
    async def template_clone_template(
        template_id: str,
        project_name: str,
        target_dir: Optional[str] = None,
        git_strategy: str = "child",
        branch: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> str:
        """Bootstrap a new SciTeX project by cloning a registered template repo and seeding it with the chosen name — optionally at a branch/tag, with configurable git wiring (`child`/`squash`/`fork`/`none`). Use when the user asks to "start a new SciTeX project", "clone the research template", "scaffold a paper repo", "initialize a new package from template"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp

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

    @owned_tool("scitex-template", "template")
    async def template_list_git_strategies() -> str:
        """Enumerate the git wiring options `template_clone_template` accepts — `child` (submodule), `squash`, `fork`, `none`. Use when the user asks "how do I wire git for the new project?", "what git options does the template support?"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp

        from scitex.template._mcp.handlers import list_git_strategies_handler

        return await async_wrap_as_mcp(list_git_strategies_handler, idempotent=True)

    @owned_tool("scitex-template", "template")
    async def template_get_code_template(
        template_id: str,
        filepath: Optional[str] = None,
        docstring: Optional[str] = None,
    ) -> str:
        """Return a boilerplate code template for a SciTeX script/module — core patterns (`session`, `io`, `config`) or per-module usage examples, or `'all'`. Use when the user asks "scaffold a scitex script", "give me a stats experiment template", "how do I start a scitex session?"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp

        from scitex.template._mcp.handlers import get_code_template_handler

        return await async_wrap_as_mcp(
            get_code_template_handler,
            idempotent=True,
            template_id=template_id,
            filepath=filepath,
            docstring=docstring,
        )

    @owned_tool("scitex-template", "template")
    async def template_list_code_templates() -> str:
        """Return the catalog of every code template `template_get_code_template` can serve. Use when the user asks "what templates are available?", "which modules have boilerplate?"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp

        from scitex.template._mcp.handlers import list_code_templates_handler

        return await async_wrap_as_mcp(list_code_templates_handler, idempotent=True)

    # -- tunnel ----------------------------------------------------------
    @owned_tool("scitex-ssh", "tunnel")
    async def tunnel_setup(port: int, bastion_server: str, secret_key_path: str) -> str:
        """Install an `autossh`-backed systemd unit that opens a reverse SSH tunnel (local -> bastion:port) and auto-reconnects on drop. Use when the user asks to "set up a reverse tunnel", "expose this machine through a bastion", "open port X on the jump host", or mentions bastion, jump host, NAT traversal, HPC login node."""
        from scitex_dev.ecosystem import wrap_as_mcp

        from scitex.tunnel import setup

        return wrap_as_mcp(
            setup,
            side_effects=["systemd_service: creates autossh service"],
            port=port,
            bastion_server=bastion_server,
            secret_key_path=secret_key_path,
        )

    @owned_tool("scitex-ssh", "tunnel")
    async def tunnel_remove(port: int) -> str:
        """Tear down an autossh reverse-tunnel unit (stop + disable + rm unit + daemon-reload). Use when the user asks to "remove the tunnel", "delete reverse tunnel on port X", "stop autossh", "decommission this route"."""
        from scitex_dev.ecosystem import wrap_as_mcp

        from scitex.tunnel import remove

        return wrap_as_mcp(
            remove,
            side_effects=["systemd_service: stops and disables autossh service"],
            port=port,
        )

    @owned_tool("scitex-ssh", "tunnel")
    async def tunnel_status(port: int = 0) -> str:
        """Live state of autossh reverse-tunnel systemd units — active/inactive, PID, restart count, last journal lines. Use when the user asks "is my tunnel up?", "why can't I reach port 2222?", "list all reverse tunnels". `port=0` lists everything."""
        from scitex_dev.ecosystem import wrap_as_mcp

        from scitex.tunnel import status

        return wrap_as_mcp(status, idempotent=True, port=port if port else None)

    # -- larger families (separate modules) ------------------------------
    if is_exposed("scitex", "scitex", package_policy):
        if is_exposed("scitex-introspect", "introspect", package_policy):
            register_introspect_tools(mcp)
        if is_exposed("scitex-notification", "notification", package_policy):
            register_notification_tools(mcp)


# EOF
