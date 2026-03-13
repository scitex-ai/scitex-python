#!/usr/bin/env python3
# Timestamp: 2026-01-04
# File: tests/scitex/audio/engines/test_pyttsx3_engine.py

"""Tests for scitex_audio.engines.pyttsx3_engine module."""

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest


class TestSystemTTS:
    """Tests for SystemTTS class."""

    def test_name_property(self):
        """Test that name returns 'pyttsx3'."""
        with patch("pyttsx3.init"):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            assert tts.name == "pyttsx3"

    def test_default_rate(self):
        """Test default rate is 150 WPM."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS()
        assert tts.rate == 150

    def test_default_volume(self):
        """Test default volume is 1.0."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS()
        assert tts.volume == 1.0

    def test_default_voice_is_none(self):
        """Test default voice is None."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS()
        assert tts.voice is None

    def test_custom_rate_initialization(self):
        """Test initializing with custom rate."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS(rate=200)
        assert tts.rate == 200

    def test_custom_volume_initialization(self):
        """Test initializing with custom volume."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS(volume=0.5)
        assert tts.volume == 0.5

    def test_custom_voice_initialization(self):
        """Test initializing with custom voice."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS(voice="en-us")
        assert tts.voice == "en-us"

    def test_engine_lazy_loading(self):
        """Test engine is lazily loaded."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS()
        # Engine should not be initialized yet
        assert tts._engine is None

    def test_engine_property_initializes_pyttsx3(self):
        """Test engine property initializes pyttsx3."""
        mock_engine = MagicMock()

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            engine = tts.engine

            assert engine is mock_engine
            mock_engine.setProperty.assert_any_call("rate", 150)
            mock_engine.setProperty.assert_any_call("volume", 1.0)

    def test_engine_sets_voice_when_provided(self):
        """Test engine sets voice when provided."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.name = "English"
        mock_voice.id = "en-us"
        mock_engine.getProperty.return_value = [mock_voice]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS(voice="English")
            _ = tts.engine

            # Should have called setProperty with voice
            mock_engine.setProperty.assert_any_call("voice", "en-us")

    def test_engine_import_error_handling(self):
        """Test ImportError is raised when pyttsx3 not installed."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS()

        # Mock the internal import of pyttsx3 to fail
        import importlib

        original_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name == "pyttsx3":
                raise ImportError("pyttsx3 not installed")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ImportError) as exc_info:
                _ = tts.engine

        assert "pyttsx3" in str(exc_info.value)

    def test_inherits_from_base_tts(self):
        """Test that SystemTTS inherits from BaseTTS."""
        from scitex_audio.engines._base import BaseTTS
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        assert issubclass(SystemTTS, BaseTTS)

    def test_synthesize_saves_to_file(self, tmp_path):
        """Test synthesize saves audio to file."""
        mock_engine = MagicMock()

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            output_file = tmp_path / "test.mp3"

            result = tts.synthesize("Hello world", str(output_file))

            mock_engine.save_to_file.assert_called_once_with(
                "Hello world", str(output_file)
            )
            mock_engine.runAndWait.assert_called_once()
            assert result == output_file

    def test_synthesize_uses_voice_from_config(self, tmp_path):
        """Test synthesize uses voice from config."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.name = "English"
        mock_voice.id = "en-us"
        mock_engine.getProperty.return_value = [mock_voice]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            tts.config["voice"] = "English"
            output_file = tmp_path / "test.mp3"

            tts.synthesize("Hello", str(output_file))

            # Voice should be set
            mock_engine.setProperty.assert_called()

    def test_speak_direct_method(self):
        """Test speak_direct speaks without saving to file."""
        mock_engine = MagicMock()

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            tts.speak_direct("Hello world")

            mock_engine.say.assert_called_once_with("Hello world")
            mock_engine.runAndWait.assert_called_once()

    def test_speak_direct_with_voice_config(self):
        """Test speak_direct uses voice from config."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.name = "English"
        mock_voice.id = "en-us"
        mock_engine.getProperty.return_value = [mock_voice]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            tts.config["voice"] = "English"
            tts.speak_direct("Hello")

            mock_engine.say.assert_called_once_with("Hello")

    def test_get_voices_returns_list(self):
        """Test get_voices returns a list of voice dictionaries."""
        mock_engine = MagicMock()
        mock_voice1 = MagicMock()
        mock_voice1.name = "English"
        mock_voice1.id = "en-us"
        mock_voice1.languages = ["en"]

        mock_voice2 = MagicMock()
        mock_voice2.name = "Spanish"
        mock_voice2.id = "es-es"
        mock_voice2.languages = ["es"]

        mock_engine.getProperty.return_value = [mock_voice1, mock_voice2]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            voices = tts.get_voices()

            assert isinstance(voices, list)
            assert len(voices) == 2

            # Check structure
            assert voices[0]["name"] == "English"
            assert voices[0]["id"] == "en-us"
            assert voices[0]["type"] == "system"
            assert voices[0]["languages"] == ["en"]

    def test_get_voices_handles_missing_languages_attr(self):
        """Test get_voices handles voices without languages attribute."""
        mock_engine = MagicMock()
        mock_voice = MagicMock(spec=["name", "id"])  # No languages attr
        mock_voice.name = "Test Voice"
        mock_voice.id = "test-id"
        del mock_voice.languages  # Ensure it's not there

        mock_engine.getProperty.return_value = [mock_voice]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            voices = tts.get_voices()

            assert len(voices) == 1
            assert voices[0]["name"] == "Test Voice"
            assert voices[0]["languages"] == []  # Default empty list

    def test_set_voice_by_name(self):
        """Test _set_voice sets voice by name."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.name = "English Voice"
        mock_voice.id = "en-voice-id"
        mock_engine.getProperty.return_value = [mock_voice]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            tts._set_voice("English")

            mock_engine.setProperty.assert_called_with("voice", "en-voice-id")

    def test_set_voice_by_id(self):
        """Test _set_voice sets voice by exact ID."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.name = "English Voice"
        mock_voice.id = "en-voice-id"
        mock_engine.getProperty.return_value = [mock_voice]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            tts._set_voice("en-voice-id")

            mock_engine.setProperty.assert_called_with("voice", "en-voice-id")

    def test_set_voice_not_found_keeps_default(self):
        """Test _set_voice keeps default when voice not found."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.name = "English Voice"
        mock_voice.id = "en-voice-id"
        mock_engine.getProperty.return_value = [mock_voice]

        with patch("pyttsx3.init", return_value=mock_engine):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            # Access engine to trigger lazy initialization (sets rate, volume)
            _ = tts.engine
            initial_calls = mock_engine.setProperty.call_count
            tts._set_voice("NonExistent Voice")

            # Should not have made additional setProperty calls for voice
            # since the voice was not found in the available voices
            assert mock_engine.setProperty.call_count == initial_calls


