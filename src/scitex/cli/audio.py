#!/usr/bin/env python3
"""
SciTeX CLI - Audio Commands (Text-to-Speech)

Provides text-to-speech with multiple backend support.
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
def audio(ctx, help_recursive, as_json):
    """
    Text-to-speech utilities

    \b
    Backends (fallback order):
      pyttsx3    - System TTS (offline, free)
      gtts       - Google TTS (free, needs internet)
      luxtts     - LuxTTS (open-source, offline, voice-cloning)
      elevenlabs - ElevenLabs (paid, high quality)

    \b
    Examples:
      scitex audio speak "Hello world"
      scitex audio speak "Bonjour" --backend gtts --voice fr
      scitex audio backends              # List available backends
      scitex audio check                 # Check audio status (WSL)
    """
    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, audio)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, audio)
        else:
            click.echo(ctx.get_help())


@audio.command()
@click.argument("text")
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["pyttsx3", "gtts", "luxtts", "elevenlabs"]),
    help="TTS backend (auto-selects with fallback if not specified)",
)
@click.option("--voice", "-v", help="Voice name, ID, or language code")
@click.option("--output", "-o", type=click.Path(), help="Save audio to file")
@click.option("--no-play", is_flag=True, help="Don't play audio (only save)")
@click.option("--rate", "-r", type=int, help="Speech rate (pyttsx3 only, default: 150)")
@click.option(
    "--speed", "-s", type=float, help="Speed multiplier (gtts only, e.g., 1.5)"
)
@click.option("--no-fallback", is_flag=True, help="Disable backend fallback on error")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def speak(text, backend, voice, output, no_play, rate, speed, no_fallback, as_json):
    """
    Convert text to speech

    \b
    Examples:
      scitex audio speak "Hello world"
      scitex audio speak "Bonjour" --backend gtts --voice fr
      scitex audio speak "Test" --output speech.mp3 --no-play
      scitex audio speak "Fast speech" --backend pyttsx3 --rate 200
      scitex audio speak "Slow speech" --backend gtts --speed 0.8
      scitex audio speak "Hello" --json
    """
    import logging
    import warnings

    # Suppress noisy warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    kwargs = {
        "text": text,
        "play": not no_play,
        "fallback": not no_fallback,
    }
    if backend:
        kwargs["backend"] = backend
    if voice:
        kwargs["voice"] = voice
    if output:
        kwargs["output_path"] = output
    if rate:
        kwargs["rate"] = rate
    if speed:
        kwargs["speed"] = speed

    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.audio import speak as tts_speak

        wrap_as_cli(tts_speak, as_json=True, **kwargs)
        return

    try:
        from scitex.audio import speak as tts_speak

        result = tts_speak(**kwargs)

        if output and result.get("path"):
            click.secho(f"Audio saved: {result['path']}", fg="green")

        if not no_play:
            if result.get("played"):
                click.secho("Speech completed (audio played)", fg="green")
            else:
                click.secho(
                    "Warning: Audio generated but playback failed (no speaker?)",
                    fg="yellow",
                )

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@audio.command(name="backends")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_backends(as_json):
    """
    List available TTS backends

    \b
    Example:
      scitex audio backends
      scitex audio backends --json
    """
    try:
        from scitex.audio import FALLBACK_ORDER, available_backends

        backends = available_backends()

        if as_json:
            from scitex_dev import Result

            data = {
                "available": backends,
                "fallback_order": FALLBACK_ORDER,
            }
            click.echo(Result(success=True, data=data).to_json())
        else:
            click.secho("Available TTS Backends", fg="cyan", bold=True)
            click.echo("=" * 40)

            click.echo("\nFallback order:")
            for i, b in enumerate(FALLBACK_ORDER, 1):
                status = (
                    click.style("available", fg="green")
                    if b in backends
                    else click.style("not installed", fg="red")
                )
                click.echo(f"  {i}. {b}: {status}")

            if not backends:
                click.echo()
                click.secho("No backends available!", fg="red")
                click.echo("Install one of:")
                click.echo("  pip install pyttsx3  # + apt install espeak-ng")
                click.echo("  pip install gTTS")
                click.echo("  pip install elevenlabs")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@audio.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def check(as_json):
    """
    Check audio status (especially for WSL)

    \b
    Checks:
      - WSL detection
      - WSLg availability
      - PulseAudio connection
      - Windows fallback availability

    \b
    Example:
      scitex audio check
      scitex audio check --json
    """
    try:
        from scitex.audio import check_wsl_audio

        status = check_wsl_audio()

        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data=status).to_json())
        else:
            click.secho("Audio Status Check", fg="cyan", bold=True)
            click.echo("=" * 40)

            def status_mark(val):
                return (
                    click.style("Yes", fg="green")
                    if val
                    else click.style("No", fg="red")
                )

            click.echo(f"\nWSL Environment: {status_mark(status['is_wsl'])}")

            if status["is_wsl"]:
                click.echo(f"WSLg Available: {status_mark(status['wslg_available'])}")
                click.echo(
                    f"PulseServer Socket: {status_mark(status['pulse_server_exists'])}"
                )
                click.echo(
                    f"PulseAudio Connected: {status_mark(status['pulse_connected'])}"
                )
                click.echo(
                    f"Windows Fallback: {status_mark(status['windows_fallback_available'])}"
                )

            click.echo()
            rec = status["recommended"]
            if rec == "linux":
                click.secho("Recommended: Linux audio (PulseAudio)", fg="green")
            elif rec == "windows":
                click.secho(
                    "Recommended: Windows fallback (powershell.exe)", fg="yellow"
                )
            else:
                click.secho("No audio output available", fg="red")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@audio.command()
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def stop(as_json):
    """
    Stop any currently playing speech

    \b
    Example:
      scitex audio stop
      scitex audio stop --json
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.audio import stop_speech

        wrap_as_cli(stop_speech, as_json=True)
        return
    try:
        from scitex.audio import stop_speech

        stop_speech()
        click.secho("Speech stopped", fg="green")
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@audio.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def mcp(ctx, as_json):
    """MCP (Model Context Protocol) server operations for audio."""
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, mcp)
        else:
            click.echo(ctx.get_help())


