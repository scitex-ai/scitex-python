#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/audio.py
"""Audio module tools for FastMCP unified server."""

import json


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def register_audio_tools(mcp) -> None:
    """Register audio tools with FastMCP server."""

    @mcp.tool()
    async def audio_speak(
        text: str,
        backend: str | None = None,
        voice: str | None = None,
        rate: int = 150,
        speed: float = 1.5,
        play: bool = True,
        save: bool = False,
        output_path: str | None = None,
        fallback: bool = True,
        agent_id: str | None = None,
        wait: bool = True,
        signature: bool = False,
    ) -> str:
        """Convert text to speech with smart routing.

        Smart routing (mode=auto, default):
        - If local audio sink is SUSPENDED and relay available -> uses relay
        - If local audio available -> uses local
        - If neither available -> returns error with instructions

        Args:
            save: Auto-save to timestamped file in SCITEX_DIR/audio/ if output_path not set.
            output_path: Explicit path to save audio file (e.g. /tmp/notify.mp3).

        Environment variables:
        - SCITEX_AUDIO_MODE: 'local', 'remote', or 'auto' (default: auto)
        - SCITEX_AUDIO_RELAY_URL: Relay server URL for remote playback
        """
        from scitex.audio._mcp.handlers import speak_handler

        result = await speak_handler(
            text=text,
            backend=backend,
            voice=voice,
            rate=rate,
            speed=speed,
            play=play,
            save=save,
            output_path=output_path,
            fallback=fallback,
            agent_id=agent_id,
            wait=wait,
            signature=signature,
        )
        return _json(result)


# EOF
