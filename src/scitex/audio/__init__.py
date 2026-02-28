#!/usr/bin/env python3
# Timestamp: "2025-12-11 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/audio/__init__.py
# ----------------------------------------

from __future__ import annotations

"""
SciTeX Audio Module - Text-to-Speech with Multiple Backends

Fallback order: elevenlabs -> gtts -> pyttsx3

Backends:
    - elevenlabs: ElevenLabs (paid, high quality)
    - gtts: Google TTS (free, requires internet)
    - pyttsx3: System TTS (offline, free, uses espeak/SAPI5)

Usage:
    import scitex

    # Auto-select with fallback (pyttsx3 -> gtts -> elevenlabs)
    scitex.audio.speak("Hello, world!")

    # Specify backend
    scitex.audio.speak("Hello", backend="gtts")

    # Use TTS class directly
    from scitex.audio import GoogleTTS, ElevenLabsTTS, SystemTTS
    tts = SystemTTS()
    tts.speak("Hello!")

Installation:
    pip install scitex[audio]
"""

import subprocess as _subprocess

# Check for missing dependencies and warn user (internal)
from scitex._install_guide import warn_module_deps as _warn_module_deps

_missing = _warn_module_deps("audio")

# Import from engines subpackage (public TTS classes only)
# Internal imports (prefixed with _ to hide from API)
from . import engines as _engines_module
from .engines import ElevenLabsTTS, GoogleTTS, SystemTTS
from .engines._base import BaseTTS as _BaseTTS
from .engines._base import TTSBackend as _TTSBackend

del _engines_module


def stop_speech() -> None:
    """Stop any currently playing speech by killing espeak processes."""
    try:
        _subprocess.run(["pkill", "-9", "espeak"], capture_output=True)
    except Exception:
        pass


def check_wsl_audio() -> dict:
    """Check WSL audio status and connectivity.

    Returns:
        dict with keys:
        - is_wsl: bool - whether running in WSL
        - wslg_available: bool - whether WSLg is available
        - pulse_server_exists: bool - whether PulseServer socket exists
        - pulse_connected: bool - whether PulseAudio connection works
        - windows_fallback_available: bool - whether Windows fallback is available
        - recommended: str - recommended playback method
    """
    import os
    import shutil

    result = {
        "is_wsl": False,
        "wslg_available": False,
        "pulse_server_exists": False,
        "pulse_connected": False,
        "windows_fallback_available": False,
        "recommended": "linux",
    }

    # Check if in WSL
    if os.path.exists("/mnt/c/Windows"):
        result["is_wsl"] = True

        # Check WSLg
        if os.path.exists("/mnt/wslg"):
            result["wslg_available"] = True

        # Check PulseServer socket
        if os.path.exists("/mnt/wslg/PulseServer"):
            result["pulse_server_exists"] = True

            # Try to connect to PulseAudio
            try:
                env = os.environ.copy()
                env["PULSE_SERVER"] = "unix:/mnt/wslg/PulseServer"
                proc = _subprocess.run(
                    ["pactl", "info"],
                    capture_output=True,
                    timeout=5,
                    env=env,
                )
                if proc.returncode == 0:
                    result["pulse_connected"] = True
            except Exception:
                pass

        # Check Windows fallback
        if shutil.which("powershell.exe"):
            result["windows_fallback_available"] = True

        # Determine recommendation
        if result["pulse_connected"]:
            result["recommended"] = "linux"
        elif result["windows_fallback_available"]:
            result["recommended"] = "windows"
        else:
            result["recommended"] = "none"
    else:
        # Native Linux
        result["recommended"] = "linux"

    return result


# Import audio availability check
from ._audio_check import check_local_audio_available

# Keep legacy TTS import for backwards compatibility
from ._tts import TTS

__all__ = [
    "speak",
    "generate_bytes",
    "stop_speech",
    "check_wsl_audio",
    "check_local_audio_available",
    "TTS",
    "GoogleTTS",
    "ElevenLabsTTS",
    "SystemTTS",
    "get_tts",
    "available_backends",
    "start_mcp_server",
    "FALLBACK_ORDER",
]

