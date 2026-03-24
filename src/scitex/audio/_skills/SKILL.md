---
name: stx.audio
description: Text-to-speech and audio playback utilities with multiple TTS backend support.
---

# stx.audio

The `stx.audio` module provides text-to-speech (TTS) and audio playback functionality. It supports multiple TTS backends (ElevenLabs, Google TTS, Lux TTS, system TTS) with automatic fallback ordering.

## Python API

```python
import scitex as stx

# Speak text using the best available backend
stx.audio.speak("Experiment complete.")

# Check available backends
backends = stx.audio.available_backends()

# Use a specific backend
tts = stx.audio.get_tts("elevenlabs")
tts.speak("Processing finished.")

# Generate audio bytes without playing
audio_bytes = stx.audio.generate_bytes("Hello world")

# Backend classes
tts = stx.audio.ElevenLabsTTS()
tts = stx.audio.GoogleTTS()
tts = stx.audio.SystemTTS()

# Check audio availability (WSL-aware)
is_available = stx.audio.check_wsl_audio()
```

## Key Features

- `speak(text)` — speak text using best available TTS backend
- Multiple backend classes: `ElevenLabsTTS`, `GoogleTTS`, `LuxTTS`, `SystemTTS`
- `available_backends()` — list which TTS backends are installed
- `generate_bytes(text)` — generate audio bytes without playing
- WSL audio compatibility checking via `check_wsl_audio()`
- Configurable fallback order via `FALLBACK_ORDER`
