#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_desktop.py

"""Desktop notification backend (Linux notify-send, WSL PowerShell toast)."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class DesktopBackend(BaseNotifyBackend):
    """Desktop notification via native OS APIs.

    Supports:
    - Linux: notify-send
    - WSL/Windows: PowerShell toast notifications
    """

    name = "desktop"

    def _is_wsl(self) -> bool:
        """Check if running in WSL."""
        try:
            with open("/proc/version") as f:
                return "microsoft" in f.read().lower()
        except Exception:
            return False

    def _has_powershell(self) -> bool:
        """Check if PowerShell is available."""
        return shutil.which("powershell.exe") is not None

    def is_available(self) -> bool:
        # Check for notify-send (Linux)
        if shutil.which("notify-send") is not None:
            return True
        # Check for PowerShell (WSL/Windows)
        if self._is_wsl() and self._has_powershell():
            return True
        return False

    async def send(
        self,
        message: str,
        title: Optional[str] = None,
        level: NotifyLevel = NotifyLevel.INFO,
        **kwargs,
    ) -> NotifyResult:
        try:
            title = title or "SciTeX"

            # Use PowerShell for WSL
            if self._is_wsl() and self._has_powershell():
                return await self._send_windows_toast(message, title, level)

            # Use notify-send for Linux
            if shutil.which("notify-send"):
                return await self._send_notify_send(message, title, level)

            return NotifyResult(
                success=False,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                error="No desktop notification method available",
            )
        except Exception as e:
            return NotifyResult(
                success=False,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                error=str(e),
            )

    async def _send_notify_send(
        self, message: str, title: str, level: NotifyLevel
    ) -> NotifyResult:
        """Send notification via notify-send (Linux)."""
        urgency_map = {
            NotifyLevel.INFO: "normal",
            NotifyLevel.WARNING: "normal",
            NotifyLevel.ERROR: "critical",
            NotifyLevel.CRITICAL: "critical",
        }

        cmd = [
            "notify-send",
            "-u",
            urgency_map.get(level, "normal"),
            title,
            message,
        ]

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, timeout=5),
        )

        return NotifyResult(
            success=True,
            backend=self.name,
            message=message,
            timestamp=datetime.now().isoformat(),
        )

    async def _send_windows_toast(
        self, message: str, title: str, level: NotifyLevel
    ) -> NotifyResult:
        """Send Windows toast notification via PowerShell."""
        import os as _os

        # Escape for XML
        title_escaped = (
            title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        message_escaped = (
            message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

        ps_script = f"""[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = '<toast><visual><binding template="ToastGeneric"><text>{title_escaped}</text><text>{message_escaped}</text></binding></visual></toast>'
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("SciTeX").Show($toast)
"""

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False) as f:
            f.write(ps_script)
            ps_file = f.name

        try:
            # Use Popen to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.Popen(
                    [
                        "powershell.exe",
                        "-NoProfile",
                        "-NonInteractive",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        ps_file,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                ),
            )

            # Give PowerShell time to read the file
            await asyncio.sleep(0.5)

            return NotifyResult(
                success=True,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                details={"method": "windows_toast"},
            )
        finally:
            # Clean up temp file after delay
            await asyncio.sleep(1)
            try:
                _os.unlink(ps_file)
            except Exception:
                pass


# EOF
