#!/usr/bin/env python3
"""SciTeX Audio — thin wrapper delegating to scitex-audio package."""

from scitex_audio import *  # noqa: F401,F403
from scitex_audio import (
    FALLBACK_ORDER,
    TTS,
    ElevenLabsTTS,
    GoogleTTS,
    LuxTTS,
    SystemTTS,
    available_backends,
    check_local_audio_available,
    check_wsl_audio,
    generate_bytes,
    get_tts,
    speak,
    stop_speech,
)

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
    "LuxTTS",
    "get_tts",
    "available_backends",
    "FALLBACK_ORDER",
]

# EOF
