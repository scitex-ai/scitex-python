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
      scitex event get-latest
      scitex event get-latest --type test_complete
      scitex event list-history --limit 10
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
    """Emit an event.

    $ scitex event emit --type test_complete --project my-project
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


@event.command("get-latest")
@click.option("--type", "event_type", default=None, help="Filter by event type")
@click.option(
    "--json", "as_json", is_flag=True, help="Return a structured Result envelope."
)
def latest_cmd(event_type, as_json):
    """Show the latest event.

    $ scitex event get-latest --type test_complete
    """
    from scitex.events import latest

    data = latest(event_type)
    if as_json:
        from scitex_dev import Result

        click.echo(
            Result(
                success=data is not None,
                data={"event": data},
                error="No events found." if data is None else None,
            ).to_json()
        )
    elif data is not None:
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo("No events found.")
    if data is None:
        raise SystemExit(1)


@event.command("list-history")
@click.option("--limit", default=20, help="Max events to show")
@click.option(
    "--json", "as_json", is_flag=True, help="Return a structured Result envelope."
)
def history_cmd(limit, as_json):
    """Show recent event history.

    $ scitex event list-history --limit 10
    """
    from scitex.events import history

    events = history(limit=limit)
    if as_json:
        from scitex_dev import Result

        click.echo(Result(success=True, data={"events": events}).to_json())
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
@click.option(
    "--json", "as_json", is_flag=True, help="Return a structured Result envelope."
)
def types_cmd(as_json):
    """List known event types.

    $ scitex event list-types
    """
    from scitex.events import get_type_info, list_types

    names = list_types()
    if as_json:
        from scitex_dev import Result

        entries = [{"name": name, **get_type_info(name)} for name in names]
        click.echo(Result(success=True, data={"types": entries}).to_json())
        return
    for t in names:
        info = get_type_info(t)
        desc = info.get("description", "")
        keys = ", ".join(info.get("payload_keys", []))
        click.echo(f"  {t:20s} {desc}")
        if keys:
            click.echo(f"  {'':20s} payload: {keys}")


# Preserve established read routes and their text/argv behavior during migration.
from scitex_dev.ecosystem import deprecated_alias

deprecated_alias(event, "latest", target=("get-latest",), remove_in="3.0")
deprecated_alias(event, "history", target=("list-history",), remove_in="3.0")
deprecated_alias(event, "types", target=("list-types",), remove_in="3.0")


# EOF
