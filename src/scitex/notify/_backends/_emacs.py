#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_emacs.py

"""Emacs notification backend using emacsclient."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class EmacsBackend(BaseNotifyBackend):
    """Notification via Emacs using emacsclient.

    Displays notifications in Emacs minibuffer or as alerts.
    Supports different display methods:
    - popup: temporary popup buffer (default, most noticeable)
    - minibuffer: message function
    - alert: alert.el package
    - notifications: notifications.el (desktop notifications from Emacs)
    """

    name = "emacs"

    def __init__(self, method: str = "popup", timeout: float = 5.0):
        """Initialize Emacs backend.

        Parameters
        ----------
        method : str
            Notification method: 'popup', 'minibuffer', 'alert', or 'notifications'
        timeout : float
            Display timeout for visual methods
        """
        self.method = method
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if emacsclient is available."""
        return shutil.which("emacsclient") is not None

    def _escape_elisp_string(self, s: str) -> str:
        """Escape a string for use in elisp."""
        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    def _get_face_for_level(self, level: NotifyLevel) -> str:
        """Get Emacs face name for notification level."""
        faces = {
            NotifyLevel.INFO: "success",
            NotifyLevel.WARNING: "warning",
            NotifyLevel.ERROR: "error",
            NotifyLevel.CRITICAL: "error",
        }
        return faces.get(level, "default")

    async def send(
        self,
        message: str,
        title: Optional[str] = None,
        level: NotifyLevel = NotifyLevel.INFO,
        **kwargs,
    ) -> NotifyResult:
        """Send notification via Emacs."""
        try:
            method = kwargs.get("method", self.method)
            timeout = kwargs.get("timeout", self.timeout)

            # Escape strings for elisp
            msg_escaped = self._escape_elisp_string(message)
            title_escaped = self._escape_elisp_string(title or "SciTeX")
            face = self._get_face_for_level(level)

            # Build elisp command based on method
            if method == "popup":
                # Popup buffer - most noticeable
                level_colors = {
                    NotifyLevel.INFO: "#98C379",  # green
                    NotifyLevel.WARNING: "#E5C07B",  # yellow
                    NotifyLevel.ERROR: "#E06C75",  # red
                    NotifyLevel.CRITICAL: "#E06C75",  # red
                }
                color = level_colors.get(level, "#98C379")
                elisp = f"""
                (let* ((buf (get-buffer-create "*SciTeX Alert*"))
                       (timeout {int(timeout)}))
                  (with-current-buffer buf
                    (erase-buffer)
                    (insert (propertize "\\n  ╔══════════════════════════════════════╗\\n"
                                        'face '(:foreground "{color}" :weight bold)))
                    (insert (propertize "  ║  SciTeX Alert                        ║\\n"
                                        'face '(:foreground "{color}" :weight bold)))
                    (insert (propertize "  ╠══════════════════════════════════════╣\\n"
                                        'face '(:foreground "{color}")))
                    (insert (propertize (format "  ║  [%s] %s\\n" "{level.value.upper()}" "{msg_escaped}")
                                        'face '(:foreground "{color}")))
                    (insert (propertize "  ╚══════════════════════════════════════╝\\n"
                                        'face '(:foreground "{color}")))
                    (goto-char (point-min)))
                  (display-buffer buf
                    '((display-buffer-in-side-window)
                      (side . bottom)
                      (window-height . 8)))
                  (run-at-time timeout nil
                    (lambda ()
                      (when-let ((win (get-buffer-window buf t)))
                        (delete-window win))
                      (kill-buffer buf)))
                  (message "[SciTeX] %s" "{msg_escaped}"))
                """
            elif method == "alert":
                # Use alert.el package (if installed)
                severity_map = {
                    NotifyLevel.INFO: "normal",
                    NotifyLevel.WARNING: "moderate",
                    NotifyLevel.ERROR: "high",
                    NotifyLevel.CRITICAL: "urgent",
                }
                severity = severity_map.get(level, "normal")
                elisp = f"""
                (if (fboundp 'alert)
                    (alert "{msg_escaped}"
                           :title "{title_escaped}"
                           :severity '{severity}
                           :timeout {int(timeout)})
                  (message "[%s] %s: %s" "{level.value.upper()}" "{title_escaped}" "{msg_escaped}"))
                """
            elif method == "notifications":
                # Use notifications.el (requires D-Bus)
                urgency_map = {
                    NotifyLevel.INFO: "normal",
                    NotifyLevel.WARNING: "normal",
                    NotifyLevel.ERROR: "critical",
                    NotifyLevel.CRITICAL: "critical",
                }
                urgency = urgency_map.get(level, "normal")
                elisp = f"""
                (if (fboundp 'notifications-notify)
                    (notifications-notify
                     :title "{title_escaped}"
                     :body "{msg_escaped}"
                     :urgency '{urgency}
                     :timeout {int(timeout * 1000)})
                  (message "[%s] %s: %s" "{level.value.upper()}" "{title_escaped}" "{msg_escaped}"))
                """
            else:
                # Default: minibuffer message with face
                elisp = f"""
                (let ((msg (propertize "[{level.value.upper()}] {title_escaped}: {msg_escaped}" 'face '{face})))
                  (message "%s" msg))
                """

            # Clean up elisp (remove extra whitespace)
            elisp = " ".join(elisp.split())

            # Execute via emacsclient
            cmd = ["emacsclient", "--eval", elisp]

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                ),
            )

            if result.returncode == 0:
                return NotifyResult(
                    success=True,
                    backend=self.name,
                    message=message,
                    timestamp=datetime.now().isoformat(),
                    details={"method": method, "elisp_result": result.stdout.strip()},
                )
            else:
                return NotifyResult(
                    success=False,
                    backend=self.name,
                    message=message,
                    timestamp=datetime.now().isoformat(),
                    error=result.stderr.strip() or "emacsclient failed",
                )

        except subprocess.TimeoutExpired:
            return NotifyResult(
                success=False,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                error="emacsclient timed out",
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