@mcp.command()
@click.option(
    "-t",
    "--transport",
    type=click.Choice(["stdio", "sse", "http"]),
    default="stdio",
    help="Transport protocol (default: stdio)",
)
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host for HTTP/SSE transport (default: 0.0.0.0)",
)
@click.option(
    "--port",
    default=31293,
    type=int,
    help="Port for HTTP/SSE transport (default: 31293)",
)
def start(transport, host, port):
    """Start the MCP server for remote audio playback.

    \b
    Examples:
      scitex audio mcp start
      scitex audio mcp start -t http --port 31293
    """
    try:
        from scitex_audio.mcp_server import FASTMCP_AVAILABLE, run_server

        if not FASTMCP_AVAILABLE:
            click.secho("Error: fastmcp not installed", fg="red", err=True)
            click.echo("\nInstall with:")
            click.echo("  pip install fastmcp")
            sys.exit(1)

        if transport != "stdio":
            click.secho(f"Starting scitex-audio MCP server ({transport})", fg="cyan")
            click.echo(f"  Host: {host}")
            click.echo(f"  Port: {port}")
            click.echo()
            click.echo("Remote agents can connect via SSH tunnel:")
            click.echo(f"  ssh -L {port}:localhost:{port} <this-host>")
            click.echo()

        run_server(transport=transport, host=host, port=port)

    except ImportError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        click.echo("\nInstall dependencies:")
        click.echo("  pip install fastmcp")
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@mcp.command()
def doctor():
    """
    Check MCP server health and dependencies

    \b
    Example:
      scitex audio mcp doctor
    """
    click.secho("Audio MCP Server Health Check", fg="cyan", bold=True)
    click.echo()

    # Check fastmcp
    click.echo("Checking FastMCP... ", nl=False)
    try:
        from scitex_audio.mcp_server import FASTMCP_AVAILABLE

        if FASTMCP_AVAILABLE:
            click.secho("OK", fg="green")
        else:
            click.secho("NOT INSTALLED", fg="red")
            click.echo("  Install with: pip install fastmcp")
    except ImportError:
        click.secho("FAIL", fg="red")

    # Check audio backends
    click.echo("Checking audio backends... ", nl=False)
    try:
        from scitex.audio import available_backends

        backends = available_backends()
        if backends:
            click.secho(f"OK ({', '.join(backends)})", fg="green")
        else:
            click.secho("NONE AVAILABLE", fg="yellow")
    except Exception as e:
        click.secho(f"FAIL ({e})", fg="red")


@mcp.command("list-tools")
@click.option(
    "-v", "--verbose", count=True, help="Verbosity: -v sig, -vv +desc, -vvv full"
)
@click.option("-c", "--compact", is_flag=True, help="Compact signatures (single line)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_tools(ctx, verbose, compact, as_json):
    """List available audio MCP tools (delegates to main MCP with -m audio)."""
    from scitex.cli.mcp import list_tools as main_list_tools

    # Invoke main list-tools with audio module filter
    ctx.invoke(
        main_list_tools,
        verbose=verbose,
        compact=compact,
        module="audio",
        as_json=as_json,
    )


@audio.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind (default: 0.0.0.0)",
)
@click.option(
    "--port",
    default=31293,
    type=int,
    help="Port to bind (default: 31293)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Kill existing process using the port if any",
)
def relay(host, port, force):
    """
    Run simple HTTP relay server for remote audio playback

    \b
    Endpoints: POST /speak, GET /health, GET /list_backends

    \b
    Example:
      scitex audio relay --port 31293
      # Remote: export SCITEX_AUDIO_RELAY_URL=http://LOCAL_IP:31293
      # Or SSH: ssh -R 31293:localhost:31293 remote-server
    """
    try:
        from scitex_audio.mcp_server import run_relay_server

        # Handle force flag
        if force:
            from scitex_audio._utils import kill_process_on_port

            kill_process_on_port(port)

        click.secho("Starting audio relay server", fg="cyan")
        click.echo(f"  Host: {host}")
        click.echo(f"  Port: {port}")
        click.echo()
        click.echo("Endpoints:")
        click.echo("  POST /speak       - Play text-to-speech")
        click.echo("  GET  /health      - Health check")
        click.echo("  GET  /list_backends - List backends")
        click.echo()

        run_relay_server(host=host, port=port, force=force)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@audio.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List Python APIs (alias for: scitex introspect api scitex.audio)."""
    from scitex.cli.introspect import api

    ctx.invoke(
        api,
        dotted_path="scitex.audio",
        verbose=verbose,
        max_depth=max_depth,
        as_json=as_json,
    )


if __name__ == "__main__":
    audio()
