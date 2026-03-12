#!/usr/bin/env python3
"""
SciTeX CLI - Command-line interface for SciTeX platform

Provides unified interface for:
- Cloud operations (wraps tea for Gitea)
- Scholar operations (Django API)
- Code operations (Django API)
- Viz operations (Django API)
- Writer operations (Django API)
- Project operations (integrated workflows)
"""

import click

from .main import cli


def print_help_recursive(ctx, group: click.Group) -> None:
    """Print help for a group and all its subcommands.

    Args:
        ctx: The click context
        group: The click group to print help for
    """
    # Create a fake parent context to show correct command path in Usage
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(group, info_name=group.name, parent=fake_parent)

    click.secho(f"━━━ scitex {group.name} ━━━", fg="cyan", bold=True)
    click.echo(group.get_help(parent_ctx))

    for name in sorted(group.list_commands(ctx) or []):
        cmd = group.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex {group.name} {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))
            # Handle nested subgroups
            if isinstance(cmd, click.Group):
                for sub_name in sorted(cmd.list_commands(sub_ctx) or []):
                    sub_cmd = cmd.get_command(sub_ctx, sub_name)
                    if sub_cmd is None:
                        continue
                    click.echo()
                    click.secho(
                        f"━━━ scitex {group.name} {name} {sub_name} ━━━",
                        fg="cyan",
                        bold=True,
                    )
                    with click.Context(
                        sub_cmd, info_name=sub_name, parent=sub_ctx
                    ) as sub_sub_ctx:
                        click.echo(sub_cmd.get_help(sub_sub_ctx))


def format_python_signature(func, multiline: bool = True, indent: str = "  ") -> tuple:
    """Format Python function signature with colors matching mcp list-tools.

    Returns (name_colored, signature_colored)
    """
    import inspect

    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return click.style(func.__name__, fg="green", bold=True), ""

    params = []
    for name, param in sig.parameters.items():
        # Get type annotation
        if param.annotation != inspect.Parameter.empty:
            ann = param.annotation
            type_str = ann.__name__ if hasattr(ann, "__name__") else str(ann)
            type_str = type_str.replace("typing.", "")
        else:
            type_str = None

        # Get default value
        if param.default != inspect.Parameter.empty:
            default = param.default
            def_str = repr(default) if len(repr(default)) < 20 else "..."
            if type_str:
                p = f"{click.style(name, fg='white', bold=True)}: {click.style(type_str, fg='cyan')} = {click.style(def_str, fg='yellow')}"
            else:
                p = f"{click.style(name, fg='white', bold=True)} = {click.style(def_str, fg='yellow')}"
        else:
            if type_str:
                p = f"{click.style(name, fg='white', bold=True)}: {click.style(type_str, fg='cyan')}"
            else:
                p = click.style(name, fg="white", bold=True)
        params.append(p)

    # Return type
    ret_str = ""
    if sig.return_annotation != inspect.Parameter.empty:
        ret = sig.return_annotation
        ret_name = ret.__name__ if hasattr(ret, "__name__") else str(ret)
        ret_name = ret_name.replace("typing.", "")
        ret_str = f" -> {click.style(ret_name, fg='magenta')}"

    name_s = click.style(func.__name__, fg="green", bold=True)

    if multiline and len(params) > 2:
        param_indent = indent + "    "
        params_str = ",\n".join(f"{param_indent}{p}" for p in params)
        sig_s = f"(\n{params_str}\n{indent}){ret_str}"
    else:
        sig_s = f"({', '.join(params)}){ret_str}"

    return name_s, sig_s


def group_to_json(ctx, group: click.Group) -> None:
    """Output a group's subcommands as Result JSON and exit.

    Provides ``--json`` behavior for group-level commands, listing
    available subcommands with their short help text.
    """
    from scitex_dev import Result

    cmds = {}
    for name in sorted(group.list_commands(ctx) or []):
        cmd = group.get_command(ctx, name)
        if cmd:
            cmds[name] = cmd.get_short_help_str(limit=150)
    click.echo(Result(success=True, data={"commands": cmds}).to_json())
    ctx.exit(0)


__all__ = ["cli", "print_help_recursive", "format_python_signature", "group_to_json"]
