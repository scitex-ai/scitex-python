---
name: audio-backends
description: TTS backend classes (GoogleTTS, ElevenLabsTTS, SystemTTS, LuxTTS), engine discovery, fallback ordering, and WSL audio checks.
---

# Audio Backends

## Backend classes

All backends inherit from `TTS` (abstract base class).

| Class | Engine key | Requires |
|-------|-----------|----------|
| `GoogleTTS` | `"google"` | `gTTS`, internet |
| `ElevenLabsTTS` | `"elevenlabs"` | `elevenlabs`, API key |
| `SystemTTS` | `"system"` | `espeak` or `say` (macOS) |
| `LuxTTS` | `"lux"` | `lux-tts` package |

```python
import scitex as stx

# Get a specific backend instance
tts = stx.audio.get_tts("google")
tts.speak("Hello from Google TTS")

# Generate bytes directly from a backend
data = tts.generate_bytes("Analysis complete")
```

---

## available_backends

Return a list of backend names that are currently importable.

```python
available_backends() -> list[str]
```

```python
import scitex as stx

print(stx.audio.available_backends())
# ['google', 'system']  — depends on installed packages
```

---

## FALLBACK_ORDER

Module-level list that controls the automatic engine selection order.

```python
import scitex as stx

print(stx.audio.FALLBACK_ORDER)
# ['elevenlabs', 'google', 'lux', 'system']
```

Modify to change default priority:

```python
stx.audio.FALLBACK_ORDER = ["system", "google"]
stx.audio.speak("Uses system TTS first now.")
```

---

## WSL / local audio checks

```python
stx.audio.check_wsl_audio() -> bool
    # True if running in WSL and audio output is accessible.

stx.audio.check_local_audio_available() -> bool
    # True if a local audio device can be opened.
```
