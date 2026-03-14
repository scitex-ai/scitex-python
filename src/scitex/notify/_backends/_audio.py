#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_audio.py

"""Audio notification backend via TTS."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class AudioBackend(BaseNotifyBackend):
    """Audio notification via scitex.audio TTS."""

    name = "audio"

    def __init__(
        self,
        backend: str = "gtts",
        speed: float = 1.5,
        rate: int = 180,
    ):
        self.tts_backend = backend
        self.speed = speed
        self.rate = rate

    def is_available(self) -> bool:
        try:
            from scitex.audio import available_backends

            return len(available_backends()) > 0
        except ImportError:
            return False

    async def send(
        self,
        message: str,
        title: Optional[str] = None,
        level: NotifyLevel = NotifyLevel.INFO,
        **kwargs,
    ) -> NotifyResult:
        try:
            from scitex.audio import speak

            # Prepend title if provided
            full_message = f"{title}. {message}" if title else message

            # Add urgency prefix for critical/error levels
            if level == NotifyLevel.CRITICAL:
                full_message = f"Critical alert! {full_message}"
            elif level == NotifyLevel.ERROR:
                full_message = f"Error. {full_message}"

            # Run TTS in executor to not block
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: speak(
                    full_message,
                    backend=kwargs.get("tts_backend", self.tts_backend),
                    speed=kwargs.get("speed", self.speed),
                    rate=kwargs.get("rate", self.rate),
                ),
            )

            return NotifyResult(
                success=True,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            return NotifyResult(
                success=False,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                error=str(e),
            )


# EOF
