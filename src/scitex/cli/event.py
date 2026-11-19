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
      scitex event show-latest
      scitex event show-latest --type test_complete
      scitex event list --limit 10
      scitex event list-types
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
    """Emit an event and print it as JSON.

    \b
    Examples:
      scitex event emit --type test_complete --project figrecipe
      scitex event emit --type test_complete --project figrecipe --status failure
      scitex event emit --type job_done --project gpac --payload '{"job": 42}'
    """
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


@event.command("show-latest")
@click.option("--type", "event_type", default=None, help="Filter by event type")
@click.option("--json", "as_json", is_flag=True, help="Output as compact JSON")
def latest_cmd(event_type, as_json):
    """Show the latest event (exit 1 when there is none).

    \b
    Examples:
      scitex event show-latest
      scitex event show-latest --type test_complete
      scitex event show-latest --json
    """
    from scitex.events import latest

    data = latest(event_type)
    if data is None:
        click.echo("null" if as_json else "No events found.")
        raise SystemExit(1)
    click.echo(json.dumps(data) if as_json else json.dumps(data, indent=2))


@event.command("list")
@click.option("--limit", default=20, help="Max events to show")
@click.option("--json", "as_json", is_flag=True, help="Output as a JSON array")
def history_cmd(limit, as_json):
    """List recent events.

    \b
    Examples:
      scitex event list
      scitex event list --limit 10
      scitex event list --json
    """
    from scitex.events import history

    events = history(limit=limit)
    if as_json:
        click.echo(json.dumps(events))
        return
    if not events:
        click.echo("No event history.")
        return
    for ev in events:
        status_icon = "+" if ev.get("status") == "success" else "x"
        click.echo(
            f"  [{status_icon}] {ev['type']} | {ev['project']} | {ev['timestamp']}"
        )


@event.command("list-types")
@click.option("--json", "as_json", is_flag=True, help="Output as a JSON object")
def types_cmd(as_json):
    """List known event types.

    \b
    Examples:
      scitex event list-types
      scitex event list-types --json
    """
    from scitex.events import get_type_info, list_types

    if as_json:
        click.echo(json.dumps({t: get_type_info(t) for t in list_types()}))
        return
    for t in list_types():
        info = get_type_info(t)
        desc = info.get("description", "")
        keys = ", ".join(info.get("payload_keys", []))
        click.echo(f"  {t:20s} {desc}")
        if keys:
            click.echo(f"  {'':20s} payload: {keys}")


# Renamed to the noun/verb convention; old names stay as hidden aliases.
from ._deprecation import alias_renamed  # noqa: E402

alias_renamed(
    event,
    {"history": "list", "latest": "show-latest", "types": "list-types"},
)


# EOF
