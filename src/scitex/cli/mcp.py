#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/cli/mcp.py
"""
SciTeX MCP CLI - Model Context Protocol server management commands.

Commands:
- scitex mcp list       List all available MCP tools
- scitex mcp doctor     Check MCP server health and configuration
- scitex mcp serve      Start the unified MCP server
"""

import click


@click.group(invoke_without_command=True)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.pass_context
def mcp(ctx, help_recursive):
    """MCP (Model Context Protocol) server management."""  # noqa: D301
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _extract_return_keys(description: str) -> list:
    """Extract return dict keys from docstring Returns section."""
    import re

    if not description or "Returns" not in description:
        return []
    match = re.search(
        r"Returns\s*[-]+\s*\w+\s*(.+?)(?:Raises|Examples|Notes|\Z)",
        description,
        re.DOTALL,
    )
    if not match:
        return []
    return re.findall(r"'([a-z_]+)'", match.group(1))


def _format_signature(tool_obj, multiline: bool = False, indent: str = "  ") -> str:
    """Format tool as Python-like function signature with return type."""
    params = []
    if hasattr(tool_obj, "parameters") and tool_obj.parameters:
        schema = tool_obj.parameters
        props = schema.get("properties", {})
        required = schema.get("required", [])
        for name, info in props.items():
            ptype = info.get("type", "any")
            default = info.get("default")
            if name in required:
                p = f"{click.style(name, fg='white', bold=True)}: {click.style(ptype, fg='cyan')}"
            elif default is not None:
                def_str = repr(default) if len(repr(default)) < 20 else "..."
                p = f"{click.style(name, fg='white', bold=True)}: {click.style(ptype, fg='cyan')} = {click.style(def_str, fg='yellow')}"
            else:
                p = f"{click.style(name, fg='white', bold=True)}: {click.style(ptype, fg='cyan')} = {click.style('None', fg='yellow')}"
            params.append(p)
    # All MCP tools return standardized Result envelope
    ret_type = (
        f" -> {click.style('Result', fg='magenta')}"
        f"{click.style('{success, data, error, next_steps}', fg='yellow')}"
    )
    name_s = click.style(tool_obj.name, fg="green", bold=True)
    if multiline and len(params) > 2:
        param_indent = indent + "    "
        params_str = ",\n".join(f"{param_indent}{p}" for p in params)
        return f"{indent}{name_s}(\n{params_str}\n{indent}){ret_type}"
    return f"{indent}{name_s}({', '.join(params)}){ret_type}"


def _estimate_tokens(text: str) -> int:
    """Estimate token count (rough: ~4 chars per token)."""
    return len(text) // 4 if text else 0


def _get_all_tools(mcp_server) -> dict:
    """Get ALL tools including mounted sub-servers (crossref, openalex)."""
    from scitex._mcp_tools._compat import get_tools_sync

    return get_tools_sync(mcp_server)


def _get_mcp_summary(mcp_server, all_tools: dict | None = None) -> dict:
    """Get MCP server summary statistics."""
    import json as json_mod

    if all_tools is None:
        all_tools = _get_all_tools(mcp_server)
    tools = list(all_tools.values())
    instructions = getattr(mcp_server, "instructions", "") or ""
    total_desc = sum(len(t.description or "") for t in tools)
    total_params = sum(
        (
            len(json_mod.dumps(t.parameters))
            if hasattr(t, "parameters") and t.parameters
            else 0
        )
        for t in tools
    )

    return {
        "name": getattr(mcp_server, "name", "unknown"),
        "tool_count": len(tools),
        "instructions_tokens": _estimate_tokens(instructions),
        "descriptions_tokens": _estimate_tokens("x" * total_desc),
        "schemas_tokens": _estimate_tokens("x" * total_params),
        "total_context_tokens": (
            _estimate_tokens(instructions)
            + _estimate_tokens("x" * total_desc)
            + _estimate_tokens("x" * total_params)
        ),
    }


