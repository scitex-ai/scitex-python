#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_email.py

"""Email notification backend."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class EmailBackend(BaseNotifyBackend):
    """Email notification via scitex.utils._email."""

    name = "email"

    def __init__(
        self,
        recipient: Optional[str] = None,
        sender: Optional[str] = None,
    ):
        self.recipient = (
            recipient
            or os.getenv("SCITEX_UI_EMAIL_NOTIFICATION_TO")
            or os.getenv("SCITEX_NOTIFY_EMAIL_TO")
        )
        self.sender = (
            sender
            or os.getenv("SCITEX_UI_EMAIL_NOTIFICATION_FROM")
            or os.getenv("SCITEX_NOTIFY_EMAIL_FROM")
        )

    def is_available(self) -> bool:
        return bool(
            os.getenv("SCITEX_SCHOLAR_EMAIL_NOREPLY")  # New name
            or os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS")  # Deprecated
            or os.getenv("SCITEX_EMAIL_NOREPLY")  # Global
            or os.getenv("SCITEX_EMAIL_AGENT")  # Fallback
        ) and bool(
            os.getenv("SCITEX_SCHOLAR_EMAIL_PASSWORD")  # New name
            or os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD")  # Deprecated
            or os.getenv("SCITEX_EMAIL_PASSWORD")  # Fallback
        )

    async def send(
        self,
        message: str,
        title: Optional[str] = None,
        level: NotifyLevel = NotifyLevel.INFO,
        **kwargs,
    ) -> NotifyResult:
        try:
            from scitex.utils._notify import notify as email_notify

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: email_notify(
                    subject=title or f"[SciTeX] {level.value.upper()}",
                    message=message,
                    recipient_email=kwargs.get("recipient", self.recipient),
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