class TestSystemTTSEdgeCases:
    """Edge case tests for SystemTTS."""

    def test_espeak_runtime_error_handling(self):
        """Test handling of eSpeak RuntimeError."""
        with patch("pyttsx3.init", side_effect=RuntimeError("eSpeak not installed")):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            with pytest.raises(RuntimeError) as exc_info:
                _ = tts.engine

            assert "espeak" in str(exc_info.value).lower()

    def test_other_runtime_error_propagates(self):
        """Test that non-eSpeak RuntimeErrors propagate."""
        with patch("pyttsx3.init", side_effect=RuntimeError("Some other error")):
            from scitex_audio.engines._pyttsx3_engine import SystemTTS

            tts = SystemTTS()
            with pytest.raises(RuntimeError) as exc_info:
                _ = tts.engine

            assert "other error" in str(exc_info.value).lower()

    def test_volume_boundary_values(self):
        """Test volume at boundary values."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        # Minimum volume
        tts_min = SystemTTS(volume=0.0)
        assert tts_min.volume == 0.0

        # Maximum volume
        tts_max = SystemTTS(volume=1.0)
        assert tts_max.volume == 1.0

    def test_rate_can_be_very_high(self):
        """Test rate can be set to high values."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS(rate=500)
        assert tts.rate == 500

    def test_rate_can_be_very_low(self):
        """Test rate can be set to low values."""
        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        tts = SystemTTS(rate=50)
        assert tts.rate == 50


