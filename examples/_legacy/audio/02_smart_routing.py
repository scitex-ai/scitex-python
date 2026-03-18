#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-31
# File: examples/audio/02_smart_routing.py

"""Smart routing examples for scitex.audio module.

Demonstrates automatic local/relay routing based on audio availability.
"""

import os

import scitex.audio as audio


def example_auto_mode():
    """Example: Automatic routing (default behavior)."""
    print("Example 1: Auto Mode (Smart Routing)")
    print("-" * 40)

    # Check current audio state
    local_status = audio.check_local_audio_available()
    print(f"  Local sink state: {local_status.get('state')}")
    print(f"  Local available: {local_status.get('available')}")

    # Auto mode - routes to relay if local is SUSPENDED
    result = audio.speak("Testing auto mode routing.", mode="auto")
    print(f"  Mode used: {result.get('mode')}")
    print(f"  Played: {result.get('played')}")
    if result.get("routing"):
        print(f"  Routing: {result.get('routing')}")


def example_force_local():
    """Example: Force local playback."""
    print("\nExample 2: Force Local Mode")
    print("-" * 40)

    # Force local - fails if sink is SUSPENDED
    result = audio.speak("Testing local mode.", mode="local")
    if result.get("success"):
        print(f"  Local playback succeeded")
    else:
        print(f"  Local playback failed: {result.get('error')}")
        print(f"  Sink state: {result.get('local_state')}")


def example_force_remote():
    """Example: Force relay mode."""
    print("\nExample 3: Force Remote/Relay Mode")
    print("-" * 40)

    # Check if relay is configured
    relay_url = os.environ.get("SCITEX_AUDIO_RELAY_URL")
    print(f"  SCITEX_AUDIO_RELAY_URL: {relay_url or '(not set)'}")

    # Force remote - uses relay server
    result = audio.speak("Testing remote relay mode.", mode="remote")
    if result.get("success"):
        print(f"  Relay playback succeeded")
    else:
        print(f"  Relay playback failed: {result.get('error')}")


def example_environment_config():
    """Example: Environment variable configuration."""
    print("\nExample 4: Environment Configuration")
    print("-" * 40)

    env_vars = [
        "SCITEX_AUDIO_MODE",
        "SCITEX_AUDIO_RELAY_URL",
        "SCITEX_AUDIO_RELAY_HOST",
        "SCITEX_AUDIO_RELAY_PORT",
    ]

    for var in env_vars:
        value = os.environ.get(var, "(not set)")
        print(f"  {var}: {value}")


def example_relay_setup_check():
    """Example: Check relay server availability."""
    print("\nExample 5: Relay Server Check")
    print("-" * 40)

    try:
        from scitex.audio._relay import is_relay_available, get_relay_client

        if is_relay_available():
            client = get_relay_client()
            health = client.health()
            print(f"  Relay server: AVAILABLE")
            print(f"  Health: {health}")
        else:
            print(f"  Relay server: NOT AVAILABLE")
            print("  To set up relay:")
            print("    1. On local machine: scitex audio relay --port 31293")
            print("    2. SSH with tunnel: ssh -R 31293:localhost:31293 remote")
    except Exception as e:
        print(f"  Error checking relay: {e}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("SciTeX Audio - Smart Routing Examples")
    print("=" * 60)
    print()
    print("Smart routing automatically selects local or relay based on:")
    print("  - Local audio sink state (RUNNING/IDLE/SUSPENDED)")
    print("  - Relay server availability")
    print()

    example_environment_config()
    example_auto_mode()
    example_force_local()
    example_force_remote()
    example_relay_setup_check()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
