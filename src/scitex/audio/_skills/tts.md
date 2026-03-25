---
name: audio-tts
description: Synthesize speech from text using speak(), generate audio bytes with generate_bytes(), and stop ongoing playback with stop_speech().
---

# TTS / Speech

## speak

High-level function to synthesize and play speech immediately.

```python
speak(text: str, engine: str | None = None, **kwargs) -> None
```

Selects an engine from `FALLBACK_ORDER` if `engine=None`. Raises `RuntimeError` if no engine is available.

**Examples**

```python
import scitex as stx

# Play with default engine (auto-select via fallback order)
stx.audio.speak("Experiment complete.")

# Force a specific engine
stx.audio.speak("Hypothesis confirmed.", engine="google")

# ElevenLabs with voice selection
stx.audio.speak("Results published.", engine="elevenlabs", voice_id="Rachel")
```

---

## generate_bytes

Return raw audio bytes without playing them.

```python
generate_bytes(text: str, engine: str | None = None, **kwargs) -> bytes
```

Useful for saving audio to a file or streaming it elsewhere.

**Examples**

```python
import scitex as stx

audio_data = stx.audio.generate_bytes("Figure one shows a scatter plot.")
with open("narration.mp3", "wb") as f:
    f.write(audio_data)
```

---

## stop_speech

Stop any currently-playing audio.

```python
stop_speech() -> None
```

**Example**

```python
import scitex as stx

stx.audio.speak("Long narration...")
# ... some time later
stx.audio.stop_speech()
```
