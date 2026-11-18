#!/usr/bin/env python3
"""Shared helpers for the ``scitex mcp list-tools`` / ``doctor`` commands."""

import click


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
    from scitex._mcp import get_tools_sync

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


# EOF
