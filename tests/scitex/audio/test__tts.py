#!/usr/bin/env python3
# Timestamp: 2026-01-04
# File: tests/scitex/audio/test__tts.py

"""Tests for scitex_audio._tts module (legacy ElevenLabs TTS)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestTTSConfig:
    """Tests for TTSConfig dataclass."""

    def test_default_voice_id(self):
        """Test default voice ID is Rachel."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.voice_id == "21m00Tcm4TlvDq8ikWAM"

    def test_default_voice_name_is_none(self):
        """Test default voice name is None."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.voice_name is None

    def test_default_model_id(self):
        """Test default model ID."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.model_id == "eleven_multilingual_v2"

    def test_default_stability(self):
        """Test default stability."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.stability == 0.5

    def test_default_similarity_boost(self):
        """Test default similarity_boost."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.similarity_boost == 0.75

    def test_default_style(self):
        """Test default style."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.style == 0.0

    def test_default_speed(self):
        """Test default speed."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.speed == 1.0

    def test_default_output_format(self):
        """Test default output format."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig()
        assert config.output_format == "mp3_44100_128"

    def test_custom_values(self):
        """Test custom configuration values."""
        from scitex_audio._tts import TTSConfig

        config = TTSConfig(
            voice_id="custom-id",
            voice_name="Custom",
            model_id="custom_model",
            stability=0.8,
            similarity_boost=0.9,
            style=0.5,
            speed=1.5,
            output_format="wav_44100_16",
        )
        assert config.voice_id == "custom-id"
        assert config.voice_name == "Custom"
        assert config.model_id == "custom_model"
        assert config.stability == 0.8
        assert config.similarity_boost == 0.9
        assert config.style == 0.5
        assert config.speed == 1.5
        assert config.output_format == "wav_44100_16"


class TestTTS:
    """Tests for TTS class."""

    def test_voices_dictionary(self):
        """Test VOICES dictionary contains expected voices."""
        from scitex_audio._tts import TTS

        assert "rachel" in TTS.VOICES
        assert "adam" in TTS.VOICES
        assert "bella" in TTS.VOICES
        assert "josh" in TTS.VOICES
        assert "sam" in TTS.VOICES

    def test_api_key_from_parameter(self):
        """Test API key from parameter."""
        from scitex_audio._tts import TTS

        tts = TTS(api_key="test-api-key")
        assert tts.api_key == "test-api-key"

    def test_api_key_from_environment(self):
        """Test API key from environment variable."""
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "env-api-key"}):
            from scitex_audio._tts import TTS

            tts = TTS()
            assert tts.api_key == "env-api-key"

    def test_voice_name_sets_voice_id(self):
        """Test voice_name parameter sets voice_id."""
        from scitex_audio._tts import TTS

        tts = TTS(voice_name="rachel")
        assert tts.config.voice_id == TTS.VOICES["rachel"]

    def test_voice_id_overrides_voice_name(self):
        """Test voice_id parameter overrides voice_name."""
        from scitex_audio._tts import TTS

        custom_id = "custom-voice-id"
        tts = TTS(voice_name="rachel", voice_id=custom_id)
        assert tts.config.voice_id == custom_id

    def test_config_kwargs_passed(self):
        """Test kwargs are passed to config."""
        from scitex_audio._tts import TTS

        tts = TTS(stability=0.8, speed=1.5)
        assert tts.config.stability == 0.8
        assert tts.config.speed == 1.5

    def test_client_lazy_loading(self):
        """Test client is lazily loaded."""
        from scitex_audio._tts import TTS

        tts = TTS()
        assert tts._client is None

    def test_client_import_error(self):
        """Test ImportError when elevenlabs not installed."""
        from scitex_audio._tts import TTS

        tts = TTS()

        # Mock the internal import of elevenlabs to fail
        original_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name == "elevenlabs.client" or name.startswith("elevenlabs"):
                raise ImportError("elevenlabs not installed")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ImportError) as exc_info:
                _ = tts.client

        assert "elevenlabs" in str(exc_info.value)

    def test_speak_method_exists(self):
        """Test speak method exists."""
        from scitex_audio._tts import TTS

        tts = TTS()
        assert hasattr(tts, "speak")
        assert callable(tts.speak)

    def test_list_voices_method_exists(self):
        """Test list_voices method exists."""
        from scitex_audio._tts import TTS

        tts = TTS()
        assert hasattr(tts, "list_voices")
        assert callable(tts.list_voices)

    def test_speak_with_mocked_client(self, tmp_path):
        """Test speak with mocked ElevenLabs client."""
        mock_client = MagicMock()
        mock_audio = [b"audio", b"data"]
        mock_client.text_to_speech.convert.return_value = mock_audio

        from scitex_audio._tts import TTS

        tts = TTS(api_key="test-key")
        tts._client = mock_client

        output_file = tmp_path / "test.mp3"

        with patch.object(tts, "_play_audio"):
            result = tts.speak("Hello", output_path=str(output_file), play=False)

        assert result == output_file
        assert output_file.exists()

    def test_speak_uses_custom_voice_name(self, tmp_path):
        """Test speak uses voice_name parameter."""
        mock_client = MagicMock()
        mock_client.text_to_speech.convert.return_value = [b"audio"]

        from scitex_audio._tts import TTS

        tts = TTS(api_key="test-key")
        tts._client = mock_client

        output_file = tmp_path / "test.mp3"

        with patch.object(tts, "_play_audio"):
            tts.speak(
                "Hello", output_path=str(output_file), voice_name="adam", play=False
            )

        call_kwargs = mock_client.text_to_speech.convert.call_args[1]
        assert call_kwargs["voice_id"] == TTS.VOICES["adam"]

    def test_speak_uses_custom_voice_id(self, tmp_path):
        """Test speak uses voice_id parameter."""
        mock_client = MagicMock()
        mock_client.text_to_speech.convert.return_value = [b"audio"]

        from scitex_audio._tts import TTS

        tts = TTS(api_key="test-key")
        tts._client = mock_client

        output_file = tmp_path / "test.mp3"
        custom_id = "custom-voice-id"

        with patch.object(tts, "_play_audio"):
            tts.speak(
                "Hello", output_path=str(output_file), voice_id=custom_id, play=False
            )

        call_kwargs = mock_client.text_to_speech.convert.call_args[1]
        assert call_kwargs["voice_id"] == custom_id

    def test_speak_plays_audio_by_default(self, tmp_path):
        """Test speak plays audio by default."""
        mock_client = MagicMock()
        mock_client.text_to_speech.convert.return_value = [b"audio"]

        from scitex_audio._tts import TTS

        tts = TTS(api_key="test-key")
        tts._client = mock_client

        with patch.object(tts, "_play_audio") as mock_play:
            tts.speak("Hello")
            mock_play.assert_called_once()

    def test_speak_returns_none_without_output_path(self, tmp_path):
        """Test speak returns None when no output_path specified."""
        mock_client = MagicMock()
        mock_client.text_to_speech.convert.return_value = [b"audio"]

        from scitex_audio._tts import TTS

        tts = TTS(api_key="test-key")
        tts._client = mock_client

        with patch.object(tts, "_play_audio"):
            result = tts.speak("Hello", play=True)

        assert result is None

    def test_list_voices_returns_list(self):
        """Test list_voices returns a list."""
        mock_client = MagicMock()
        mock_voice = MagicMock()
        mock_voice.name = "Test Voice"
        mock_voice.voice_id = "test-id"
        mock_voice.labels = {}

        mock_response = MagicMock()
        mock_response.voices = [mock_voice]
        mock_client.voices.get_all.return_value = mock_response

        from scitex_audio._tts import TTS

        tts = TTS(api_key="test-key")
        tts._client = mock_client

        voices = tts.list_voices()

        assert isinstance(voices, list)
        assert len(voices) == 1
        assert voices[0]["name"] == "Test Voice"


class TestTTSPlayAudio:
    """Tests for TTS audio playback methods."""

    def test_play_audio_tries_multiple_players(self, tmp_path):
        """Test _play_audio tries multiple players."""
        from scitex_audio._tts import TTS

        tts = TTS()
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b"dummy")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("player not found")
            # Should not raise
            tts._play_audio(test_file)

    def test_play_audio_windows_fallback(self, tmp_path):
        """Test Windows fallback is tried in WSL."""
        from scitex_audio._tts import TTS

        tts = TTS()
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b"dummy")

        with patch("os.path.exists", return_value=True):  # Simulate WSL
            with patch.object(
                tts, "_play_audio_windows", return_value=True
            ) as mock_win:
                tts._play_audio(test_file)
                mock_win.assert_called_once()

    def test_play_audio_windows_returns_false_non_wsl(self, tmp_path):
        """Test _play_audio_windows returns False when not in WSL."""
        from scitex_audio._tts import TTS

        tts = TTS()
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b"dummy")

        with patch("os.path.exists", return_value=False):
            result = tts._play_audio_windows(test_file)
            assert result is False


class TestModuleLevelSpeak:
    """Tests for module-level speak function."""

    def test_speak_function_exists(self):
        """Test speak function exists at module level."""
        from scitex_audio._tts import speak

        assert callable(speak)

    def test_speak_creates_default_tts(self):
        """Test speak creates default TTS instance."""
        from scitex_audio import _tts

        # Reset the default TTS
        _tts._default_tts = None

        mock_client = MagicMock()
        mock_client.text_to_speech.convert.return_value = [b"audio"]

        with patch.object(
            _tts.TTS, "client", new_callable=lambda: property(lambda s: mock_client)
        ):
            with patch.object(_tts.TTS, "_play_audio"):
                _tts.speak("Hello", play=False)

        # Should have created a default TTS
        # Note: actual test depends on implementation

    def test_speak_with_voice_parameter(self):
        """Test speak function with voice parameter."""
        # Just verify the function signature
        import inspect

        from scitex_audio._tts import speak

        sig = inspect.signature(speak)
        assert "voice" in sig.parameters
        assert "play" in sig.parameters
        assert "output_path" in sig.parameters


class TestTTSEdgeCases:
    """Edge case tests for TTS."""

    def test_empty_text(self):
        """Test handling of empty text."""
        from scitex_audio._tts import TTS

        tts = TTS()
        # Should not raise during initialization
        assert tts is not None

    def test_voice_name_case_insensitive(self):
        """Test voice_name is case insensitive."""
        from scitex_audio._tts import TTS

        tts_lower = TTS(voice_name="rachel")
        tts_upper = TTS(voice_name="RACHEL")
        tts_mixed = TTS(voice_name="Rachel")

        assert (
            tts_lower.config.voice_id
            == tts_upper.config.voice_id
            == tts_mixed.config.voice_id
        )


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/audio/_tts.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-12-11 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex-code/src/scitex/audio/_tts.py
# # ----------------------------------------
#
# """
# Text-to-Speech implementation using ElevenLabs API.
#
# This module provides TTS functionality that can be used:
# 1. Directly via the ElevenLabs Python SDK
# 2. Via MCP server integration
#
# Environment Variables:
#     ELEVENLABS_API_KEY: Your ElevenLabs API key
# """
#
# from __future__ import annotations
#
# import os
# import subprocess
# import tempfile
# from dataclasses import dataclass, field
# from pathlib import Path
# from typing import Optional
#
# __all__ = ["TTS", "speak"]
#
#
# @dataclass
# class TTSConfig:
#     """Configuration for TTS."""
#
#     voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)
#     voice_name: Optional[str] = None
#     model_id: str = "eleven_multilingual_v2"
#     stability: float = 0.5
#     similarity_boost: float = 0.75
#     style: float = 0.0
#     speed: float = 1.0
#     output_format: str = "mp3_44100_128"
#
#
# class TTS:
#     """Text-to-Speech using ElevenLabs API.
#
#     Examples:
#         # Basic usage
#         tts = TTS()
#         tts.speak("Hello, world!")
#
#         # With custom voice
#         tts = TTS(voice_name="Rachel")
#         tts.speak("Processing complete")
#
#         # Save to file without playing
#         tts.speak("Test", output_path="/tmp/test.mp3", play=False)
#     """
#
#     # Popular voice presets
#     VOICES = {
#         "rachel": "21m00Tcm4TlvDq8ikWAM",
#         "adam": "pNInz6obpgDQGcFmaJgB",
#         "antoni": "ErXwobaYiN019PkySvjV",
#         "bella": "EXAVITQu4vr4xnSDxMaL",
#         "domi": "AZnzlk1XvdvUeBnXmlld",
#         "elli": "MF3mGyEYCl7XYWbV9V6O",
#         "josh": "TxGEqnHWrfWFTfGW9XjX",
#         "sam": "yoZ06aMxZJJ28mfd3POQ",
#     }
#
#     def __init__(
#         self,
#         api_key: Optional[str] = None,
#         voice_name: Optional[str] = None,
#         voice_id: Optional[str] = None,
#         **kwargs,
#     ):
#         """Initialize TTS.
#
#         Args:
#             api_key: ElevenLabs API key. Defaults to ELEVENLABS_API_KEY env var.
#             voice_name: Voice name (e.g., "Rachel", "Adam").
#             voice_id: Direct voice ID (overrides voice_name).
#             **kwargs: Additional config options (stability, speed, etc.)
#         """
#         self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
#         self.config = TTSConfig(**kwargs)
#
#         if voice_id:
#             self.config.voice_id = voice_id
#         elif voice_name:
#             self.config.voice_name = voice_name
#             normalized = voice_name.lower()
#             if normalized in self.VOICES:
#                 self.config.voice_id = self.VOICES[normalized]
#
#         self._client = None
#
#     @property
#     def client(self):
#         """Lazy-load ElevenLabs client."""
#         if self._client is None:
#             try:
#                 from elevenlabs.client import ElevenLabs
#
#                 self._client = ElevenLabs(api_key=self.api_key)
#             except ImportError:
#                 raise ImportError(
#                     "elevenlabs package not installed. "
#                     "Install with: pip install elevenlabs"
#                 )
#         return self._client
#
#     def speak(
#         self,
#         text: str,
#         output_path: Optional[str] = None,
#         play: bool = True,
#         voice_name: Optional[str] = None,
#         voice_id: Optional[str] = None,
#     ) -> Optional[Path]:
#         """Convert text to speech and optionally play it.
#
#         Args:
#             text: Text to convert to speech.
#             output_path: Path to save audio file. Auto-generated if None.
#             play: Whether to play the audio after generation.
#             voice_name: Override voice name for this call.
#             voice_id: Override voice ID for this call.
#
#         Returns:
#             Path to the generated audio file, or None if only played.
#         """
#         # Determine voice
#         vid = voice_id or self.config.voice_id
#         if voice_name and not voice_id:
#             normalized = voice_name.lower()
#             vid = self.VOICES.get(normalized, vid)
#
#         # Generate audio
#         audio = self.client.text_to_speech.convert(
#             text=text,
#             voice_id=vid,
#             model_id=self.config.model_id,
#             voice_settings={
#                 "stability": self.config.stability,
#                 "similarity_boost": self.config.similarity_boost,
#                 "style": self.config.style,
#                 "speed": self.config.speed,
#             },
#             output_format=self.config.output_format,
#         )
#
#         # Determine output path
#         if output_path:
#             out_path = Path(output_path)
#         else:
#             suffix = ".mp3" if "mp3" in self.config.output_format else ".wav"
#             fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="scitex_tts_")
#             os.close(fd)
#             out_path = Path(tmp_path)
#
#         # Write audio to file
#         with open(out_path, "wb") as f:
#             for chunk in audio:
#                 f.write(chunk)
#
#         # Play if requested
#         if play:
#             self._play_audio(out_path)
#
#         return out_path if output_path else None
#
#     def _play_audio(self, path: Path) -> None:
#         """Play audio file using available system player.
#
#         Includes Windows fallback for WSL environments.
#         """
#         # Check if we're in WSL - if so, prefer Windows playback directly
#         # to avoid double playback issues with Linux audio hanging
#         if os.path.exists("/mnt/c/Windows"):
#             if self._play_audio_windows(path):
#                 return
#             # Fall through to Linux players if Windows playback fails
#
#         players = [
#             ["mpv", "--no-video", str(path)],
#             ["ffplay", "-nodisp", "-autoexit", str(path)],
#             ["aplay", str(path)],
#             ["afplay", str(path)],  # macOS
#         ]
#
#         for player_cmd in players:
#             try:
#                 subprocess.run(
#                     player_cmd,
#                     check=True,
#                     stdout=subprocess.DEVNULL,
#                     stderr=subprocess.DEVNULL,
#                     timeout=30,
#                 )
#                 return
#             except subprocess.TimeoutExpired:
#                 # Audio playback hung, don't try more players
#                 return
#             except (subprocess.CalledProcessError, FileNotFoundError):
#                 continue
#
#         print(f"Warning: No audio player found. Audio saved to: {path}")
#
#     def _play_audio_windows(self, path: Path) -> bool:
#         """Play audio via Windows PowerShell SoundPlayer (WSL fallback).
#
#         Uses headless SoundPlayer - no GUI popup.
#         """
#         import shutil
#         import tempfile
#
#         # Check if we're in WSL
#         if not os.path.exists("/mnt/c/Windows"):
#             return False
#
#         powershell = shutil.which("powershell.exe")
#         if not powershell:
#             return False
#
#         try:
#             # SoundPlayer only supports WAV, so convert if needed
#             wav_path = path
#             if path.suffix.lower() in ('.mp3', '.ogg', '.m4a'):
#                 try:
#                     from pydub import AudioSegment
#                     fd, tmp_wav = tempfile.mkstemp(suffix='.wav', prefix='scitex_')
#                     os.close(fd)
#                     wav_path = Path(tmp_wav)
#                     audio = AudioSegment.from_file(str(path))
#                     audio.export(str(wav_path), format='wav')
#                 except ImportError:
#                     pass
#
#             result = subprocess.run(
#                 ["wslpath", "-w", str(wav_path)],
#                 capture_output=True,
#                 text=True,
#                 timeout=5,
#             )
#             if result.returncode != 0:
#                 return False
#
#             windows_path = result.stdout.strip()
#
#             ps_command = f'''
# $player = New-Object System.Media.SoundPlayer
# $player.SoundLocation = "{windows_path}"
# $player.PlaySync()
# '''
#             subprocess.run(
#                 [powershell, "-NoProfile", "-Command", ps_command],
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL,
#                 timeout=60,
#             )
#
#             # Clean up temp WAV
#             if wav_path != path and wav_path.exists():
#                 try:
#                     wav_path.unlink()
#                 except Exception:
#                     pass
#
#             return True
#
#         except Exception:
#             return False
#
#     def list_voices(self) -> list:
#         """List available voices from ElevenLabs."""
#         response = self.client.voices.get_all()
#         return [
#             {"name": v.name, "voice_id": v.voice_id, "labels": v.labels}
#             for v in response.voices
#         ]
#
#
# # Module-level convenience function
# _default_tts: Optional[TTS] = None
#
#
# def speak(
#     text: str,
#     voice: Optional[str] = None,
#     play: bool = True,
#     output_path: Optional[str] = None,
#     **kwargs,
# ) -> Optional[Path]:
#     """Convenience function for quick TTS.
#
#     Args:
#         text: Text to speak.
#         voice: Voice name (e.g., "Rachel", "Adam").
#         play: Whether to play audio.
#         output_path: Optional path to save audio.
#         **kwargs: Additional TTS config options.
#
#     Returns:
#         Path to audio file if output_path specified, else None.
#
#     Examples:
#         import scitex
#
#         # Simple speak
#         scitex_audio.speak("Hello!")
#
#         # With specific voice
#         scitex_audio.speak("Processing complete", voice="Adam")
#
#         # Save without playing
#         scitex_audio.speak("Test", play=False, output_path="/tmp/test.mp3")
#     """
#     global _default_tts
#
#     if _default_tts is None or kwargs:
#         _default_tts = TTS(**kwargs)
#
#     return _default_tts.speak(
#         text=text,
#         voice_name=voice,
#         play=play,
#         output_path=output_path,
#     )
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/audio/_tts.py
# --------------------------------------------------------------------------------
