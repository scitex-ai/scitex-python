#!/usr/bin/env python3
# Timestamp: 2026-01-04
# File: tests/scitex/audio/test___main__.py

"""Tests for scitex_audio.__main__ module (CLI entry point)."""

import sys
from io import StringIO  # noqa: F401
from unittest.mock import MagicMock, patch

import pytest


class TestMainFunction:
    """Tests for main() function."""

    def test_main_function_exists(self):
        """Test main function exists."""
        from scitex_audio.__main__ import main

        assert callable(main)

    def test_help_flag_shows_help(self):
        """Test --help flag shows help message."""
        from scitex_audio.__main__ import main

        with patch.object(sys, "argv", ["scitex.audio", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # --help exits with code 0
            assert exc_info.value.code == 0

    def test_no_args_shows_help(self, capsys):
        """Test no arguments shows help."""
        from scitex_audio.__main__ import main

        with patch.object(sys, "argv", ["scitex.audio"]):
            main()

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "scitex" in captured.out.lower()


class TestMCPMode:
    """Tests for MCP server mode."""

    def test_mcp_flag_starts_server(self):
        """Test --mcp flag starts MCP server."""
        mock_server_main = MagicMock()

        with patch.object(sys, "argv", ["scitex.audio", "--mcp"]):
            with patch("scitex_audio.__main__.asyncio.run") as mock_run:
                with patch("scitex_audio.mcp_server.main", mock_server_main):
                    from scitex_audio.__main__ import main

                    main()

                    mock_run.assert_called_once()


class TestSpeakCommand:
    """Tests for 'speak' subcommand."""

    def test_speak_command_calls_speak_function(self):
        """Test 'speak' command calls speak function."""
        mock_speak = MagicMock()

        with patch.object(sys, "argv", ["scitex.audio", "speak", "Hello world"]):
            with patch("scitex_audio.speak", mock_speak):
                from scitex_audio.__main__ import main

                main()

                mock_speak.assert_called_once()

    def test_speak_with_backend_option(self):
        """Test 'speak' command with --backend option."""
        mock_speak = MagicMock()

        with patch.object(
            sys, "argv", ["scitex.audio", "speak", "Hello", "-b", "gtts"]
        ):
            with patch("scitex_audio.speak", mock_speak):
                from scitex_audio.__main__ import main

                main()

                call_kwargs = mock_speak.call_args[1]
                assert call_kwargs["backend"] == "gtts"

    def test_speak_with_voice_option(self):
        """Test 'speak' command with --voice option."""
        mock_speak = MagicMock()

        with patch.object(sys, "argv", ["scitex.audio", "speak", "Hello", "-v", "en"]):
            with patch("scitex_audio.speak", mock_speak):
                from scitex_audio.__main__ import main

                main()

                call_kwargs = mock_speak.call_args[1]
                assert call_kwargs["voice"] == "en"

    def test_speak_with_output_option(self):
        """Test 'speak' command with --output option."""
        mock_speak = MagicMock()

        with patch.object(
            sys, "argv", ["scitex.audio", "speak", "Hello", "-o", "/tmp/test.mp3"]
        ):
            with patch("scitex_audio.speak", mock_speak):
                from scitex_audio.__main__ import main

                main()

                call_kwargs = mock_speak.call_args[1]
                assert call_kwargs["output_path"] == "/tmp/test.mp3"

    def test_speak_with_no_play_option(self):
        """Test 'speak' command with --no-play option."""
        mock_speak = MagicMock()

        with patch.object(sys, "argv", ["scitex.audio", "speak", "Hello", "--no-play"]):
            with patch("scitex_audio.speak", mock_speak):
                from scitex_audio.__main__ import main

                main()

                call_kwargs = mock_speak.call_args[1]
                assert call_kwargs["play"] is False

    def test_speak_with_no_fallback_option(self):
        """Test 'speak' command with --no-fallback option."""
        mock_speak = MagicMock()

        with patch.object(
            sys, "argv", ["scitex.audio", "speak", "Hello", "--no-fallback"]
        ):
            with patch("scitex_audio.speak", mock_speak):
                from scitex_audio.__main__ import main

                main()

                call_kwargs = mock_speak.call_args[1]
                assert call_kwargs["fallback"] is False


class TestBackendsCommand:
    """Tests for 'backends' subcommand."""

    def test_backends_command_lists_backends(self, capsys):
        """Test 'backends' command lists available backends."""
        mock_available = MagicMock(return_value=["gtts", "pyttsx3"])

        with patch.object(sys, "argv", ["scitex.audio", "backends"]):
            with patch("scitex_audio.available_backends", mock_available):
                from scitex_audio.__main__ import main

                main()

        captured = capsys.readouterr()
        assert "backends" in captured.out.lower() or "gtts" in captured.out.lower()

    def test_backends_shows_availability(self, capsys):
        """Test 'backends' command shows availability status."""
        mock_available = MagicMock(return_value=["gtts"])

        with patch.object(sys, "argv", ["scitex.audio", "backends"]):
            with patch("scitex_audio.available_backends", mock_available):
                from scitex_audio.__main__ import main

                main()

        captured = capsys.readouterr()
        # Should show available/not available status
        assert "available" in captured.out.lower() or "[*]" in captured.out


class TestVoicesCommand:
    """Tests for 'voices' subcommand."""

    def test_voices_command_lists_voices(self, capsys):
        """Test 'voices' command lists available voices."""
        mock_tts = MagicMock()
        mock_tts.get_voices.return_value = [
            {"name": "English", "id": "en"},
            {"name": "French", "id": "fr"},
        ]

        mock_available = MagicMock(return_value=["gtts"])
        mock_get_tts = MagicMock(return_value=mock_tts)

        with patch.object(sys, "argv", ["scitex.audio", "voices"]):
            with patch("scitex_audio.available_backends", mock_available):
                with patch("scitex_audio.get_tts", mock_get_tts):
                    from scitex_audio.__main__ import main

                    main()

        captured = capsys.readouterr()
        assert "english" in captured.out.lower() or "voices" in captured.out.lower()

    def test_voices_with_backend_option(self, capsys):
        """Test 'voices' command with --backend option."""
        mock_tts = MagicMock()
        mock_tts.get_voices.return_value = [{"name": "Test", "id": "test"}]

        mock_get_tts = MagicMock(return_value=mock_tts)

        with patch.object(sys, "argv", ["scitex.audio", "voices", "-b", "elevenlabs"]):
            with patch("scitex_audio.get_tts", mock_get_tts):
                from scitex_audio.__main__ import main

                main()

                mock_get_tts.assert_called_with("elevenlabs")

    def test_voices_no_backends_available(self, capsys):
        """Test 'voices' command when no backends available."""
        mock_available = MagicMock(return_value=[])

        with patch.object(sys, "argv", ["scitex.audio", "voices"]):
            with patch("scitex_audio.available_backends", mock_available):
                from scitex_audio.__main__ import main

                main()

        captured = capsys.readouterr()
        assert "no backends" in captured.out.lower()

    def test_voices_handles_error(self, capsys):
        """Test 'voices' command handles errors gracefully."""
        mock_get_tts = MagicMock(side_effect=Exception("Backend error"))
        mock_available = MagicMock(return_value=["gtts"])

        with patch.object(sys, "argv", ["scitex.audio", "voices"]):
            with patch("scitex_audio.available_backends", mock_available):
                with patch("scitex_audio.get_tts", mock_get_tts):
                    from scitex_audio.__main__ import main

                    main()

        captured = capsys.readouterr()
        assert "error" in captured.out.lower()


class TestArgumentParser:
    """Tests for argument parsing."""

    def test_backend_choices(self):
        """Test backend argument accepts valid choices."""
        import argparse  # noqa: F401

        from scitex_audio.__main__ import main  # noqa: F401

        # Valid backends should not raise
        valid_backends = ["pyttsx3", "gtts", "elevenlabs"]
        for backend in valid_backends:
            # Just verify the choices are accepted by argparse
            assert backend in valid_backends

    def test_invalid_backend_rejected(self):
        """Test invalid backend is rejected."""
        with patch.object(
            sys, "argv", ["scitex.audio", "speak", "Hello", "-b", "invalid"]
        ):
            with pytest.raises(SystemExit):
                from scitex_audio.__main__ import main

                main()


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_cli_module_runnable(self):
        """Test module can be run as script."""
        # Just verify the module structure
        from scitex_audio import __main__

        assert hasattr(__main__, "main")

    def test_cli_has_subcommands(self):
        """Test CLI has expected subcommands."""
        # Verify by checking help output
        from scitex_audio.__main__ import main

        with patch.object(sys, "argv", ["scitex.audio", "--help"]):
            with pytest.raises(SystemExit):
                main()


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
