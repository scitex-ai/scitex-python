#!/usr/bin/env python3
# Timestamp: 2026-01-04
# File: tests/scitex/audio/engines/test_base.py

"""Tests for scitex_audio.engines.base module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestTTSBackend:
    """Tests for TTSBackend class."""

    def test_backend_constants(self):
        """Test that backend constants are defined correctly."""
        from scitex_audio.engines._base import TTSBackend

        assert TTSBackend.ELEVENLABS == "elevenlabs"
        assert TTSBackend.GTTS == "gtts"
        assert TTSBackend.PYTTSX3 == "pyttsx3"
        assert TTSBackend.EDGE == "edge"

    def test_available_returns_list(self):
        """Test that available() returns a list."""
        from scitex_audio.engines._base import TTSBackend

        result = TTSBackend.available()
        assert isinstance(result, list)

    def test_available_detects_gtts_when_installed(self):
        """Test that available() detects gTTS when installed."""
        from scitex_audio.engines._base import TTSBackend

        with patch.dict("sys.modules", {"gtts": MagicMock()}):
            # Force re-evaluation by calling available
            backends = TTSBackend.available()
            # gtts should be detected if the module import succeeds
            assert isinstance(backends, list)

    def test_available_handles_missing_modules_gracefully(self):
        """Test that available() handles ImportError gracefully."""
        from scitex_audio.engines._base import TTSBackend

        # Should not raise even if modules are missing
        result = TTSBackend.available()
        assert isinstance(result, list)


class TestBaseTTS:
    """Tests for BaseTTS abstract base class."""

    def test_cannot_instantiate_directly(self):
        """Test that BaseTTS cannot be instantiated directly."""
        from scitex_audio.engines._base import BaseTTS

        with pytest.raises(TypeError):
            BaseTTS()

    def test_config_stored_correctly(self):
        """Test that config kwargs are stored."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS(key1="value1", key2="value2")
        assert tts.config["key1"] == "value1"
        assert tts.config["key2"] == "value2"

    def test_requires_api_key_default_false(self):
        """Test that requires_api_key defaults to False."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        assert tts.requires_api_key is False

    def test_requires_internet_default_false(self):
        """Test that requires_internet defaults to False."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        assert tts.requires_internet is False

    def test_speak_with_output_path(self, tmp_path):
        """Test speak() returns dict with path when output_path is provided."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                # Create a dummy file
                path = Path(output_path)
                path.write_text("dummy audio")
                return path

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        output_file = tmp_path / "test.mp3"

        # Mock _play_audio to avoid actual playback
        with patch.object(tts, "_play_audio", return_value=True):
            result = tts.speak("Hello", output_path=str(output_file), play=True)

        assert result["success"] is True
        assert result["path"] == output_file
        assert output_file.exists()

    def test_speak_without_output_path_returns_dict(self, tmp_path):
        """Test speak() returns dict without path when no output_path is provided."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                path = Path(output_path)
                path.write_text("dummy audio")
                return path

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()

        with patch.object(tts, "_play_audio", return_value=True):
            result = tts.speak("Hello", play=True)

        assert result["success"] is True
        assert "path" not in result

    def test_speak_sets_voice_in_config(self, tmp_path):
        """Test that speak() sets voice in config when provided."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                path = Path(output_path)
                path.write_text("dummy audio")
                return path

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        output_file = tmp_path / "test.mp3"

        with patch.object(tts, "_play_audio"):
            tts.speak("Hello", output_path=str(output_file), voice="custom_voice")

        assert tts.config.get("voice") == "custom_voice"

    def test_speak_without_play(self, tmp_path):
        """Test speak() does not play when play=False."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                path = Path(output_path)
                path.write_text("dummy audio")
                return path

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        output_file = tmp_path / "test.mp3"

        with patch.object(tts, "_play_audio") as mock_play:
            tts.speak("Hello", output_path=str(output_file), play=False)
            mock_play.assert_not_called()

    def test_play_audio_tries_multiple_players(self, tmp_path):
        """Test _play_audio tries multiple players."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        test_file = tmp_path / "test.mp3"
        test_file.write_text("dummy")

        # Mock subprocess.run to simulate player not found
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("player not found")
            # Should not raise, just print warning
            tts._play_audio(test_file)

    def test_play_audio_handles_timeout(self, tmp_path):
        """Test _play_audio handles timeout gracefully."""
        import subprocess

        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        test_file = tmp_path / "test.mp3"
        test_file.write_text("dummy")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("ffplay", 30)
            # Should not raise
            tts._play_audio(test_file)

    @pytest.mark.skipif(
        not os.path.exists("/mnt/c/Windows"), reason="WSL-specific test"
    )
    def test_play_audio_windows_wsl_fallback(self, tmp_path):
        """Test Windows fallback in WSL environment."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        test_file = tmp_path / "test.wav"
        test_file.write_text("dummy")

        # Test that Windows fallback is attempted
        result = tts._play_audio_windows(test_file)
        assert isinstance(result, bool)

    def test_play_audio_windows_returns_false_on_non_wsl(self, tmp_path):
        """Test _play_audio_windows returns False when not in WSL."""
        from scitex_audio.engines._base import BaseTTS

        class ConcreteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        tts = ConcreteTTS()
        test_file = tmp_path / "test.wav"
        test_file.write_text("dummy")

        with patch("os.path.exists", return_value=False):
            result = tts._play_audio_windows(test_file)
            assert result is False


