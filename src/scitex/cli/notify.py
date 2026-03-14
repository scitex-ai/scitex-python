#!/usr/bin/env python3
"""
SciTeX CLI - Notification Commands

Send notifications, make phone calls, and manage notification backends.
"""

import sys

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def notify(ctx, help_recursive, as_json):
    """
    Notification and alerting tools

    \b
    Backends (fallback order):
      audio      - Text-to-Speech (fast, non-blocking)
      emacs      - Emacs minibuffer message
      matplotlib - Visual popup
      playwright - Browser popup
      email      - SMTP email (slowest, most reliable)
      twilio     - Phone call (explicit only)

    \b
    Examples:
      scitex notify send "Task complete!"
      scitex notify call "Wake up!"
      scitex notify call "Wake up!" --repeat 2
      scitex notify backends
    """
    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, notify)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, notify)
        else:
            click.echo(ctx.get_help())


@notify.command()
@click.argument("message")
@click.option("--title", "-t", help="Notification title")
@click.option(
    "--backend",
    "-b",
    type=click.Choice(
        [
            "audio",
            "emacs",
            "matplotlib",
            "playwright",
            "email",
            "twilio",
            "desktop",
            "webhook",
        ]
    ),
    help="Backend to use (auto-selects with fallback if not specified)",
)
@click.option(
    "--level",
    "-l",
    type=click.Choice(["info", "warning", "error", "critical"]),
    default="info",
    help="Alert level (default: info)",
)
@click.option("--no-fallback", is_flag=True, help="Disable backend fallback on error")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def send(message, title, backend, level, no_fallback, as_json):
    """
    Send a notification via configured backends

    \b
    Examples:
      scitex notify send "Task complete!"
      scitex notify send "Error in pipeline" --backend email --level error
      scitex notify send "Critical failure" --backend twilio --no-fallback
      scitex notify send "Hello" --json
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.notify import alert

        wrap_as_cli(
            alert,
            as_json=True,
            message=message,
            title=title,
            backend=backend,
            level=level,
            fallback=not no_fallback,
        )
        return

    try:
        from scitex.notify import alert

        success = alert(
            message,
            title=title,
            backend=backend,
            level=level,
            fallback=not no_fallback,
        )

        if success:
            click.secho("Notification sent", fg="green")
        else:
            click.secho("Failed to send notification (all backends failed)", fg="red")
            sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notify.command()
@click.argument("message")
@click.option("--title", "-t", help="Call title/context")
@click.option(
    "--level",
    "-l",
    type=click.Choice(["info", "warning", "error", "critical"]),
    default="info",
    help="Alert level (default: info)",
)
@click.option("--to", "to_number", help="Destination phone number (overrides default)")
@click.option(
    "--repeat",
    "-r",
    type=int,
    default=1,
    help="Repeat call N times (30s apart; use 2 to bypass iOS silent mode)",
)
@click.option("--flow-sid", help="Twilio Studio Flow SID (optional)")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def call(message, title, level, to_number, repeat, flow_sid, as_json):
    """
    Make a phone call via Twilio

    \b
    Requires env vars:
      SCITEX_NOTIFY_TWILIO_SID    - Twilio Account SID
      SCITEX_NOTIFY_TWILIO_TOKEN  - Twilio Auth Token
      SCITEX_NOTIFY_TWILIO_FROM   - Twilio phone number
      SCITEX_NOTIFY_TWILIO_TO     - Destination phone number

    \b
    Examples:
      scitex notify call "Build finished!"
      scitex notify call "Wake up!" --repeat 2
      scitex notify call "Alert!" --to +61400000000
      scitex notify call "Alert!" --flow-sid FWxxxxxxx
    """
    kwargs = {}
    if to_number:
        kwargs["to_number"] = to_number
    if flow_sid:
        kwargs["flow_sid"] = flow_sid
    if repeat > 1:
        kwargs["repeat"] = repeat

    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.notify import call as notify_call

        wrap_as_cli(
            notify_call,
            as_json=True,
            message=message,
            title=title,
            level=level,
            **kwargs,
        )
        return

    try:
        from scitex.notify import call as notify_call

        click.echo(f"Calling via Twilio (repeat={repeat})...")
        success = notify_call(
            message,
            title=title,
            level=level,
            **kwargs,
        )

        if success:
            click.secho("Call initiated successfully", fg="green")
        else:
            click.secho("Failed to make call", fg="red")
            click.echo("Check SCITEX_NOTIFY_TWILIO_* env vars are set correctly.")
            sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notify.command()
@click.argument("message")
@click.option("--title", "-t", help="SMS title/subject (prepended to message)")
@click.option("--to", "to_number", help="Destination phone number (overrides default)")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def sms(message, title, to_number, as_json):
    """
    Send an SMS via Twilio

    \b
    Requires env vars:
      SCITEX_NOTIFY_TWILIO_SID    - Twilio Account SID
      SCITEX_NOTIFY_TWILIO_TOKEN  - Twilio Auth Token
      SCITEX_NOTIFY_TWILIO_FROM   - Twilio phone number
      SCITEX_NOTIFY_TWILIO_TO     - Destination phone number

    \b
    Examples:
      scitex notify sms "Build finished!"
      scitex notify sms "Alert!" --to +61400000000
      scitex notify sms "Error in pipeline" --title "SciTeX"
    """
    kwargs = {}
    if to_number:
        kwargs["to_number"] = to_number

    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.notify import sms as notify_sms

        wrap_as_cli(
            notify_sms,
            as_json=True,
            message=message,
            title=title,
            **kwargs,
        )
        return

    try:
        from scitex.notify import sms as notify_sms

        click.echo("Sending SMS via Twilio...")
        success = notify_sms(
            message,
            title=title,
            **kwargs,
        )

        if success:
            click.secho("SMS sent successfully", fg="green")
        else:
            click.secho("Failed to send SMS", fg="red")
            click.echo("Check SCITEX_NOTIFY_TWILIO_* env vars are set correctly.")
            sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notify.command(name="backends")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_backends(as_json):
    """
    List notification backends and their availability

    \b
    Example:
      scitex notify backends
      scitex notify backends --json
    """
    try:
        from scitex.notify import DEFAULT_FALLBACK_ORDER, available_backends
        from scitex.notify._backends import BACKENDS

        available = available_backends()

        if as_json:
            from scitex_dev import Result

            data = {
                "available": available,
                "all_backends": list(BACKENDS.keys()),
                "fallback_order": DEFAULT_FALLBACK_ORDER,
            }
            click.echo(Result(success=True, data=data).to_json())
        else:
            click.secho("Notification Backends", fg="cyan", bold=True)
            click.echo("=" * 40)

            click.echo("\nFallback order:")
            for i, b in enumerate(DEFAULT_FALLBACK_ORDER, 1):
                status = (
                    click.style("available", fg="green")
                    if b in available
                    else click.style("not available", fg="red")
                )
                click.echo(f"  {i}. {b}: {status}")

            # Show non-fallback backends
            non_fallback = [b for b in BACKENDS if b not in DEFAULT_FALLBACK_ORDER]
            if non_fallback:
                click.echo("\nExplicit-only backends:")
                for b in non_fallback:
                    status = (
                        click.style("available", fg="green")
                        if b in available
                        else click.style("not available", fg="red")
                    )
                    click.echo(f"  - {b}: {status}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notify.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def config(as_json):
    """
    Show current notification configuration

    \b
    Example:
      scitex notify config
      scitex notify config --json
    """
    try:
        from scitex.notify._backends._config import get_config

        cfg = get_config()

        if as_json:
            from scitex_dev import Result

            data = {
                "default_backend": cfg.default_backend,
                "backend_priority": cfg.backend_priority,
                "available_priority": cfg.get_available_backend_priority(),
                "first_available": cfg.get_first_available_backend(),
            }
            click.echo(Result(success=True, data=data).to_json())
        else:
            click.secho("Notification Configuration", fg="cyan", bold=True)
            click.echo("=" * 40)
            click.echo(f"\nDefault backend: {cfg.default_backend}")
            click.echo(f"Priority order:  {', '.join(cfg.backend_priority)}")
            click.echo(f"First available: {cfg.get_first_available_backend()}")

            avail = cfg.get_available_backend_priority()
            if avail:
                click.echo("\nAvailable (in priority order):")
                for b in avail:
                    click.echo(f"  - {b}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@notify.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def mcp(ctx, as_json):
    """MCP (Model Context Protocol) server operations for notify."""
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, mcp)
        else:
            click.echo(ctx.get_help())


@mcp.command("list-tools")
@click.option(
    "-v", "--verbose", count=True, help="Verbosity: -v sig, -vv +desc, -vvv full"
)
@click.option("-c", "--compact", is_flag=True, help="Compact signatures (single line)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_tools(ctx, verbose, compact, as_json):
    """List available notify MCP tools (delegates to main MCP with -m notify)."""
    from scitex.cli.mcp import list_tools as main_list_tools

    ctx.invoke(
        main_list_tools,
        verbose=verbose,
        compact=compact,
        module="notify",
        as_json=as_json,
    )


@notify.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List Python APIs (alias for: scitex introspect api scitex.notify)."""
    from scitex.cli.introspect import api

    ctx.invoke(
        api,
        dotted_path="scitex.notify",
        verbose=verbose,
        max_depth=max_depth,
        as_json=as_json,
    )


if __name__ == "__main__":
    notify()
