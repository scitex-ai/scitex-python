#!/usr/bin/env python3
# Timestamp: "2026-02-06 23:02:36 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/audio/_mcp/handlers.py


"""Utility handlers for the scitex-audio MCP server."""

import asyncio
import base64
from datetime import datetime
from pathlib import Path

__all__ = [
    "speak_handler",
    "generate_audio_handler",
    "list_backends_handler",
    "list_voices_handler",
    "play_audio_handler",
    "list_audio_files_handler",
    "clear_audio_cache_handler",
    "check_audio_status_handler",
    "speech_queue_status_handler",
    "announce_context_handler",
]


def _get_audio_dir() -> Path:
    """Get the audio output directory."""
    import os

    base_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
    audio_dir = base_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir


def _get_signature() -> str:
    """Get signature string with hostname, project, and branch."""
    import os
    import socket
    import subprocess

    hostname = socket.gethostname()
    cwd = os.getcwd()
    project = os.path.basename(cwd)

    branch = None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=5,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
    except Exception:
        pass

    parts = [hostname, project]
    if branch:
        parts.append(branch)

    return ". ".join(parts) + ". "


async def generate_audio_handler(
    text: str,
    backend: str | None = None,
    voice: str | None = None,
    output_path: str | None = None,
    return_base64: bool = False,
) -> dict:
    """Generate audio file without playing."""
    try:
        from .. import speak as tts_speak

        loop = asyncio.get_event_loop()

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(_get_audio_dir() / f"tts_{timestamp}.mp3")

        def do_generate():
            return tts_speak(
                text=text,
                backend=backend,
                voice=voice,
                play=False,
                output_path=output_path,
                fallback=True,
            )

        result_path = await loop.run_in_executor(None, do_generate)

        result = {
            "success": True,
            "path": str(result_path),
            "text": text,
            "backend": backend,
            "timestamp": datetime.now().isoformat(),
        }

        if result_path.exists():
            result["size_kb"] = round(result_path.stat().st_size / 1024, 2)

        if return_base64 and result_path.exists():
            with open(result_path, "rb") as f:
                result["base64"] = base64.b64encode(f.read()).decode()

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_backends_handler() -> dict:
    """List available TTS backends."""
    try:
        from .. import FALLBACK_ORDER, available_backends

        backends = available_backends()

        info = []
        for b in FALLBACK_ORDER:
            available = b in backends
            desc = {
                "elevenlabs": "ElevenLabs - Paid, high quality",
                "gtts": "Google TTS - Free, requires internet",
                "pyttsx3": "System TTS - Offline, uses espeak/SAPI5",
            }
            info.append(
                {
                    "name": b,
                    "available": available,
                    "description": desc.get(b, ""),
                }
            )

        # Determine actual default based on FALLBACK_ORDER
        default = None
        for b in FALLBACK_ORDER:
            if b in backends:
                default = b
                break

        return {
            "success": True,
            "backends": info,
            "available": backends,
            "default": default,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_voices_handler(backend: str = "gtts") -> dict:
    """List available voices for a backend."""
    try:
        from .. import get_tts

        loop = asyncio.get_event_loop()

        def do_list():
            tts = get_tts(backend)
            return tts.get_voices()

        voices = await loop.run_in_executor(None, do_list)

        return {
            "success": True,
            "backend": backend,
            "voices": voices,
            "count": len(voices),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def play_audio_handler(path: str) -> dict:
    """Play an audio file."""
    try:
        from ..engines.base import BaseTTS

        path_obj = Path(path)
        if not path_obj.exists():
            return {"success": False, "error": f"File not found: {path}"}

        loop = asyncio.get_event_loop()

        def do_play():
            BaseTTS._play_audio(None, path_obj)

        await loop.run_in_executor(None, do_play)

        return {
            "success": True,
            "played": str(path_obj),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_audio_files_handler(limit: int = 20) -> dict:
    """List generated audio files."""
    try:
        audio_dir = _get_audio_dir()
        if not audio_dir.exists():
            return {"success": True, "files": [], "count": 0}

        audio_files = sorted(
            list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]

        files = []
        for f in audio_files:
            files.append(
                {
                    "name": f.name,
                    "path": str(f),
                    "size_kb": round(f.stat().st_size / 1024, 2),
                    "created": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                }
            )

        total_size = sum(f.stat().st_size for f in audio_dir.glob("*.*"))

        return {
            "success": True,
            "files": files,
            "count": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "audio_dir": str(audio_dir),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def clear_audio_cache_handler(max_age_hours: float = 24) -> dict:
    """Clear audio cache."""
    try:
        audio_dir = _get_audio_dir()
        if not audio_dir.exists():
            return {"success": True, "deleted": 0}

        deleted = 0
        now = datetime.now()

        for f in list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav")):
            try:
                if max_age_hours == 0:
                    f.unlink()
                    deleted += 1
                else:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    age_hours = (now - mtime).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        f.unlink()
                        deleted += 1
            except Exception:
                pass

        return {
            "success": True,
            "deleted": deleted,
            "max_age_hours": max_age_hours,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def check_audio_status_handler() -> dict:
    """Check WSL audio connectivity and available playback methods."""
    try:
        from .. import check_wsl_audio

        status = check_wsl_audio()
        status["success"] = True
        status["timestamp"] = datetime.now().isoformat()
        return status

    except Exception as e:
        return {"success": False, "error": str(e)}


def _emit_browser_speech(text: str) -> None:
    """Emit OSC escape sequence to relay speech through PTY to browser.

    When running inside a SciTeX Cloud Apptainer container, there is no
    local audio sink. Instead, we emit a custom OSC escape:
        \\x1b]9999;speak:<base64-text>\\x07
    This flows through: PTY → WebSocket → browser xterm.js → speakText().
    """
    import sys

    b64 = base64.b64encode(text.encode()).decode()
    # Write to stderr so it doesn't interfere with MCP stdio protocol.
    # The PTY captures both stdout and stderr.
    sys.stderr.write(f"\x1b]9999;speak:{b64}\x07")
    sys.stderr.flush()


async def speak_handler(
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
) -> dict:
    """Convert text to speech with fallback.

    Args:
        save: If True and output_path is None, auto-generate a timestamped path.
        output_path: Explicit path to save the audio file (overrides save flag).
        signature: If True, prepend hostname/project/branch to text.
    """
    import os

    try:
        # Prepend signature if requested
        final_text = text
        sig = None
        if signature:
            sig = _get_signature()
            final_text = sig + text

        # SciTeX Cloud container mode: relay speech to browser via OSC escape
        if os.environ.get("SCITEX_CLOUD") == "true":
            _emit_browser_speech(final_text)
            result = {
                "success": True,
                "text": text,
                "backend": "browser_relay",
                "played": True,
                "play_requested": play,
                "mode": "cloud_relay",
                "timestamp": datetime.now().isoformat(),
            }
            if signature:
                result["signature"] = sig
                result["full_text"] = final_text
            return result

        # Local mode: use scitex.audio directly
        from .. import speak as tts_speak

        loop = asyncio.get_event_loop()

        if output_path is None and save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(_get_audio_dir() / f"tts_{timestamp}.mp3")

        def do_speak():
            return tts_speak(
                text=final_text,
                backend=backend,
                voice=voice,
                rate=rate,
                speed=speed,
                play=play,
                output_path=output_path,
                fallback=fallback,
            )

        speak_result = await loop.run_in_executor(None, do_speak)

        result = {
            "success": speak_result.get("success", True),
            "text": text,
            "backend": speak_result.get("backend", backend),
            "played": speak_result.get("played", False),
            "play_requested": play,
            "mode": speak_result.get("mode", "local"),
            "timestamp": datetime.now().isoformat(),
        }
        if signature:
            result["signature"] = sig
            result["full_text"] = final_text
        if speak_result.get("path"):
            result["path"] = str(speak_result["path"])

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


async def speech_queue_status_handler() -> dict:
    """Get current speech queue status."""
    try:
        from .cross_process_lock import get_queue_status

        status = get_queue_status()
        status["success"] = True
        return status

    except Exception as e:
        return {"success": False, "error": str(e)}


async def announce_context_handler(include_full_path: bool = False) -> dict:
    """Announce current working directory and git branch."""
    try:
        import os
        import subprocess

        cwd = os.getcwd()
        dir_name = cwd if include_full_path else os.path.basename(cwd)

        branch = None
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=cwd,
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
        except Exception:
            pass

        if branch:
            text = f"Working in {dir_name}, on branch {branch}"
        else:
            text = f"Working in {dir_name}"

        speak_result = await speak_handler(text=text, speed=1.5)

        return {
            "success": True,
            "directory": dir_name,
            "branch": branch,
            "announced": text,
            "speak_result": speak_result,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# EOF
