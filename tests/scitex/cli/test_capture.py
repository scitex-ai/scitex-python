#!/usr/bin/env python3
"""Tests for scitex.cli.capture - Screenshot capture CLI commands."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.capture import capture


class TestCaptureGroup:
    """Tests for the capture command group."""

    def test_capture_help(self):
        """Test that capture help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(capture, ["--help"])
        assert result.exit_code == 0
        assert "Screen capture and monitoring" in result.output

    def test_capture_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(capture, ["--help"])
        expected_commands = ["snap", "start", "stop", "gif", "info", "window"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in capture help"


class TestCaptureSnap:
    """Tests for the capture snap command."""

    def test_snap_default(self):
        """Test snap command with default options."""
        runner = CliRunner()
        with patch("scitex.capture.snap") as mock_snap:
            mock_snap.return_value = "/tmp/screenshot.jpg"
            result = runner.invoke(capture, ["snap"])
            assert result.exit_code == 0
            assert "Screenshot saved" in result.output
            mock_snap.assert_called_once()

    def test_snap_with_output(self):
        """Test snap command with output path."""
        runner = CliRunner()
        with patch("scitex.capture.snap") as mock_snap:
            mock_snap.return_value = "/tmp/custom.jpg"
            result = runner.invoke(capture, ["snap", "--output", "/tmp/custom.jpg"])
            assert result.exit_code == 0
            call_kwargs = mock_snap.call_args[1]
            # CLI maps --output to output_dir parameter
            assert call_kwargs.get("output_dir") == "/tmp/custom.jpg"

    def test_snap_with_monitor(self):
        """Test snap command with specific monitor."""
        runner = CliRunner()
        with patch("scitex.capture.snap") as mock_snap:
            mock_snap.return_value = "/tmp/screenshot.jpg"
            result = runner.invoke(capture, ["snap", "--monitor", "1"])
            assert result.exit_code == 0
            call_kwargs = mock_snap.call_args[1]
            assert call_kwargs.get("monitor_id") == 1

    def test_snap_all_monitors(self):
        """Test snap command with --all-monitors flag."""
        runner = CliRunner()
        with patch("scitex.capture.snap") as mock_snap:
            mock_snap.return_value = "/tmp/screenshot.jpg"
            result = runner.invoke(capture, ["snap", "--all-monitors"])
            assert result.exit_code == 0
            call_kwargs = mock_snap.call_args[1]
            assert call_kwargs.get("capture_all") is True

    def test_snap_with_quality(self):
        """Test snap command with quality option."""
        runner = CliRunner()
        with patch("scitex.capture.snap") as mock_snap:
            mock_snap.return_value = "/tmp/screenshot.jpg"
            result = runner.invoke(capture, ["snap", "--quality", "90"])
            assert result.exit_code == 0
            call_kwargs = mock_snap.call_args[1]
            assert call_kwargs.get("quality") == 90

    def test_snap_error_handling(self):
        """Test snap command handles errors gracefully."""
        runner = CliRunner()
        with patch("scitex.capture.snap") as mock_snap:
            mock_snap.side_effect = Exception("Screenshot failed")
            result = runner.invoke(capture, ["snap"])
            assert result.exit_code == 1
            assert "Error" in result.output


class TestCaptureStart:
    """Tests for the capture start command."""

    def test_start_default(self):
        """Test start command with default options."""
        runner = CliRunner()
        with patch("scitex.capture.start") as mock_start:
            mock_start.return_value = {"session_id": "20250108_120000"}
            result = runner.invoke(capture, ["start"])
            assert result.exit_code == 0
            assert "Monitoring started" in result.output
            mock_start.assert_called_once()

    def test_start_with_interval(self):
        """Test start command with custom interval."""
        runner = CliRunner()
        with patch("scitex.capture.start") as mock_start:
            mock_start.return_value = {"session_id": "20250108_120000"}
            result = runner.invoke(capture, ["start", "--interval", "2.0"])
            assert result.exit_code == 0
            call_kwargs = mock_start.call_args[1]
            assert call_kwargs.get("interval") == 2.0

    def test_start_with_output_dir(self):
        """Test start command with output directory."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("scitex.capture.start") as mock_start:
                mock_start.return_value = {"session_id": "20250108_120000"}
                result = runner.invoke(capture, ["start", "--output", tmpdir])
                assert result.exit_code == 0


class TestCaptureStop:
    """Tests for the capture stop command."""

    def test_stop(self):
        """Test stop command."""
        runner = CliRunner()
        with patch("scitex.capture.stop") as mock_stop:
            mock_stop.return_value = {"stopped": True, "count": 10}
            result = runner.invoke(capture, ["stop"])
            assert result.exit_code == 0
            assert "Monitoring stopped" in result.output

    def test_stop_not_running(self):
        """Test stop command when not running."""
        runner = CliRunner()
        with patch("scitex.capture.stop") as mock_stop:
            mock_stop.return_value = {"stopped": False}
            result = runner.invoke(capture, ["stop"])
            assert result.exit_code == 0


class TestCaptureGif:
    """Tests for the capture gif command."""

    def test_gif_from_session(self):
        """Test gif command with session ID."""
        runner = CliRunner()
        with patch("scitex.capture.create_gif_from_session") as mock_gif:
            mock_gif.return_value = "/tmp/output.gif"
            result = runner.invoke(capture, ["gif", "--session", "20250108_120000"])
            assert result.exit_code == 0
            assert "GIF created" in result.output

    def test_gif_from_latest(self):
        """Test gif command with latest session."""
        runner = CliRunner()
        with patch("scitex.capture.create_gif_from_latest_session") as mock_gif:
            mock_gif.return_value = "/tmp/output.gif"
            result = runner.invoke(capture, ["gif"])
            assert result.exit_code == 0
            assert "GIF created" in result.output

    def test_gif_with_output(self):
        """Test gif command with output path."""
        runner = CliRunner()
        with patch("scitex.capture.create_gif_from_session") as mock_gif:
            mock_gif.return_value = "/tmp/custom.gif"
            result = runner.invoke(
                capture,
                ["gif", "--session", "20250108_120000", "--output", "/tmp/custom.gif"],
            )
            assert result.exit_code == 0
            call_kwargs = mock_gif.call_args[1]
            assert call_kwargs.get("output_path") == "/tmp/custom.gif"

    def test_gif_with_duration(self):
        """Test gif command with frame duration."""
        runner = CliRunner()
        with patch("scitex.capture.create_gif_from_session") as mock_gif:
            mock_gif.return_value = "/tmp/output.gif"
            result = runner.invoke(
                capture, ["gif", "--session", "20250108_120000", "--duration", "0.3"]
            )
            assert result.exit_code == 0
            call_kwargs = mock_gif.call_args[1]
            assert call_kwargs.get("duration") == 0.3

    def test_gif_failure(self):
        """Test gif command handles failure."""
        runner = CliRunner()
        with patch("scitex.capture.create_gif_from_latest_session") as mock_gif:
            mock_gif.return_value = None
            result = runner.invoke(capture, ["gif"])
            assert result.exit_code == 0  # Still 0 but with warning message
            assert "No screenshots found" in result.output


class TestCaptureInfo:
    """Tests for the capture info command."""

    def test_info_default(self):
        """Test info command."""
        runner = CliRunner()
        with patch("scitex.capture.get_info") as mock_info:
            mock_info.return_value = {
                "Monitors": {
                    "Count": 1,
                    "Details": [{"Width": 1920, "Height": 1080, "Primary": True}],
                },
                "Windows": {"Count": 0, "Details": []},
            }
            result = runner.invoke(capture, ["info"])
            assert result.exit_code == 0
            assert "Display Information" in result.output
            assert "Monitors" in result.output

    def test_info_json(self):
        """Test info command with --json flag."""
        runner = CliRunner()
        with patch("scitex.capture.get_info") as mock_info:
            mock_info.return_value = {
                "Monitors": {"Count": 1, "Details": [{"Width": 1920, "Height": 1080}]},
            }
            result = runner.invoke(capture, ["info", "--json"])
            assert result.exit_code == 0
            output = json.loads(result.output)
            data = output.get("data", output)
            assert "Monitors" in data


class TestCaptureWindow:
    """Tests for the capture window command."""

    def test_window_capture(self):
        """Test window capture command."""
        runner = CliRunner()
        with patch("scitex.capture.capture_window") as mock_capture:
            mock_capture.return_value = "/tmp/window.jpg"
            result = runner.invoke(capture, ["window", "12345"])
            assert result.exit_code == 0
            assert "Window captured" in result.output
            mock_capture.assert_called_once()

    def test_window_with_output(self):
        """Test window capture with output path."""
        runner = CliRunner()
        with patch("scitex.capture.capture_window") as mock_capture:
            mock_capture.return_value = "/tmp/custom.jpg"
            result = runner.invoke(
                capture, ["window", "12345", "--output", "/tmp/custom.jpg"]
            )
            assert result.exit_code == 0

    def test_window_failure(self):
        """Test window capture handles failure."""
        runner = CliRunner()
        with patch("scitex.capture.capture_window") as mock_capture:
            mock_capture.return_value = None
            result = runner.invoke(capture, ["window", "12345"])
            assert result.exit_code == 0  # Still 0 since window was captured
            assert "Window captured" in result.output


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/capture.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# """
# SciTeX CLI - Capture Commands (Screenshot/Monitoring)
#
# Provides screen capture, monitoring, and GIF creation.
# """
#
# import sys
#
# import click
#
#
# @click.group(context_settings={"help_option_names": ["-h", "--help"]})
# def capture():
#     """
#     Screen capture and monitoring utilities
#
#     \b
#     Commands:
#       snap          Take a single screenshot
#       start         Start continuous monitoring
#       stop          Stop monitoring
#       gif           Create GIF from session
#       info          Display info (monitors, windows)
#       window        Capture specific window by handle
#
#     \b
#     Examples:
#       scitex capture snap                      # Take screenshot
#       scitex capture snap --message "debug"   # With message in filename
#       scitex capture start --interval 2       # Monitor every 2 seconds
#       scitex capture stop                     # Stop monitoring
#       scitex capture gif                      # Create GIF from latest session
#       scitex capture info                     # List monitors and windows
#     """
#     pass
#
#
# @capture.command()
# @click.option("--message", "-m", default="", help="Message to include in filename")
# @click.option("--output", "-o", type=click.Path(), help="Output directory")
# @click.option(
#     "--quality", "-q", type=int, default=85, help="JPEG quality 1-100 (default: 85)"
# )
# @click.option(
#     "--monitor", type=int, default=0, help="Monitor number (0-based, default: 0)"
# )
# @click.option("--all-monitors", is_flag=True, help="Capture all monitors combined")
# def snap(message, output, quality, monitor, all_monitors):
#     """
#     Take a single screenshot
#
#     \b
#     Examples:
#       scitex capture snap
#       scitex capture snap --message "before-change"
#       scitex capture snap --all-monitors
#       scitex capture snap --monitor 1 --quality 95
#     """
#     try:
#         from scitex.capture import snap as take_snap
#
#         click.echo("Taking screenshot...")
#
#         # Build kwargs
#         kwargs = {"message": message}
#         if output:
#             kwargs["output_dir"] = output
#         if quality != 85:
#             kwargs["quality"] = quality
#         if all_monitors:
#             kwargs["capture_all"] = True
#         else:
#             kwargs["monitor_id"] = monitor
#
#         result = take_snap(**kwargs)
#
#         if result:
#             click.secho(f"Screenshot saved: {result}", fg="green")
#         else:
#             click.secho("Screenshot taken", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @capture.command()
# @click.option(
#     "--interval",
#     "-i",
#     type=float,
#     default=1.0,
#     help="Seconds between captures (default: 1.0)",
# )
# @click.option("--output", "-o", type=click.Path(), help="Output directory")
# @click.option(
#     "--quality", "-q", type=int, default=60, help="JPEG quality 1-100 (default: 60)"
# )
# @click.option(
#     "--monitor", type=int, default=0, help="Monitor number (0-based, default: 0)"
# )
# @click.option("--all-monitors", is_flag=True, help="Capture all monitors combined")
# def start(interval, output, quality, monitor, all_monitors):
#     """
#     Start continuous screenshot monitoring
#
#     \b
#     Examples:
#       scitex capture start                    # Default 1 second interval
#       scitex capture start --interval 0.5    # Every 0.5 seconds
#       scitex capture start --all-monitors
#     """
#     try:
#         from scitex.capture import start as start_monitor
#
#         click.echo(f"Starting monitoring (interval: {interval}s)...")
#         click.echo("Press Ctrl+C or run 'scitex capture stop' to stop")
#
#         kwargs = {"interval": interval}
#         if output:
#             kwargs["output_dir"] = output
#         if quality != 60:
#             kwargs["quality"] = quality
#         if all_monitors:
#             kwargs["capture_all"] = True
#         else:
#             kwargs["monitor_id"] = monitor
#
#         start_monitor(**kwargs)
#         click.secho("Monitoring started", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @capture.command()
# def stop():
#     """
#     Stop continuous monitoring
#
#     \b
#     Example:
#       scitex capture stop
#     """
#     try:
#         from scitex.capture import stop as stop_monitor
#
#         stop_monitor()
#         click.secho("Monitoring stopped", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @capture.command()
# @click.option(
#     "--session",
#     "-s",
#     help="Session ID (e.g., '20250823_104523'). Use 'latest' for most recent.",
# )
# @click.option("--output", "-o", type=click.Path(), help="Output GIF path")
# @click.option(
#     "--duration",
#     "-d",
#     type=float,
#     default=0.5,
#     help="Duration per frame in seconds (default: 0.5)",
# )
# @click.option("--max-frames", type=int, help="Maximum number of frames to include")
# @click.option(
#     "--pattern", "-p", help="Glob pattern for images (alternative to session)"
# )
# def gif(session, output, duration, max_frames, pattern):
#     """
#     Create animated GIF from screenshots
#
#     \b
#     Examples:
#       scitex capture gif                         # From latest session
#       scitex capture gif --session 20250823_104523
#       scitex capture gif --duration 0.3 --max-frames 50
#       scitex capture gif --pattern "./screenshots/*.jpg"
#     """
#     try:
#         if pattern:
#             from scitex.capture import create_gif_from_pattern
#
#             click.echo(f"Creating GIF from pattern: {pattern}")
#             result = create_gif_from_pattern(
#                 pattern=pattern,
#                 output_path=output,
#                 duration=duration,
#                 max_frames=max_frames,
#             )
#         elif session:
#             from scitex.capture import create_gif_from_session
#
#             click.echo(f"Creating GIF from session: {session}")
#             result = create_gif_from_session(
#                 session_id=session,
#                 output_path=output,
#                 duration=duration,
#                 max_frames=max_frames,
#             )
#         else:
#             from scitex.capture import create_gif_from_latest_session
#
#             click.echo("Creating GIF from latest session...")
#             result = create_gif_from_latest_session(
#                 output_path=output,
#                 duration=duration,
#                 max_frames=max_frames,
#             )
#
#         if result:
#             click.secho(f"GIF created: {result}", fg="green")
#         else:
#             click.secho("No screenshots found to create GIF", fg="yellow")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @capture.command()
# @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
# def info(as_json):
#     """
#     Display system info (monitors, windows, virtual desktops)
#
#     \b
#     Examples:
#       scitex capture info
#       scitex capture info --json
#     """
#     try:
#         from scitex.capture import get_info
#
#         info_data = get_info()
#
#         if as_json:
#             import json
#
#             click.echo(json.dumps(info_data, indent=2, default=str))
#         else:
#             click.secho("Display Information", fg="cyan", bold=True)
#             click.echo("=" * 50)
#
#             # Monitors
#             monitors = info_data.get("Monitors", {})
#             click.secho(f"\nMonitors ({monitors.get('Count', 0)}):", fg="yellow")
#             for i, mon in enumerate(monitors.get("Details", [])):
#                 primary = " (Primary)" if mon.get("Primary") else ""
#                 click.echo(f"  [{i}] {mon.get('Width')}x{mon.get('Height')}{primary}")
#
#             # Windows
#             windows = info_data.get("Windows", {})
#             click.secho(f"\nWindows ({windows.get('Count', 0)}):", fg="yellow")
#             for win in windows.get("Details", [])[:10]:  # Show first 10
#                 title = win.get("Title", "")[:40]
#                 handle = win.get("Handle", "")
#                 click.echo(f"  [{handle}] {title}")
#             if windows.get("Count", 0) > 10:
#                 click.echo(f"  ... and {windows.get('Count') - 10} more")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @capture.command()
# @click.argument("handle", type=int)
# @click.option("--output", "-o", type=click.Path(), help="Output file path")
# @click.option("--quality", "-q", type=int, default=85, help="JPEG quality 1-100")
# def window(handle, output, quality):
#     """
#     Capture a specific window by its handle
#
#     \b
#     Get window handles with: scitex capture info
#
#     \b
#     Examples:
#       scitex capture window 12345
#       scitex capture window 12345 --output ./window.jpg
#     """
#     try:
#         from scitex.capture import capture_window
#
#         click.echo(f"Capturing window {handle}...")
#         result = capture_window(handle, output)
#
#         if result:
#             click.secho(f"Window captured: {result}", fg="green")
#         else:
#             click.secho("Window captured", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     capture()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/capture.py
# --------------------------------------------------------------------------------
