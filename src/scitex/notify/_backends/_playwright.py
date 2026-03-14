#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_playwright.py

"""Playwright browser notification backend."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class PlaywrightBackend(BaseNotifyBackend):
    """Browser notification via Playwright."""

    name = "playwright"

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            from playwright.async_api import async_playwright  # noqa: F401

            return True
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
            from playwright.async_api import async_playwright

            # Color based on level
            colors = {
                NotifyLevel.INFO: "#2196F3",
                NotifyLevel.WARNING: "#FF9800",
                NotifyLevel.ERROR: "#F44336",
                NotifyLevel.CRITICAL: "#9C27B0",
            }
            color = colors.get(level, "#2196F3")

            # Escape HTML
            title_safe = (title or "SciTeX").replace("<", "&lt;").replace(">", "&gt;")
            message_safe = message.replace("<", "&lt;").replace(">", "&gt;")

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        background: {color};
                        color: white;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        height: calc(100vh - 40px);
                    }}
                    h1 {{ margin: 0 0 10px 0; font-size: 24px; }}
                    p {{ margin: 0; font-size: 16px; opacity: 0.9; }}
                </style>
            </head>
            <body>
                <h1>{title_safe}</h1>
                <p>{message_safe}</p>
            </body>
            </html>
            """

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                await page.set_viewport_size({"width": 400, "height": 150})
                await page.set_content(html)

                timeout = kwargs.get("timeout", self.timeout)
                await asyncio.sleep(timeout)
                await browser.close()

            return NotifyResult(
                success=True,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                details={"timeout": timeout},
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
