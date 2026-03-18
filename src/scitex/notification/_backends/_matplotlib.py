#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_matplotlib.py

"""Matplotlib visual notification backend."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class MatplotlibBackend(BaseNotifyBackend):
    """Visual notification via matplotlib popup window."""

    name = "matplotlib"

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            import matplotlib  # noqa: F401

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
            import matplotlib.pyplot as plt

            # Color based on level
            colors = {
                NotifyLevel.INFO: "#2196F3",
                NotifyLevel.WARNING: "#FF9800",
                NotifyLevel.ERROR: "#F44336",
                NotifyLevel.CRITICAL: "#9C27B0",
            }
            color = colors.get(level, "#2196F3")

            # Create figure
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")

            # Background
            fig.patch.set_facecolor(color)

            # Title and message
            ax.text(
                0.5,
                0.7,
                title or "SciTeX",
                ha="center",
                va="center",
                fontsize=16,
                fontweight="bold",
                color="white",
            )
            ax.text(
                0.5,
                0.35,
                message,
                ha="center",
                va="center",
                fontsize=12,
                color="white",
                wrap=True,
            )

            # Show non-blocking
            plt.ion()
            plt.show(block=False)

            # Force render
            fig.canvas.draw()
            fig.canvas.flush_events()

            # Auto-close after timeout, keeping GUI responsive
            timeout = kwargs.get("timeout", self.timeout)
            elapsed = 0.0
            interval = 0.1  # Check every 100ms
            while elapsed < timeout:
                await asyncio.sleep(interval)
                fig.canvas.flush_events()
                elapsed += interval

            plt.close(fig)

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
