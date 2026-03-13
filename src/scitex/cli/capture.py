#!/usr/bin/env python3
"""
SciTeX CLI - Capture Commands (Screenshot/Monitoring)

Provides screen capture, monitoring, and GIF creation.
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
def capture(ctx, help_recursive, as_json):
    """
    Screen capture and monitoring utilities

    \b
    Commands:
      snap          Take a single screenshot
      start         Start continuous monitoring
      stop          Stop monitoring
      gif           Create GIF from session
      info          Display info (monitors, windows)
      window        Capture specific window by handle

    \b
    Examples:
      scitex capture snap                      # Take screenshot
      scitex capture snap --message "debug"   # With message in filename
      scitex capture start --interval 2       # Monitor every 2 seconds
      scitex capture stop                     # Stop monitoring
      scitex capture gif                      # Create GIF from latest session
      scitex capture info                     # List monitors and windows
    """
    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, capture)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, capture)
        else:
            click.echo(ctx.get_help())


@capture.command()
@click.option("--message", "-m", default="", help="Message to include in filename")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option(
    "--quality", "-q", type=int, default=85, help="JPEG quality 1-100 (default: 85)"
)
@click.option(
    "--monitor", type=int, default=0, help="Monitor number (0-based, default: 0)"
)
@click.option("--all-monitors", is_flag=True, help="Capture all monitors combined")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def snap(message, output, quality, monitor, all_monitors, as_json):
    """
    Take a single screenshot

    \b
    Examples:
      scitex capture snap
      scitex capture snap --message "before-change"
      scitex capture snap --all-monitors
      scitex capture snap --monitor 1 --quality 95
    """
    # Build kwargs
    kwargs = {"message": message}
    if output:
        kwargs["output_dir"] = output
    if quality != 85:
        kwargs["quality"] = quality
    if all_monitors:
        kwargs["capture_all"] = True
    else:
        kwargs["monitor_id"] = monitor

    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.capture import snap as take_snap

        wrap_as_cli(take_snap, as_json=True, **kwargs)
        return

    try:
        from scitex.capture import snap as take_snap

        click.echo("Taking screenshot...")

        result = take_snap(**kwargs)

        if result:
            click.secho(f"Screenshot saved: {result}", fg="green")
        else:
            click.secho("Screenshot taken", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@capture.command()
@click.option(
    "--interval",
    "-i",
    type=float,
    default=1.0,
    help="Seconds between captures (default: 1.0)",
)
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option(
    "--quality", "-q", type=int, default=60, help="JPEG quality 1-100 (default: 60)"
)
@click.option(
    "--monitor", type=int, default=0, help="Monitor number (0-based, default: 0)"
)
@click.option("--all-monitors", is_flag=True, help="Capture all monitors combined")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def start(interval, output, quality, monitor, all_monitors, as_json):
    """
    Start continuous screenshot monitoring

    \b
    Examples:
      scitex capture start                    # Default 1 second interval
      scitex capture start --interval 0.5    # Every 0.5 seconds
      scitex capture start --all-monitors
    """
    kwargs = {"interval": interval}
    if output:
        kwargs["output_dir"] = output
    if quality != 60:
        kwargs["quality"] = quality
    if all_monitors:
        kwargs["capture_all"] = True
    else:
        kwargs["monitor_id"] = monitor

    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.capture import start as start_monitor

        wrap_as_cli(start_monitor, as_json=True, **kwargs)
        return

    try:
        from scitex.capture import start as start_monitor

        click.echo(f"Starting monitoring (interval: {interval}s)...")
        click.echo("Press Ctrl+C or run 'scitex capture stop' to stop")

        start_monitor(**kwargs)
        click.secho("Monitoring started", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@capture.command()
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def stop(as_json):
    """
    Stop continuous monitoring

    \b
    Example:
      scitex capture stop
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.capture import stop as stop_monitor

        wrap_as_cli(stop_monitor, as_json=True)
        return

    try:
        from scitex.capture import stop as stop_monitor

        stop_monitor()
        click.secho("Monitoring stopped", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@capture.command()
@click.option(
    "--session",
    "-s",
    help="Session ID (e.g., '20250823_104523'). Use 'latest' for most recent.",
)
@click.option("--output", "-o", type=click.Path(), help="Output GIF path")
@click.option(
    "--duration",
    "-d",
    type=float,
    default=0.5,
    help="Duration per frame in seconds (default: 0.5)",
)
@click.option("--max-frames", type=int, help="Maximum number of frames to include")
@click.option(
    "--pattern", "-p", help="Glob pattern for images (alternative to session)"
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def gif(session, output, duration, max_frames, pattern, as_json):
    """
    Create animated GIF from screenshots

    \b
    Examples:
      scitex capture gif                         # From latest session
      scitex capture gif --session 20250823_104523
      scitex capture gif --duration 0.3 --max-frames 50
      scitex capture gif --pattern "./screenshots/*.jpg"
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        def _run():
            if pattern:
                from scitex.capture import create_gif_from_pattern

                return create_gif_from_pattern(
                    pattern=pattern,
                    output_path=output,
                    duration=duration,
                    max_frames=max_frames,
                )
            elif session:
                from scitex.capture import create_gif_from_session

                return create_gif_from_session(
                    session_id=session,
                    output_path=output,
                    duration=duration,
                    max_frames=max_frames,
                )
            else:
                from scitex.capture import create_gif_from_latest_session

                return create_gif_from_latest_session(
                    output_path=output,
                    duration=duration,
                    max_frames=max_frames,
                )

        wrap_as_cli(_run, as_json=True)
        return

    try:
        if pattern:
            from scitex.capture import create_gif_from_pattern

            click.echo(f"Creating GIF from pattern: {pattern}")
            result = create_gif_from_pattern(
                pattern=pattern,
                output_path=output,
                duration=duration,
                max_frames=max_frames,
            )
        elif session:
            from scitex.capture import create_gif_from_session

            click.echo(f"Creating GIF from session: {session}")
            result = create_gif_from_session(
                session_id=session,
                output_path=output,
                duration=duration,
                max_frames=max_frames,
            )
        else:
            from scitex.capture import create_gif_from_latest_session

            click.echo("Creating GIF from latest session...")
            result = create_gif_from_latest_session(
                output_path=output,
                duration=duration,
                max_frames=max_frames,
            )

        if result:
            click.secho(f"GIF created: {result}", fg="green")
        else:
            click.secho("No screenshots found to create GIF", fg="yellow")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@capture.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def info(as_json):
    """
    Display system info (monitors, windows, virtual desktops)

    \b
    Examples:
      scitex capture info
      scitex capture info --json
    """
    try:
        from scitex.capture import get_info

        info_data = get_info()

        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data=info_data).to_json())
        else:
            click.secho("Display Information", fg="cyan", bold=True)
            click.echo("=" * 50)

            # Monitors
            monitors = info_data.get("Monitors", {})
            click.secho(f"\nMonitors ({monitors.get('Count', 0)}):", fg="yellow")
            for i, mon in enumerate(monitors.get("Details", [])):
                primary = " (Primary)" if mon.get("Primary") else ""
                click.echo(f"  [{i}] {mon.get('Width')}x{mon.get('Height')}{primary}")

            # Windows
            windows = info_data.get("Windows", {})
            click.secho(f"\nWindows ({windows.get('Count', 0)}):", fg="yellow")
            for win in windows.get("Details", [])[:10]:  # Show first 10
                title = win.get("Title", "")[:40]
                handle = win.get("Handle", "")
                click.echo(f"  [{handle}] {title}")
            if windows.get("Count", 0) > 10:
                click.echo(f"  ... and {windows.get('Count') - 10} more")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@capture.command()
@click.argument("handle", type=int)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--quality", "-q", type=int, default=85, help="JPEG quality 1-100")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def window(handle, output, quality, as_json):
    """
    Capture a specific window by its handle

    \b
    Get window handles with: scitex capture info

    \b
    Examples:
      scitex capture window 12345
      scitex capture window 12345 --output ./window.jpg
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.capture import capture_window

        wrap_as_cli(capture_window, as_json=True, handle=handle, output=output)
        return

    try:
        from scitex.capture import capture_window

        click.echo(f"Capturing window {handle}...")
        result = capture_window(handle, output)

        if result:
            click.secho(f"Window captured: {result}", fg="green")
        else:
            click.secho("Window captured", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


from ._capture_mcp import register_mcp

register_mcp(capture)


@capture.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List Python APIs (alias for: scitex introspect api scitex.capture)."""
    from scitex.cli.introspect import api

    ctx.invoke(
        api,
        dotted_path="scitex.capture",
        verbose=verbose,
        max_depth=max_depth,
        as_json=as_json,
    )


if __name__ == "__main__":
    capture()
