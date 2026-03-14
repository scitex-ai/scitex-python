#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/scholar/auth/providers/_notifications.py

"""Scholar authentication notifications with configurable backends.

Environment Variables:
    SCITEX_SCHOLAR_ALERT_BACKENDS: Comma-separated list of backends to use.
        Default: "audio,email"
        Available: audio, emacs, matplotlib, playwright, email
        Example: "audio,emacs,email" or "email" (email only)
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from scitex import logging

if TYPE_CHECKING:
    from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)

# Default backends for scholar alerts
DEFAULT_ALERT_BACKENDS = ["audio", "email"]


class ScholarNotifier:
    """Notification handler for scholar authentication with configurable backends.

    Uses SCITEX_SCHOLAR_ALERT_BACKENDS environment variable to configure
    which notification backends to use. Supports cascade config pattern.

    Example:
        notifier = ScholarNotifier(scholar_config)
        await notifier.notify_intervention_needed(email="user@uni.edu", timeout=120)
        await notifier.notify_success(email="user@uni.edu", expiry_info="2 hours")
        await notifier.notify_failed(email="user@uni.edu", error="Timeout")
    """

    def __init__(self, scholar_config: Optional[ScholarConfig] = None):
        """Initialize notifier with optional scholar config.

        Parameters
        ----------
        scholar_config : ScholarConfig, optional
            Scholar configuration for email addresses and other settings.
        """
        self.scholar_config = scholar_config
        self._backends = self._resolve_backends()

    def _resolve_backends(self) -> list[str]:
        """Resolve alert backends from config/env with cascade priority."""
        # Check env var first
        env_backends = os.getenv("SCITEX_SCHOLAR_ALERT_BACKENDS")
        if env_backends:
            backends = [b.strip() for b in env_backends.split(",") if b.strip()]
            logger.debug(f"Using alert backends from env: {backends}")
            return backends

        # Use default
        logger.debug(f"Using default alert backends: {DEFAULT_ALERT_BACKENDS}")
        return DEFAULT_ALERT_BACKENDS.copy()

    def _get_email_addresses(self) -> tuple[Optional[str], str]:
        """Get to/from email addresses for notifications.

        Note: SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS is for SMTP auth, not From header.
        The From header should always be noreply@scitex.ai for notifications.

        Priority for to_email: env var → config → default
        """
        # Check env var first (highest priority for runtime override)
        to_email = os.getenv("SCITEX_SCHOLAR_NOTIFICATION_EMAIL")

        # From header is always noreply (SMTP auth uses different env var)
        from_email = "noreply@scitex.ai"

        # Fall back to config if env var not set
        if not to_email and self.scholar_config:
            to_email = self.scholar_config.resolve(
                "notification_email", None, None, str
            )

        return to_email, from_email

    async def _send_ui_alert(
        self,
        message: str,
        title: str = "SciTeX Scholar",
        level: str = "info",
    ) -> bool:
        """Send alert via scitex.notify with configured backends (excluding email)."""
        try:
            from scitex.notify import alert_async

            # Use non-email backends for immediate UI feedback
            ui_backends = [b for b in self._backends if b != "email"]
            if not ui_backends:
                return False

            return await alert_async(
                message,
                title=title,
                backend=ui_backends,
                level=level,
                fallback=False,  # Only use configured backends
            )
        except Exception as e:
            logger.debug(f"UI alert failed: {e}")
            return False

    async def _send_email(
        self,
        subject: str,
        message: str,
    ) -> bool:
        """Send detailed email notification."""
        if "email" not in self._backends:
            return False

        try:
            from scitex.utils._email import send_email_async

            to_email, from_email = self._get_email_addresses()
            if not to_email:
                logger.debug("No email address configured for notifications")
                return False

            success = await send_email_async(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                message=message,
            )

            if success:
                logger.info(f"Notification email sent to {to_email}")
            return success

        except Exception as e:
            logger.debug(f"Email notification failed: {e}")
            return False

    async def notify_intervention_needed(
        self,
        email: Optional[str] = None,
        timeout: int = 120,
        login_url: str = "https://my.openathens.net",
        screenshot_data: Optional[dict] = None,
    ) -> bool:
        """Notify that user intervention is needed (2FA) with optional screenshot.

        Parameters
        ----------
        email : str, optional
            Account email being authenticated
        timeout : int
            Authentication timeout in seconds
        login_url : str
            URL for manual login
        screenshot_data : dict, optional
            Screenshot with 'base64', 'url', 'timestamp' keys

        Returns
        -------
        bool
            True if at least one notification succeeded
        """
        # Short audio alert
        ui_success = await self._send_ui_alert(
            "2FA required! Check email for screenshot.",
            title="SciTeX: 2FA",
            level="warning",
        )

        # Email with screenshot if available
        if screenshot_data and screenshot_data.get("base64"):
            email_success = await self._send_screenshot_email(screenshot_data, email)
        else:
            # Simple fallback email
            email_success = await self._send_email(
                "SciTeX: 2FA Required",
                f"Please check browser for 2FA prompt.\nAccount: {email}\nTimeout: {timeout}s",
            )

        return ui_success or email_success

    async def notify_success(
        self,
        email: Optional[str] = None,
        expiry_info: str = "Unknown",
        verification_url: str = "https://my.openathens.net",
    ) -> bool:
        """Notify that authentication was successful.

        Parameters
        ----------
        email : str, optional
            Account email that was authenticated
        expiry_info : str
            Session expiry information
        verification_url : str
            URL to verify authentication status

        Returns
        -------
        bool
            True if at least one notification succeeded
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Short message for immediate UI feedback
        ui_message = f"OpenAthens authenticated! Session expires: {expiry_info}"

        # Detailed email message
        email_message = f"""
OpenAthens Authentication Complete

Your OpenAthens authentication has been completed successfully.

Details:
- System: SciTeX Scholar Module
- Service: OpenAthens Single Sign-On
- Account: {email or "Not specified"}
- Session expires: {expiry_info}
- Verification URL: {verification_url}

Status: Authenticated

You can now access institutional resources through SciTeX Scholar.
The system will use this session for automatic PDF downloads and research access.

This is an automated notification from the SciTeX Scholar authentication system.
Time: {timestamp}
        """.strip()

        # Send both UI alert (immediate) and email (detailed)
        ui_success = await self._send_ui_alert(
            ui_message,
            title="SciTeX: Auth Success",
            level="info",
        )
        email_success = await self._send_email(
            "SciTeX Scholar: OpenAthens Authentication Successful",
            email_message,
        )

        return ui_success or email_success

    async def _send_screenshot_email(
        self,
        screenshot_data: dict,
        email: Optional[str] = None,
    ) -> bool:
        """Send email with screenshot as proper MIME attachment."""
        try:
            import asyncio
            import base64
            import smtplib
            from email.mime.image import MIMEImage
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            to_email, from_email = self._get_email_addresses()
            if not to_email:
                return False

            timestamp = screenshot_data.get("timestamp", "Unknown")
            url = screenshot_data.get("url", "Unknown")
            b64_data = screenshot_data.get("base64", "")
            filepath = screenshot_data.get("path", "")

            if not b64_data:
                logger.warning("No screenshot data available")
                return False

            # Create multipart message with related content (for inline images)
            msg = MIMEMultipart("related")
            msg["Subject"] = f"SciTeX: Auth Screenshot - {timestamp}"
            msg["From"] = from_email
            msg["To"] = to_email

            # HTML body with CID reference to image
            html_message = f"""
<html>
<body>
<h2>OpenAthens Authentication Progress</h2>
<p><strong>Time:</strong> {timestamp}</p>
<p><strong>Account:</strong> {email or "Not specified"}</p>
<p><strong>Current URL:</strong> {url}</p>
<p><strong>Action Required:</strong> Check the screenshot below for 2FA codes or login prompts.</p>
<hr>
<img src="cid:screenshot" style="max-width: 100%; border: 1px solid #ccc;">
<hr>
<p><em>This is an automated notification from SciTeX Scholar.</em></p>
</body>
</html>
            """.strip()

            msg_alternative = MIMEMultipart("alternative")
            msg_alternative.attach(MIMEText(html_message, "html"))
            msg.attach(msg_alternative)

            # Attach image with Content-ID
            image_data = base64.b64decode(b64_data)
            image = MIMEImage(image_data, _subtype="png")
            image.add_header("Content-ID", "<screenshot>")
            image.add_header("Content-Disposition", "inline", filename="screenshot.png")
            msg.attach(image)

            # Send email
            smtp_user = os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS")
            smtp_password = os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD")
            smtp_server = os.getenv(
                "SCITEX_SCHOLAR_FROM_EMAIL_SMTP_SERVER", "mail1030.onamae.ne.jp"
            )
            smtp_port = int(os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_SMTP_PORT", "587"))

            if not smtp_user or not smtp_password:
                logger.warning("SMTP credentials not configured for screenshot email")
                return False

            def _send_sync():
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                server.quit()
                return True

            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, _send_sync)

            if success:
                logger.info(f"Screenshot email sent to {to_email}")
            return success

        except Exception as e:
            logger.warning(f"Screenshot email failed: {e}")
            return False

    async def notify_failed(
        self,
        email: Optional[str] = None,
        error_details: str = "Unknown error",
        timeout: int = 120,
        login_url: str = "https://my.openathens.net",
    ) -> bool:
        """Notify that authentication failed.

        Parameters
        ----------
        email : str, optional
            Account email that failed authentication
        error_details : str
            Error description
        timeout : int
            Timeout that was used
        login_url : str
            URL for manual login

        Returns
        -------
        bool
            True if at least one notification succeeded
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Short message for immediate UI feedback
        ui_message = f"OpenAthens authentication failed: {error_details}"

        # Detailed email message
        email_message = f"""
OpenAthens Authentication Failed

The OpenAthens authentication process was not completed successfully.

Details:
- System: SciTeX Scholar Module
- Service: OpenAthens Single Sign-On
- Account: {email or "Not specified"}
- Error: {error_details}
- Timeout: {timeout} seconds

Status: Authentication failed

Next Steps:
1. Check your internet connection
2. Verify your institutional email and credentials
3. Try the authentication process again
4. Contact your institution's IT support if problems persist

Manual login URL: {login_url}

This is an automated notification from the SciTeX Scholar authentication system.
Time: {timestamp}
        """.strip()

        # Send both UI alert (immediate) and email (detailed)
        ui_success = await self._send_ui_alert(
            ui_message,
            title="SciTeX: Auth Failed",
            level="error",
        )
        email_success = await self._send_email(
            "SciTeX Scholar: OpenAthens Authentication Failed",
            email_message,
        )

        return ui_success or email_success


# EOF