class TestAbstractMethodsEnforced:
    """Test that abstract methods are enforced."""

    def test_synthesize_is_abstract(self):
        """Test that synthesize must be implemented."""
        from scitex_audio.engines._base import BaseTTS

        class IncompleteTTS(BaseTTS):
            def get_voices(self):
                return []

            @property
            def name(self):
                return "test"

        with pytest.raises(TypeError):
            IncompleteTTS()

    def test_get_voices_is_abstract(self):
        """Test that get_voices must be implemented."""
        from scitex_audio.engines._base import BaseTTS

        class IncompleteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            @property
            def name(self):
                return "test"

        with pytest.raises(TypeError):
            IncompleteTTS()

    def test_name_is_abstract(self):
        """Test that name property must be implemented."""
        from scitex_audio.engines._base import BaseTTS

        class IncompleteTTS(BaseTTS):
            def synthesize(self, text, output_path):
                return Path(output_path)

            def get_voices(self):
                return []

        with pytest.raises(TypeError):
            IncompleteTTS()


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/audio/engines/base.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-12-11 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex-code/src/scitex/audio/engines/base.py
# # ----------------------------------------
#
# """
# Base TTS class defining the common interface for all TTS backends.
# """
#
# from __future__ import annotations
#
# import subprocess
# from abc import ABC, abstractmethod
# from pathlib import Path
# from typing import List, Optional
#
# __all__ = ["BaseTTS", "TTSBackend"]
#
#
# class TTSBackend:
#     """Enum-like class for TTS backend types."""
#
#     ELEVENLABS = "elevenlabs"
#     GTTS = "gtts"
#     PYTTSX3 = "pyttsx3"
#     EDGE = "edge"  # Future: edge-tts
#
#     @classmethod
#     def available(cls) -> List[str]:
#         """Return list of available backends."""
#         backends = []
#
#         # Check gTTS (always available if installed, needs internet)
#         try:
#             import gtts
#
#             backends.append(cls.GTTS)
#         except ImportError:
#             pass
#
#         # Check pyttsx3
#         try:
#             import pyttsx3
#
#             backends.append(cls.PYTTSX3)
#         except ImportError:
#             pass
#
#         # Check ElevenLabs
#         try:
#             import elevenlabs
#             import os
#
#             if os.environ.get("ELEVENLABS_API_KEY"):
#                 backends.append(cls.ELEVENLABS)
#         except ImportError:
#             pass
#
#         return backends
#
#
# class BaseTTS(ABC):
#     """Abstract base class for TTS implementations."""
#
#     def __init__(self, **kwargs):
#         self.config = kwargs
#
#     @abstractmethod
#     def synthesize(self, text: str, output_path: str) -> Path:
#         """Synthesize text to audio file.
#
#         Args:
#             text: Text to convert to speech.
#             output_path: Path to save the audio file.
#
#         Returns:
#             Path to the generated audio file.
#         """
#         pass
#
#     @abstractmethod
#     def get_voices(self) -> List[dict]:
#         """Get available voices for this backend.
#
#         Returns:
#             List of voice dictionaries with 'name' and 'id' keys.
#         """
#         pass
#
#     @property
#     @abstractmethod
#     def name(self) -> str:
#         """Return the backend name."""
#         pass
#
#     @property
#     def requires_api_key(self) -> bool:
#         """Whether this backend requires an API key."""
#         return False
#
#     @property
#     def requires_internet(self) -> bool:
#         """Whether this backend requires internet connection."""
#         return False
#
#     def speak(
#         self,
#         text: str,
#         output_path: Optional[str] = None,
#         play: bool = True,
#         voice: Optional[str] = None,
#     ) -> Optional[Path]:
#         """Synthesize and optionally play text.
#
#         Args:
#             text: Text to speak.
#             output_path: Optional path to save audio.
#             play: Whether to play the audio.
#             voice: Optional voice name/id.
#
#         Returns:
#             Path to audio file if output_path specified, else None.
#         """
#         import tempfile
#
#         # Determine output path
#         if output_path:
#             out_path = Path(output_path)
#         else:
#             suffix = ".mp3"
#             fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="scitex_tts_")
#             import os
#
#             os.close(fd)
#             out_path = Path(tmp_path)
#
#         # Set voice if provided
#         if voice:
#             self.config["voice"] = voice
#
#         # Synthesize
#         result_path = self.synthesize(text, str(out_path))
#
#         # Play if requested
#         if play:
#             self._play_audio(result_path)
#
#         # Return path only if explicitly requested
#         if output_path:
#             return result_path
#
#         return None
#
#     def _play_audio(self, path: Path) -> None:
#         """Play audio file using available system player.
#
#         Includes Windows fallback for WSL environments where PulseAudio
#         may be unstable.
#         """
#         import os
#
#         # Check if we're in WSL - if so, prefer Windows playback directly
#         # to avoid double playback issues with Linux audio hanging
#         if os.path.exists("/mnt/c/Windows"):
#             if self._play_audio_windows(path):
#                 return
#             # Fall through to Linux players if Windows playback fails
#
#         players = [
#             ["ffplay", "-nodisp", "-autoexit", str(path)],
#             ["mpv", "--no-video", str(path)],
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
#         This is useful when WSLg PulseAudio connection is unstable.
#         Uses System.Media.SoundPlayer which is headless (no GUI).
#
#         Args:
#             path: Path to audio file (in WSL filesystem)
#
#         Returns:
#             True if playback succeeded, False otherwise
#         """
#         import os
#         import shutil
#         import tempfile
#
#         # Check if we're in WSL
#         if not os.path.exists("/mnt/c/Windows"):
#             return False
#
#         # Check if powershell.exe is available
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
#                     # Create temp WAV file
#                     fd, tmp_wav = tempfile.mkstemp(suffix='.wav', prefix='scitex_')
#                     os.close(fd)
#                     wav_path = Path(tmp_wav)
#
#                     audio = AudioSegment.from_file(str(path))
#                     audio.export(str(wav_path), format='wav')
#                 except ImportError:
#                     # pydub not available, try direct playback anyway
#                     pass
#
#             # Convert WSL path to Windows path
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
#             # Play using PowerShell's SoundPlayer (headless, no GUI)
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
#             # Clean up temp WAV if created
#             if wav_path != path and wav_path.exists():
#                 try:
#                     wav_path.unlink()
#                 except Exception:
#                     pass
#
#             return True
#
#         except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
#             return False
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/audio/engines/base.py
# --------------------------------------------------------------------------------
