#!/usr/bin/env python3
# Timestamp: "2025-12-11 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/audio/engines/base.py
# ----------------------------------------

"""
Base TTS class defining the common interface for all TTS backends.
"""

from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

__all__ = ["BaseTTS", "TTSBackend"]


class TTSBackend:
    """Enum-like class for TTS backend types."""

    ELEVENLABS = "elevenlabs"
    GTTS = "gtts"
    PYTTSX3 = "pyttsx3"
    EDGE = "edge"  # Future: edge-tts

    @classmethod
    def available(cls) -> List[str]:
        """Return list of available backends."""
        backends = []

        # Check gTTS (always available if installed, needs internet)
        try:
            import gtts

            backends.append(cls.GTTS)
        except ImportError:
            pass

        # Check pyttsx3
        try:
            import pyttsx3

            backends.append(cls.PYTTSX3)
        except ImportError:
            pass

        # Check ElevenLabs
        try:
            import os

            import elevenlabs

            if os.environ.get("SCITEX_AUDIO_ELEVENLABS_API_KEY") or os.environ.get(
                "ELEVENLABS_API_KEY"
            ):
                backends.append(cls.ELEVENLABS)
        except ImportError:
            pass

        return backends


class BaseTTS(ABC):
    """Abstract base class for TTS implementations."""

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> Path:
        """Synthesize text to audio file.

        Args:
            text: Text to convert to speech.
            output_path: Path to save the audio file.

        Returns
        -------
            Path to the generated audio file.
        """
        pass

    @abstractmethod
    def get_voices(self) -> List[dict]:
        """Get available voices for this backend.

        Returns
        -------
            List of voice dictionaries with 'name' and 'id' keys.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the backend name."""
        pass

    @property
    def requires_api_key(self) -> bool:
        """Whether this backend requires an API key."""
        return False

    @property
    def requires_internet(self) -> bool:
        """Whether this backend requires internet connection."""
        return False

    def speak(
        self,
        text: str,
        output_path: Optional[str] = None,
        play: bool = True,
        voice: Optional[str] = None,
    ) -> dict:
        """Synthesize and optionally play text.

        Args:
            text: Text to speak.
            output_path: Optional path to save audio.
            play: Whether to play the audio.
            voice: Optional voice name/id.

        Returns
        -------
            Dict with keys: path (if output_path), played (bool), success (bool).
        """
        import tempfile

        # Determine output path
        if output_path:
            out_path = Path(output_path)
        else:
            suffix = ".mp3"
            fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="scitex_tts_")
            import os

            os.close(fd)
            out_path = Path(tmp_path)

        # Set voice if provided
        if voice:
            self.config["voice"] = voice

        # Synthesize
        result_path = self.synthesize(text, str(out_path))

        # Play if requested
        played = False
        if play:
            played = self._play_audio(result_path)

        result = {"success": True, "played": played, "play_requested": play}
        if output_path:
            result["path"] = result_path
        return result

    def to_bytes(
        self,
        text: str,
        voice: Optional[str] = None,
    ) -> bytes:
        """Synthesize text and return raw audio bytes (MP3).

        Does not play audio — caller is responsible for playback.
        Useful for streaming audio to a browser or returning via HTTP.

        Args:
            text: Text to convert to speech.
            voice: Optional voice name/id.

        Returns
        -------
            MP3 audio bytes.
        """
        import os
        import tempfile

        if voice:
            self.config["voice"] = voice

        fd, tmp_path = tempfile.mkstemp(suffix=".mp3", prefix="scitex_tts_")
        os.close(fd)
        try:
            self.synthesize(text, tmp_path)
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _play_audio(self, path: Path) -> bool:
        """Play audio file using available system player.

        Includes Windows fallback for WSL environments where PulseAudio
        may be unstable.

        Returns
        -------
            True if playback succeeded, False otherwise.
        """
        import os

        # Check if we're in WSL - if so, prefer Windows playback directly
        # to avoid double playback issues with Linux audio hanging
        if os.path.exists("/mnt/c/Windows"):
            if self._play_audio_windows(path):
                return True
            # Fall through to Linux players if Windows playback fails

        players = [
            ["ffplay", "-nodisp", "-autoexit", str(path)],
            ["mpv", "--no-video", str(path)],
            ["aplay", str(path)],
            ["afplay", str(path)],  # macOS
        ]

        for player_cmd in players:
            try:
                subprocess.run(
                    player_cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=30,
                )
                return True
            except subprocess.TimeoutExpired:
                # Audio playback hung - might have played but can't confirm
                return False
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        print(f"Warning: No audio player found. Audio saved to: {path}")
        return False

    def _play_audio_windows(self, path: Path) -> bool:
        """Play audio via Windows PowerShell SoundPlayer (WSL fallback).

        This is useful when WSLg PulseAudio connection is unstable.
        Uses System.Media.SoundPlayer which is headless (no GUI).

        Args:
            path: Path to audio file (in WSL filesystem)

        Returns
        -------
            True if playback succeeded, False otherwise
        """
        import os
        import shutil
        import tempfile

        # Check if we're in WSL
        if not os.path.exists("/mnt/c/Windows"):
            return False

        # Check if powershell.exe is available
        powershell = shutil.which("powershell.exe")
        if not powershell:
            return False

        try:
            # SoundPlayer only supports WAV, so convert if needed
            wav_path = path
            if path.suffix.lower() in (".mp3", ".ogg", ".m4a"):
                try:
                    from pydub import AudioSegment

                    # Create temp WAV file
                    fd, tmp_wav = tempfile.mkstemp(suffix=".wav", prefix="scitex_")
                    os.close(fd)
                    wav_path = Path(tmp_wav)

                    audio = AudioSegment.from_file(str(path))
                    audio.export(str(wav_path), format="wav")
                except ImportError:
                    # pydub not available, try direct playback anyway
                    pass

            # Convert WSL path to Windows path
            result = subprocess.run(
                ["wslpath", "-w", str(wav_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return False

            windows_path = result.stdout.strip()

            # Play using PowerShell's SoundPlayer (headless, no GUI)
            ps_command = f"""
$player = New-Object System.Media.SoundPlayer
$player.SoundLocation = "{windows_path}"
$player.PlaySync()
"""
            subprocess.run(
                [powershell, "-NoProfile", "-Command", ps_command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60,
            )

            # Clean up temp WAV if created
            if wav_path != path and wav_path.exists():
                try:
                    wav_path.unlink()
                except Exception:
                    pass

            return True

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
            return False


# EOF