class TestSystemTTSIntegration:
    """Integration tests for SystemTTS (require pyttsx3 installed)."""

    @pytest.mark.slow
    def test_real_engine_initialization(self):
        """Test real pyttsx3 engine initialization."""
        pytest.importorskip("pyttsx3")

        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        try:
            tts = SystemTTS()
            # Access engine to trigger initialization
            engine = tts.engine
            assert engine is not None
        except RuntimeError as e:
            # May fail if espeak not installed
            if "espeak" in str(e).lower():
                pytest.skip("espeak not installed")
            raise

    @pytest.mark.slow
    def test_real_get_voices(self):
        """Test getting real system voices."""
        pytest.importorskip("pyttsx3")

        from scitex_audio.engines._pyttsx3_engine import SystemTTS

        try:
            tts = SystemTTS()
            voices = tts.get_voices()
            assert isinstance(voices, list)
            # Most systems have at least one voice
            assert len(voices) >= 0
        except RuntimeError as e:
            if "espeak" in str(e).lower():
                pytest.skip("espeak not installed")
            raise


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/audio/engines/pyttsx3_engine.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-12-11 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex-code/src/scitex/audio/engines/pyttsx3_engine.py
# # ----------------------------------------
#
# """
# System TTS backend using pyttsx3 - Offline, uses system voices.
#
# Requirements:
#     - pip install pyttsx3
#     - Linux: sudo apt install espeak-ng libespeak1
#     - Windows: Uses SAPI5 (built-in)
#     - macOS: Uses NSSpeechSynthesizer (built-in)
# """
#
# from __future__ import annotations
#
# from pathlib import Path
# from typing import List, Optional
#
# from .base import BaseTTS
#
# __all__ = ["SystemTTS"]
#
#
# class SystemTTS(BaseTTS):
#     """System TTS backend using pyttsx3.
#
#     Works offline using system's built-in TTS engine.
#     Quality varies by platform and available voices.
#
#     Platforms:
#         - Linux: espeak/espeak-ng
#         - Windows: SAPI5
#         - macOS: NSSpeechSynthesizer
#     """
#
#     def __init__(
#         self,
#         rate: int = 150,  # Words per minute
#         volume: float = 1.0,  # 0.0 to 1.0
#         voice: Optional[str] = None,
#         **kwargs,
#     ):
#         super().__init__(**kwargs)
#         self.rate = rate
#         self.volume = volume
#         self.voice = voice
#         self._engine = None
#
#     @property
#     def name(self) -> str:
#         return "pyttsx3"
#
#     @property
#     def engine(self):
#         """Lazy-load pyttsx3 engine."""
#         if self._engine is None:
#             try:
#                 import pyttsx3
#
#                 self._engine = pyttsx3.init()
#                 self._engine.setProperty("rate", self.rate)
#                 self._engine.setProperty("volume", self.volume)
#
#                 if self.voice:
#                     self._set_voice(self.voice)
#             except ImportError:
#                 raise ImportError(
#                     "pyttsx3 package not installed. "
#                     "Install with: pip install pyttsx3\n"
#                     "Linux also requires: sudo apt install espeak-ng libespeak1"
#                 )
#             except RuntimeError as e:
#                 if "eSpeak" in str(e):
#                     raise RuntimeError(
#                         "espeak not installed. "
#                         "Install with: sudo apt install espeak-ng libespeak1"
#                     )
#                 raise
#         return self._engine
#
#     def _set_voice(self, voice_name: str):
#         """Set voice by name or ID."""
#         voices = self.engine.getProperty("voices")
#         for v in voices:
#             if voice_name.lower() in v.name.lower() or voice_name == v.id:
#                 self.engine.setProperty("voice", v.id)
#                 return
#         # If not found, keep default
#
#     def synthesize(self, text: str, output_path: str) -> Path:
#         """Synthesize text using system TTS."""
#         # Set voice if specified in config
#         voice = self.config.get("voice")
#         if voice:
#             self._set_voice(voice)
#
#         out_path = Path(output_path)
#
#         # pyttsx3 can save to file
#         self.engine.save_to_file(text, str(out_path))
#         self.engine.runAndWait()
#
#         return out_path
#
#     def speak_direct(self, text: str):
#         """Speak directly without saving to file (faster)."""
#         voice = self.config.get("voice")
#         if voice:
#             self._set_voice(voice)
#
#         self.engine.say(text)
#         self.engine.runAndWait()
#
#     def get_voices(self) -> List[dict]:
#         """Get available system voices."""
#         voices = self.engine.getProperty("voices")
#         return [
#             {
#                 "name": v.name,
#                 "id": v.id,
#                 "type": "system",
#                 "languages": getattr(v, "languages", []),
#             }
#             for v in voices
#         ]
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/audio/engines/pyttsx3_engine.py
# --------------------------------------------------------------------------------
