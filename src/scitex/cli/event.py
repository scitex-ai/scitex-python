#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: scitex/cli/event.py

"""SciTeX Event CLI — emit and query events."""

import json

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def event(ctx, as_json):
    """
    Event bus for async task results.

    \b
    Examples:
      scitex event emit --type test_complete --project figrecipe --status success
      scitex event latest
      scitex event latest --type test_complete
      scitex event history --limit 10
      scitex event types
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, event)
        else:
            click.echo(ctx.get_help())


@event.command("emit")
@click.option(
    "--type", "event_type", required=True, help="Event type (e.g., test_complete)"
)
@click.option("--project", required=True, help="Project name")
@click.option("--status", default="success", help="Status: success or failure")
@click.option("--source", default="local", help="Source: local, hpc, ci")
@click.option("--payload", default=None, help="JSON payload string")
def emit_cmd(event_type, project, status, source, payload):
    """Emit an event."""
    from scitex.events import emit

    payload_dict = {}
    if payload:
        try:
            payload_dict = json.loads(payload)
        except json.JSONDecodeError:
            click.echo(f"Error: invalid JSON payload: {payload}", err=True)
            raise SystemExit(1) from None

    ev = emit(
        event_type, project=project, status=status, payload=payload_dict, source=source
    )
    click.echo(json.dumps(ev.to_dict(), indent=2))


@event.command("latest")
@click.option("--type", "event_type", default=None, help="Filter by event type")
def latest_cmd(event_type):
    """Show the latest event."""
    from scitex.events import latest

    data = latest(event_type)
    if data is None:
        click.echo("No events found.")
        raise SystemExit(1)
    click.echo(json.dumps(data, indent=2))


@event.command("history")
@click.option("--limit", default=20, help="Max events to show")
def history_cmd(limit):
    """Show recent event history."""
    from scitex.events import history

    events = history(limit=limit)
    if not events:
        click.echo("No event history.")
        return
    for ev in events:
        status_icon = "+" if ev.get("status") == "success" else "x"
        click.echo(
            f"  [{status_icon}] {ev['type']} | {ev['project']} | {ev['timestamp']}"
        )


@event.command("types")
def types_cmd():
    """List known event types."""
    from scitex.events import get_type_info, list_types

    for t in list_types():
        info = get_type_info(t)
        desc = info.get("description", "")
        keys = ", ".join(info.get("payload_keys", []))
        click.echo(f"  {t:20s} {desc}")
        if keys:
            click.echo(f"  {'':20s} payload: {keys}")


# EOF