# Fallback order: elevenlabs (best quality) -> gtts (free) -> pyttsx3 (offline)
FALLBACK_ORDER = ["elevenlabs", "gtts", "pyttsx3"]


def available_backends() -> list[str]:
    """Return list of available TTS backends in fallback order."""
    backends = []

    # Check pyttsx3 (offline)
    if SystemTTS:
        try:
            import pyttsx3

            # Try to init to check if espeak is available
            engine = pyttsx3.init()
            engine.stop()
            backends.append("pyttsx3")
        except Exception:
            pass

    # Check gTTS (requires internet, but no API key)
    if GoogleTTS:
        backends.append("gtts")

    # Check ElevenLabs (requires API key)
    if ElevenLabsTTS:
        import os

        api_key = os.environ.get("SCITEX_AUDIO_ELEVENLABS_API_KEY") or os.environ.get(
            "ELEVENLABS_API_KEY"
        )
        if api_key:
            backends.append("elevenlabs")

    return backends


def get_tts(backend: str | None = None, **kwargs) -> _BaseTTS:
    """Get a TTS instance for the specified backend.

    Args:
        backend: Backend name ('pyttsx3', 'gtts', 'elevenlabs').
                 Auto-selects with fallback if None.
        **kwargs: Backend-specific options.

    Returns:
        TTS instance.

    Raises:
        ValueError: If no backends available or backend not found.
    """
    backends = available_backends()

    if not backends:
        raise ValueError(
            "No TTS backends available. Install one of:\n"
            "  pip install pyttsx3       # System TTS (offline, free)\n"
            "    + Linux: sudo apt install espeak-ng libespeak1\n"
            "  pip install gTTS          # Google TTS (free, needs internet)\n"
            "  pip install elevenlabs    # ElevenLabs (paid, best quality)"
        )

    if backend is None:
        # Use fallback order: pyttsx3 -> gtts -> elevenlabs
        for b in FALLBACK_ORDER:
            if b in backends:
                backend = b
                break

    if backend == "pyttsx3" and SystemTTS and "pyttsx3" in backends:
        return SystemTTS(**kwargs)
    elif backend == "gtts" and GoogleTTS:
        return GoogleTTS(**kwargs)
    elif backend == "elevenlabs" and ElevenLabsTTS:
        return ElevenLabsTTS(**kwargs)
    else:
        raise ValueError(f"Backend '{backend}' not available. Available: {backends}")


# Import speak function from refactored module
from ._speak import speak


def generate_bytes(
    text: str,
    backend: str | None = None,
    voice: str | None = None,
    **kwargs,
) -> bytes:
    """Generate TTS audio as raw MP3 bytes without playing.

    Useful for web delivery: the caller streams bytes to a browser
    which plays them via the Web Audio API.

    Backends are tried in FALLBACK_ORDER (elevenlabs → gtts → pyttsx3).
    Set backend explicitly to skip auto-detection.

    Args:
        text: Text to convert to speech.
        backend: TTS backend name, or None for auto-select.
        voice: Voice name/id (backend-specific).
        **kwargs: Extra options forwarded to the backend.

    Returns
    -------
        MP3 audio bytes.

    Raises
    ------
        ValueError: When no backend is available.
        RuntimeError: When synthesis fails for all backends.

    Examples
    --------
        import scitex.audio as audio
        mp3_bytes = audio.generate_bytes("Hello, world!")
        # → send to browser or save to file
    """
    tts = get_tts(backend, **kwargs)
    return tts.to_bytes(text, voice=voice)


def start_mcp_server():
    """Start the MCP server for audio."""
    from .mcp_server import main

    # main() is synchronous - calls mcp.run() directly
    main()


# Clean up internal imports from public namespace
def _cleanup_namespace():
    import sys

    _module = sys.modules[__name__]
    for _name in ["annotations", "engines"]:
        if hasattr(_module, _name):
            delattr(_module, _name)


_cleanup_namespace()
del _cleanup_namespace


# EOF
