#!/usr/bin/env python3
"""Tests for scitex.cli.audio - Text-to-speech CLI commands."""

import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.audio import audio


class TestAudioGroup:
    """Tests for the audio command group."""

    def test_audio_help(self):
        """Test that audio help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(audio, ["--help"])
        assert result.exit_code == 0
        assert "Text-to-speech utilities" in result.output

    def test_audio_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(audio, ["--help"])
        expected_commands = ["speak", "backends", "check", "stop"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in audio help"


class TestAudioSpeak:
    """Tests for the audio speak command."""

    def test_speak_basic(self):
        """Test basic speak command."""
        runner = CliRunner()
        with patch("scitex.audio.speak") as mock_speak:
            mock_speak.return_value = None
            result = runner.invoke(audio, ["speak", "Hello world"])
            assert result.exit_code == 0
            mock_speak.assert_called_once()
            call_kwargs = mock_speak.call_args[1]
            assert call_kwargs["text"] == "Hello world"
            assert call_kwargs["play"] is True

    def test_speak_with_backend(self):
        """Test speak command with specific backend."""
        runner = CliRunner()
        with patch("scitex.audio.speak") as mock_speak:
            mock_speak.return_value = None
            result = runner.invoke(audio, ["speak", "Test", "--backend", "gtts"])
            assert result.exit_code == 0
            call_kwargs = mock_speak.call_args[1]
            assert call_kwargs["backend"] == "gtts"

    def test_speak_with_voice(self):
        """Test speak command with voice option."""
        runner = CliRunner()
        with patch("scitex.audio.speak") as mock_speak:
            mock_speak.return_value = None
            result = runner.invoke(audio, ["speak", "Bonjour", "--voice", "fr"])
            assert result.exit_code == 0
            call_kwargs = mock_speak.call_args[1]
            assert call_kwargs["voice"] == "fr"

    def test_speak_with_output(self):
        """Test speak command with output file."""
        runner = CliRunner()
        with patch("scitex.audio.speak") as mock_speak:
            mock_speak.return_value = "/tmp/speech.mp3"
            result = runner.invoke(
                audio, ["speak", "Test", "--output", "/tmp/speech.mp3", "--no-play"]
            )
            assert result.exit_code == 0
            call_kwargs = mock_speak.call_args[1]
            assert call_kwargs["output_path"] == "/tmp/speech.mp3"
            assert call_kwargs["play"] is False

    def test_speak_with_rate(self):
        """Test speak command with rate option (pyttsx3)."""
        runner = CliRunner()
        with patch("scitex.audio.speak") as mock_speak:
            mock_speak.return_value = None
            result = runner.invoke(audio, ["speak", "Fast", "--rate", "200"])
            assert result.exit_code == 0
            call_kwargs = mock_speak.call_args[1]
            assert call_kwargs["rate"] == 200

    def test_speak_with_speed(self):
        """Test speak command with speed option (gtts)."""
        runner = CliRunner()
        with patch("scitex.audio.speak") as mock_speak:
            mock_speak.return_value = None
            result = runner.invoke(audio, ["speak", "Slow", "--speed", "0.8"])
            assert result.exit_code == 0
            call_kwargs = mock_speak.call_args[1]
            assert call_kwargs["speed"] == 0.8

    def test_speak_error_handling(self):
        """Test speak command handles errors gracefully."""
        runner = CliRunner()
        with patch("scitex.audio.speak") as mock_speak:
            mock_speak.side_effect = Exception("TTS failed")
            result = runner.invoke(audio, ["speak", "Test"])
            assert result.exit_code == 1
            assert "Error" in result.output


class TestAudioBackends:
    """Tests for the audio backends command."""

    def test_backends_list(self):
        """Test backends list command."""
        runner = CliRunner()
        with patch("scitex.audio.available_backends") as mock_available:
            with patch(
                "scitex.audio.FALLBACK_ORDER", ["pyttsx3", "gtts", "elevenlabs"]
            ):
                mock_available.return_value = ["pyttsx3", "gtts"]
                result = runner.invoke(audio, ["backends"])
                assert result.exit_code == 0
                assert "Available TTS Backends" in result.output
                assert "pyttsx3" in result.output
                assert "gtts" in result.output

    def test_backends_json(self):
        """Test backends list with --json flag."""
        runner = CliRunner()
        with patch("scitex.audio.available_backends") as mock_available:
            with patch("scitex.audio.FALLBACK_ORDER", ["pyttsx3", "gtts"]):
                mock_available.return_value = ["pyttsx3"]
                result = runner.invoke(audio, ["backends", "--json"])
                assert result.exit_code == 0
                import json

                output = json.loads(result.output)
                data = output.get("data", output)
                assert "available" in data
                assert "fallback_order" in data

    def test_backends_no_available(self):
        """Test backends list when none available."""
        runner = CliRunner()
        with patch("scitex.audio.available_backends") as mock_available:
            with patch("scitex.audio.FALLBACK_ORDER", ["pyttsx3", "gtts"]):
                mock_available.return_value = []
                result = runner.invoke(audio, ["backends"])
                assert result.exit_code == 0
                assert "No backends available" in result.output


class TestAudioCheck:
    """Tests for the audio check command."""

    def test_check_default(self):
        """Test audio check command."""
        runner = CliRunner()
        with patch("scitex.audio.check_wsl_audio") as mock_check:
            mock_check.return_value = {
                "is_wsl": True,
                "wslg_available": True,
                "pulse_server_exists": True,
                "pulse_connected": True,
                "windows_fallback_available": True,
                "recommended": "linux",
            }
            result = runner.invoke(audio, ["check"])
            assert result.exit_code == 0
            assert "Audio Status Check" in result.output
            assert "WSL Environment" in result.output

    def test_check_json(self):
        """Test audio check with --json flag."""
        runner = CliRunner()
        with patch("scitex.audio.check_wsl_audio") as mock_check:
            mock_check.return_value = {
                "is_wsl": False,
                "recommended": "linux",
            }
            result = runner.invoke(audio, ["check", "--json"])
            assert result.exit_code == 0
            import json

            output = json.loads(result.output)
            data = output.get("data", output)
            assert "is_wsl" in data
            assert "recommended" in data

    def test_check_non_wsl(self):
        """Test audio check on non-WSL system."""
        runner = CliRunner()
        with patch("scitex.audio.check_wsl_audio") as mock_check:
            mock_check.return_value = {
                "is_wsl": False,
                "recommended": "linux",
            }
            result = runner.invoke(audio, ["check"])
            assert result.exit_code == 0
            # Should show WSL status but not detailed checks
            assert "WSL Environment" in result.output


class TestAudioStop:
    """Tests for the audio stop command."""

    def test_stop(self):
        """Test audio stop command."""
        runner = CliRunner()
        with patch("scitex.audio.stop_speech") as mock_stop:
            result = runner.invoke(audio, ["stop"])
            assert result.exit_code == 0
            assert "Speech stopped" in result.output
            mock_stop.assert_called_once()

    def test_stop_error(self):
        """Test audio stop handles errors."""
        runner = CliRunner()
        with patch("scitex.audio.stop_speech") as mock_stop:
            mock_stop.side_effect = Exception("Failed to stop")
            result = runner.invoke(audio, ["stop"])
            assert result.exit_code == 1
            assert "Error" in result.output


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/audio.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# """
# SciTeX CLI - Audio Commands (Text-to-Speech)
#
# Provides text-to-speech with multiple backend support.
# """
#
# import sys
#
# import click
#
#
# @click.group(context_settings={"help_option_names": ["-h", "--help"]})
# def audio():
#     """
#     Text-to-speech utilities
#
#     \b
#     Backends (fallback order):
#       pyttsx3    - System TTS (offline, free)
#       gtts       - Google TTS (free, needs internet)
#       elevenlabs - ElevenLabs (paid, high quality)
#
#     \b
#     Examples:
#       scitex audio speak "Hello world"
#       scitex audio speak "Bonjour" --backend gtts --voice fr
#       scitex audio backends              # List available backends
#       scitex audio check                 # Check audio status (WSL)
#     """
#     pass
#
#
# @audio.command()
# @click.argument("text")
# @click.option(
#     "--backend",
#     "-b",
#     type=click.Choice(["pyttsx3", "gtts", "elevenlabs"]),
#     help="TTS backend (auto-selects with fallback if not specified)",
# )
# @click.option("--voice", "-v", help="Voice name, ID, or language code")
# @click.option("--output", "-o", type=click.Path(), help="Save audio to file")
# @click.option("--no-play", is_flag=True, help="Don't play audio (only save)")
# @click.option("--rate", "-r", type=int, help="Speech rate (pyttsx3 only, default: 150)")
# @click.option(
#     "--speed", "-s", type=float, help="Speed multiplier (gtts only, e.g., 1.5)"
# )
# @click.option("--no-fallback", is_flag=True, help="Disable backend fallback on error")
# def speak(text, backend, voice, output, no_play, rate, speed, no_fallback):
#     """
#     Convert text to speech
#
#     \b
#     Examples:
#       scitex audio speak "Hello world"
#       scitex audio speak "Bonjour" --backend gtts --voice fr
#       scitex audio speak "Test" --output speech.mp3 --no-play
#       scitex audio speak "Fast speech" --backend pyttsx3 --rate 200
#       scitex audio speak "Slow speech" --backend gtts --speed 0.8
#     """
#     try:
#         from scitex.audio import speak as tts_speak
#
#         kwargs = {
#             "text": text,
#             "play": not no_play,
#             "fallback": not no_fallback,
#         }
#
#         if backend:
#             kwargs["backend"] = backend
#         if voice:
#             kwargs["voice"] = voice
#         if output:
#             kwargs["output_path"] = output
#         if rate:
#             kwargs["rate"] = rate
#         if speed:
#             kwargs["speed"] = speed
#
#         result = tts_speak(**kwargs)
#
#         if output and result:
#             click.secho(f"Audio saved: {result}", fg="green")
#         elif not no_play:
#             click.secho("Speech completed", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @audio.command(name="backends")
# @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
# def list_backends(as_json):
#     """
#     List available TTS backends
#
#     \b
#     Example:
#       scitex audio backends
#       scitex audio backends --json
#     """
#     try:
#         from scitex.audio import FALLBACK_ORDER, available_backends
#
#         backends = available_backends()
#
#         if as_json:
#             import json
#
#             output = {
#                 "available": backends,
#                 "fallback_order": FALLBACK_ORDER,
#             }
#             click.echo(json.dumps(output, indent=2))
#         else:
#             click.secho("Available TTS Backends", fg="cyan", bold=True)
#             click.echo("=" * 40)
#
#             click.echo("\nFallback order:")
#             for i, b in enumerate(FALLBACK_ORDER, 1):
#                 status = (
#                     click.style("available", fg="green")
#                     if b in backends
#                     else click.style("not installed", fg="red")
#                 )
#                 click.echo(f"  {i}. {b}: {status}")
#
#             if not backends:
#                 click.echo()
#                 click.secho("No backends available!", fg="red")
#                 click.echo("Install one of:")
#                 click.echo("  pip install pyttsx3  # + apt install espeak-ng")
#                 click.echo("  pip install gTTS")
#                 click.echo("  pip install elevenlabs")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @audio.command()
# @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
# def check(as_json):
#     """
#     Check audio status (especially for WSL)
#
#     \b
#     Checks:
#       - WSL detection
#       - WSLg availability
#       - PulseAudio connection
#       - Windows fallback availability
#
#     \b
#     Example:
#       scitex audio check
#       scitex audio check --json
#     """
#     try:
#         from scitex.audio import check_wsl_audio
#
#         status = check_wsl_audio()
#
#         if as_json:
#             import json
#
#             click.echo(json.dumps(status, indent=2))
#         else:
#             click.secho("Audio Status Check", fg="cyan", bold=True)
#             click.echo("=" * 40)
#
#             def status_mark(val):
#                 return (
#                     click.style("Yes", fg="green")
#                     if val
#                     else click.style("No", fg="red")
#                 )
#
#             click.echo(f"\nWSL Environment: {status_mark(status['is_wsl'])}")
#
#             if status["is_wsl"]:
#                 click.echo(f"WSLg Available: {status_mark(status['wslg_available'])}")
#                 click.echo(
#                     f"PulseServer Socket: {status_mark(status['pulse_server_exists'])}"
#                 )
#                 click.echo(
#                     f"PulseAudio Connected: {status_mark(status['pulse_connected'])}"
#                 )
#                 click.echo(
#                     f"Windows Fallback: {status_mark(status['windows_fallback_available'])}"
#                 )
#
#             click.echo()
#             rec = status["recommended"]
#             if rec == "linux":
#                 click.secho("Recommended: Linux audio (PulseAudio)", fg="green")
#             elif rec == "windows":
#                 click.secho(
#                     "Recommended: Windows fallback (powershell.exe)", fg="yellow"
#                 )
#             else:
#                 click.secho("No audio output available", fg="red")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @audio.command()
# def stop():
#     """
#     Stop any currently playing speech
#
#     \b
#     Example:
#       scitex audio stop
#     """
#     try:
#         from scitex.audio import stop_speech
#
#         stop_speech()
#         click.secho("Speech stopped", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     audio()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/audio.py
# --------------------------------------------------------------------------------