@mcp.command("list-tools")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v, -vv, -vvv.")
@click.option("-c", "--compact", is_flag=True, help="Compact signatures (single line)")
@click.option(
    "--module",
    "-m",
    type=str,
    default=None,
    help="Filter by module (audio, canvas, capture, dataset, diagram, plt, scholar, stats, template, ui, writer)",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--summary", "show_summary", is_flag=True, help="Show context summary")
def list_tools(
    verbose: int, compact: bool, module: str, as_json: bool, show_summary: bool
):
    """List all available MCP tools.

    Verbosity: (none) names, -v signatures, -vv +description, -vvv full.
    Signatures are expanded by default; use -c/--compact for single line.
    """  # noqa: D301
    import logging
    import warnings

    # Suppress DeprecationWarnings from third-party libraries (httplib2, etc.)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    # Suppress INFO messages from env loader during import
    logging.getLogger("scitex._env_loader").setLevel(logging.WARNING)
    try:
        from scitex.mcp_server import FASTMCP_AVAILABLE
        from scitex.mcp_server import mcp as mcp_server
    except ImportError:
        click.secho("ERROR: Could not import MCP server", fg="red", err=True)
        raise SystemExit(1) from None

    if not FASTMCP_AVAILABLE:
        click.secho(
            "ERROR: FastMCP not installed. Run: pip install fastmcp", fg="red", err=True
        )
        raise SystemExit(1)

    if mcp_server is None:
        click.secho("ERROR: MCP server not initialized", fg="red", err=True)
        raise SystemExit(1)

    # Get ALL tools (including mounted sub-servers like crossref, openalex)
    all_tools = _get_all_tools(mcp_server)

    # Group by module
    modules = {}
    for tool_name in sorted(all_tools.keys()):
        prefix = tool_name.split("_")[0]
        if prefix not in modules:
            modules[prefix] = []
        modules[prefix].append(tool_name)

    # Filter by module if specified
    if module:
        module = module.lower()
        if module not in modules:
            click.secho(f"ERROR: Unknown module '{module}'", fg="red", err=True)
            click.echo(f"Available modules: {', '.join(sorted(modules.keys()))}")
            raise SystemExit(1)
        modules = {module: modules[module]}

    summary = _get_mcp_summary(mcp_server, all_tools)

    if as_json:
        import json

        from scitex_dev.types import RESULT_SCHEMA

        output = {
            "result_envelope": RESULT_SCHEMA,
            "summary": summary,
            "total": sum(len(t) for t in modules.values()),
            "modules": {},
        }
        for mod, tool_list in modules.items():
            output["modules"][mod] = {
                "count": len(tool_list),
                "tools": [],
            }
            for tool_name in tool_list:
                tool_obj = all_tools.get(tool_name)
                schema = tool_obj.parameters if hasattr(tool_obj, "parameters") else {}
                output["modules"][mod]["tools"].append(
                    {
                        "name": tool_name,
                        "signature": (
                            _format_signature(tool_obj) if tool_obj else tool_name
                        ),
                        "description": tool_obj.description if tool_obj else "",
                        "parameters": schema,
                    }
                )
        click.echo(json.dumps(output, indent=2))
    else:
        total = sum(len(t) for t in modules.values())
        click.secho(f"SciTeX MCP: {summary['name']}", fg="cyan", bold=True)
        click.echo(f"Tools: {total} ({len(modules)} modules)")
        click.echo(
            f"Returns: {click.style('Result', fg='magenta')}"
            f"{click.style('{success, data, error, error_code, context, next_steps}', fg='yellow')}"
        )
        if show_summary:
            click.echo(f"Context: ~{summary['total_context_tokens']:,} tokens")
            click.echo(f"  Instructions: ~{summary['instructions_tokens']:,} tokens")
            click.echo(f"  Descriptions: ~{summary['descriptions_tokens']:,} tokens")
            click.echo(f"  Schemas: ~{summary['schemas_tokens']:,} tokens")
        click.echo()

        for mod, tool_list in sorted(modules.items()):
            click.secho(f"{mod}: {len(tool_list)} tools", fg="green", bold=True)
            for tool_name in tool_list:
                tool_obj = all_tools.get(tool_name)

                if verbose == 0:
                    # Names only
                    click.echo(f"  {tool_name}")
                elif verbose == 1:
                    # Full signature
                    sig = (
                        _format_signature(tool_obj, multiline=not compact)
                        if tool_obj
                        else f"  {tool_name}"
                    )
                    click.echo(sig)
                elif verbose == 2:
                    # Signature + one-line description
                    sig = (
                        _format_signature(tool_obj, multiline=not compact)
                        if tool_obj
                        else f"  {tool_name}"
                    )
                    click.echo(sig)
                    if tool_obj and tool_obj.description:
                        desc = tool_obj.description.split("\n")[0].strip()
                        click.echo(f"    {desc}")
                    click.echo()
                else:
                    # Signature + full description
                    sig = (
                        _format_signature(tool_obj, multiline=not compact)
                        if tool_obj
                        else f"  {tool_name}"
                    )
                    click.echo(sig)
                    if tool_obj and tool_obj.description:
                        for line in tool_obj.description.strip().split("\n"):
                            click.echo(f"    {line}")
                    click.echo()
            click.echo()


@mcp.command("doctor")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed diagnostics")
def doctor(verbose: bool):
    """Check MCP server health and configuration."""
    issues = []
    warnings = []

    click.secho("SciTeX MCP Doctor", fg="cyan", bold=True)
    click.echo()

    # Check 1: FastMCP installation
    click.echo("Checking FastMCP installation... ", nl=False)
    try:
        from fastmcp import FastMCP  # noqa: F401

        click.secho("OK", fg="green")
        if verbose:
            import fastmcp

            click.echo(f"  Version: {getattr(fastmcp, '__version__', 'unknown')}")
    except ImportError:
        click.secho("FAIL", fg="red")
        issues.append("FastMCP not installed. Run: pip install fastmcp")

    # Check 2: MCP server import
    click.echo("Checking MCP server module... ", nl=False)
    try:
        from scitex.mcp_server import FASTMCP_AVAILABLE
        from scitex.mcp_server import mcp as mcp_server

        if FASTMCP_AVAILABLE and mcp_server:
            click.secho("OK", fg="green")
        else:
            click.secho("WARN", fg="yellow")
            warnings.append("MCP server initialized but FastMCP not available")
    except ImportError as e:
        click.secho("FAIL", fg="red")
        issues.append(f"Could not import MCP server: {e}")

    # Check 3: _mcp_tools subpackage
    click.echo("Checking _mcp_tools subpackage... ", nl=False)
    try:
        from scitex._mcp_tools import register_all_tools  # noqa: F401

        click.secho("OK", fg="green")
    except ImportError as e:
        click.secho("FAIL", fg="red")
        issues.append(f"Could not import _mcp_tools: {e}")

    # Check 4: Individual module imports
    modules = [
        "audio",
        "canvas",
        "capture",
        "diagram",
        "plt",
        "scholar",
        "stats",
        "template",
        "ui",
        "writer",
    ]

    click.echo("Checking module registrations... ", nl=False)
    failed_modules = []
    for mod in modules:
        try:
            exec(f"from scitex._mcp_tools.{mod} import register_{mod}_tools")
        except ImportError as e:
            failed_modules.append((mod, str(e)))

    if failed_modules:
        click.secho(f"FAIL ({len(failed_modules)} modules)", fg="red")
        for mod, err in failed_modules:
            issues.append(f"Module {mod}: {err}")
    else:
        click.secho("OK", fg="green")

    # Check 5: Tool count (including mounted sub-servers)
    click.echo("Checking tool registration... ", nl=False)
    try:
        from scitex.mcp_server import mcp as mcp_server

        if mcp_server:
            all_tools = _get_all_tools(mcp_server)
            n = len(all_tools)
            if n >= 80:
                click.secho(f"OK ({n} tools)", fg="green")
            else:
                click.secho(f"WARN ({n} tools, expected 80+)", fg="yellow")
                warnings.append(f"Only {n} tools registered, expected 80+")
        else:
            click.secho("SKIP", fg="yellow")
    except Exception as e:
        click.secho("FAIL", fg="red")
        issues.append(f"Tool registration check failed: {e}")

    # Check 6: Handler imports (verbose only)
    if verbose:
        click.echo()
        click.secho("Handler Import Checks:", bold=True)
        handler_modules = [
            ("scitex.audio._mcp.handlers", "speak_handler"),
            ("scitex.capture._mcp.handlers", "capture_screenshot_handler"),
            ("scitex.scholar._mcp.handlers", "search_papers_handler"),
            ("scitex.stats._mcp.handlers", "run_test_handler"),
            ("scitex.plt._mcp._handlers_figure", "create_figure_handler"),
            ("scitex.canvas._mcp.handlers", "create_canvas_handler"),
            ("scitex.diagram._mcp.handlers", "create_diagram_handler"),
            ("scitex.template._mcp.handlers", "list_templates_handler"),
            ("scitex.ui._mcp.handlers", "notify_handler"),
            ("scitex.writer._mcp.handlers", "compile_manuscript_handler"),
        ]

        for mod_path, handler_name in handler_modules:
            click.echo(f"  {mod_path}... ", nl=False)
            try:
                mod = __import__(mod_path, fromlist=[handler_name])
                if hasattr(mod, handler_name):
                    click.secho("OK", fg="green")
                else:
                    click.secho(f"WARN (missing {handler_name})", fg="yellow")
            except ImportError as e:
                click.secho(f"FAIL ({e})", fg="red")

    # Summary
    click.echo()
    if issues:
        click.secho(f"Issues Found: {len(issues)}", fg="red", bold=True)
        for issue in issues:
            click.echo(f"  ✗ {issue}")
    if warnings:
        click.secho(f"Warnings: {len(warnings)}", fg="yellow", bold=True)
        for warning in warnings:
            click.echo(f"  ⚠ {warning}")
    if not issues and not warnings:
        click.secho("All checks passed!", fg="green", bold=True)

    raise SystemExit(1 if issues else 0)


def _print_help_recursive(ctx):
    """Print help for mcp and all its subcommands."""
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(mcp, info_name="mcp", parent=fake_parent)

    click.secho("━━━ scitex mcp ━━━", fg="cyan", bold=True)
    click.echo(mcp.get_help(parent_ctx))

    for name in sorted(mcp.list_commands(ctx) or []):
        cmd = mcp.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex mcp {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@mcp.command("start")
@click.option(
    "--transport",
    "-t",
    type=click.Choice(["stdio", "sse", "http"]),
    default="stdio",
    help="Transport type (default: stdio)",
)
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
@click.option(
    "--port", "-p", default=8085, type=int, help="Port to bind (default: 8085)"
)
def start(transport: str, host: str, port: int):
    """Start the unified MCP server."""
    try:
        from scitex.mcp_server import run_server
    except ImportError:
        click.secho("ERROR: Could not import MCP server", fg="red", err=True)
        click.echo("Run: pip install fastmcp")
        raise SystemExit(1) from None

    run_server(transport=transport, host=host, port=port)


@mcp.command("installation")
def installation():
    """Show Claude Desktop configuration for SciTeX MCP server."""
    import shutil
    import sys

    from scitex import __version__

    click.secho(f"SciTeX MCP Server v{__version__}", fg="cyan", bold=True)
    click.echo()

    # Get actual path
    scitex_path = shutil.which("scitex")
    python_path = sys.executable

    if scitex_path:
        click.echo(f"Your installation path: {scitex_path}")
        click.echo(f"Your Python path: {python_path}")
    click.echo()

    click.secho("Claude Desktop Configuration:", fg="green", bold=True)
    click.echo(
        "Add to ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)"
    )
    click.echo("or %APPDATA%\\Claude\\claude_desktop_config.json (Windows):")
    click.echo()

    config = f""""scitex": {{
  "command": "{scitex_path or "/path/to/.venv/bin/scitex"}",
  "args": ["mcp", "start"]
}}"""
    click.secho(config, fg="yellow")


# EOF
