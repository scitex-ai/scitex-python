#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-31
# File: examples/audio/01_basic_usage.py

"""Basic usage examples for scitex.audio module.

This demonstrates the core TTS functionality with multiple backends.
"""

import scitex.audio as audio


def example_basic_speak():
    """Example: Basic text-to-speech."""
    print("Example 1: Basic TTS")

    # Simple speak - auto-selects best available backend
    result = audio.speak("Hello, this is a basic TTS example.")
    print(f"  Result: {result}")


def example_specific_backend():
    """Example: Using specific TTS backends."""
    print("\nExample 2: Specific Backends")

    # List available backends
    backends = audio.available_backends()
    print(f"  Available backends: {backends}")

    # Use Google TTS (free, requires internet)
    if "gtts" in backends:
        result = audio.speak("This uses Google TTS.", backend="gtts")
        print(f"  gtts result: played={result.get('played')}")

    # Use system TTS (offline, requires espeak)
    if "pyttsx3" in backends:
        result = audio.speak("This uses system TTS.", backend="pyttsx3")
        print(f"  pyttsx3 result: played={result.get('played')}")


def example_voice_options():
    """Example: Voice and speed options."""
    print("\nExample 3: Voice Options")

    # Different language with gtts
    result = audio.speak("Bonjour le monde!", backend="gtts", voice="fr")
    print(f"  French: {result}")

    # Faster speech (1.5x speed for gtts)
    result = audio.speak("This is faster speech.", backend="gtts", speed=1.5)
    print(f"  Fast speech: {result}")

    # Slower speech
    result = audio.speak("This is slower speech.", backend="gtts", speed=0.8)
    print(f"  Slow speech: {result}")


def example_save_audio():
    """Example: Save audio to file without playing."""
    print("\nExample 4: Save Audio File")

    # Generate audio file without playing
    result = audio.speak(
        "This audio is saved to a file.",
        play=False,
        output_path="/tmp/scitex_audio_example.mp3",
    )
    print(f"  Saved to: {result.get('path')}")


def example_check_status():
    """Example: Check audio system status."""
    print("\nExample 5: Audio Status")

    # Check local audio availability
    status = audio.check_local_audio_available()
    print(f"  Local audio available: {status.get('available')}")
    print(f"  Sink state: {status.get('state')}")

    # Check WSL audio (if running in WSL)
    wsl_status = audio.check_wsl_audio()
    if wsl_status.get("is_wsl"):
        print(f"  WSL detected: PulseAudio connected={wsl_status.get('pulse_connected')}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("SciTeX Audio - Basic Usage Examples")
    print("=" * 60)

    example_basic_speak()
    example_specific_backend()
    example_voice_options()
    example_save_audio()
    example_check_status()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
