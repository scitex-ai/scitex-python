#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_webhook.py

"""Webhook notification backend for Slack, Discord, etc."""

from __future__ import annotations

import asyncio
import json
import os
import urllib.request
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class WebhookBackend(BaseNotifyBackend):
    """Webhook notification for Slack, Discord, etc."""

    name = "webhook"

    def __init__(self, url: Optional[str] = None):
        self.url = (
            url
            or os.getenv("SCITEX_UI_WEBHOOK_URL")
            or os.getenv("SCITEX_NOTIFY_WEBHOOK_URL")
        )

    def is_available(self) -> bool:
        return bool(self.url)

    async def send(
        self,
        message: str,
        title: Optional[str] = None,
        level: NotifyLevel = NotifyLevel.INFO,
        **kwargs,
    ) -> NotifyResult:
        try:
            url = kwargs.get("url", self.url)
            if not url:
                raise ValueError("No webhook URL configured")

            # Format for Slack/Discord compatibility
            payload = {
                "text": f"*{title or 'SciTeX'}*\n{message}",
                "content": f"**{title or 'SciTeX'}**\n{message}",
            }

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
            )

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=10),
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
