#!/usr/bin/env python3
# Timestamp: "2025-08-23 11:14:18 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/sso_automation/_BaseSSOAutomator.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Base class for SSO automation."""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext, Page

from scitex.logging import getLogger
from scitex.scholar.config import ScholarConfig

logger = getLogger(__name__)


class BaseSSOAutomator(ABC):
    """Abstract base class for SSO automation."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        mode: str = "interactive",
        use_persistent_session: bool = True,
        session_expiry_days: int = 7,
        notification_from_email_address=None,
        notification_from_email_password=None,
        notification_from_email_smtp_server=None,
        notification_from_email_smtp_port=None,
        notification_from_email_sender_name=None,
        notification_to_email_address=None,
        config=None,
    ):
        """Initialize SSO automator.

        Args:
            username: Username for authentication
            password: Password for authentication
            mode: Browser mode - 'interactive' for human interaction, 'stealth' for automated
            use_persistent_session: Whether to save sessions
            session_expiry_days: How long sessions remain valid
        """
        config = config or ScholarConfig()

        self.username = config.resolve("sso_username", username, default=None)
        self.password = config.resolve("sso_password", password, default=None)
        self.mode = mode
        self.use_persistent_session = use_persistent_session
        self.session_expiry_days = session_expiry_days

        self.notification_from_email_address = config.resolve(
            "from_email_address",
            notification_from_email_address,
            default=None,
        )
        self.notification_from_email_password = config.resolve(
            "from_email_password",
            notification_from_email_password,
            default=None,
        )
        self.notification_from_smtp_server = config.resolve(
            "from_email_smtp_server",
            notification_from_email_smtp_server,
            default=None,
        )
        self.notification_from_smtp_port = config.resolve(
            "from_email_smtp_port",
            notification_from_email_smtp_port,
            default=587,
        )
        self.notification_from_email_sender_name = config.resolve(
            "from_email_sender_mail",
            notification_from_email_sender_name,
            default="SciTeX Scholar",
        )
        self.notification_to_email_address = config.resolve(
            "to_email_address",
            notification_to_email_address,
            default=None,
        )

        # Session management
        self._session_dir = Path.home() / ".scitex" / "scholar" / "sso_sessions"
        self._session_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

    @abstractmethod
    def get_institution_name(self) -> str:
        """Get human-readable institution name."""
        pass

    @abstractmethod
    def get_institution_id(self) -> str:
        """Get machine-readable institution ID."""
        pass

    @abstractmethod
    def is_sso_page(self, url: str) -> bool:
        """Check if URL is institution's SSO page."""
        pass

    @abstractmethod
    async def perform_login_async(self, page: Page) -> bool:
        """Perform the login flow."""
        pass

    async def handle_sso_redirect_async(self, page: Page) -> bool:
        """Handle SSO redirect and perform login if needed.

        Args:
            page: Playwright page object

        Returns
        -------
            True if login successful or already logged in
        """
        try:
            current_url = page.url

            # Check if we're on SSO page
            if not self.is_sso_page(current_url):
                return True

            self.logger.info(f"Detected {self.get_institution_name()} SSO page")

            # Try to restore session first
            if self.use_persistent_session:
                if await self._restore_session_async(page.context):
                    self.logger.info("Restored previous session")
                    # Reload page to apply session
                    await page.reload()
                    await page.wait_for_load_state("networkidle")

                    # Check if still on SSO page
                    if not self.is_sso_page(page.url):
                        return True

            # Need to login
            self.logger.info("Performing SSO login...")
            success = await self.perform_login_async(page)

            if success and self.use_persistent_session:
                await self._save_session_async(page.context)

            return success

        except Exception as e:
            self.logger.error(f"SSO automation failed: {e}")
            return False

    async def _save_session_async(self, context: BrowserContext):
        """Save browser session."""
        try:
            state = await context.storage_state()
            session_file = (
                self._session_dir / f"{self.get_institution_id()}_session.json"
            )

            # Add expiry
            state["expiry"] = (
                datetime.now() + timedelta(days=self.session_expiry_days)
            ).isoformat()

            with open(session_file, "w") as f:
                json.dump(state, f)

            os.chmod(session_file, 0o600)
            self.logger.debug(f"Saved session to {session_file}")

        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")

    async def _restore_session_async(self, context: BrowserContext) -> bool:
        """Restore browser session."""
        try:
            session_file = (
                self._session_dir / f"{self.get_institution_id()}_session.json"
            )

            if not session_file.exists():
                return False

            with open(session_file) as f:
                state = json.load(f)

            # Check expiry
            if "expiry" in state:
                expiry = datetime.fromisoformat(state["expiry"])
                if datetime.now() > expiry:
                    self.logger.info("Session expired")
                    session_file.unlink()
                    return False

            # Apply state (cookies, localStorage, etc.)
            await context.add_cookies(state.get("cookies", []))

            # Note: localStorage restoration requires page navigation
            # It will be applied when the page loads

            self.logger.debug("Restored session successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to restore session: {e}")
            return False

    async def notify_user_async(self, event_type: str, **kwargs) -> None:
        """Send notification to user about SSO events.

        Args:
            event_type: Type of event (2fa_required, authentication_success, etc.)
            **kwargs: Additional context for the notification
        """
        # Generate notification content based on event type
        subject, message, priority = self._generate_notification_content(
            event_type, **kwargs
        )

        # Audio alert (immediate feedback) - uses scitex.notify.alert
        try:
            from scitex.notify import alert_async

            audio_msg = self._generate_audio_message(event_type, **kwargs)
            level = "critical" if priority == "high" else "info"
            await alert_async(audio_msg, title="SciTeX Scholar", level=level)
            self.logger.info(f"Audio alert sent: {event_type}")
        except Exception as e:
            self.logger.debug(f"Audio alert skipped: {e}")

        # Email notification (detailed record)
        try:
            from scitex.utils._email import send_email_async

            success = await send_email_async(
                from_email=self.notification_from_email_address,
                to_email=self.notification_to_email_address,
                subject=subject,
                message=message,
                password=self.notification_from_email_password,
                smtp_server=self.notification_from_smtp_server,
                smtp_port=self.notification_from_smtp_port,
                sender_name=self.notification_from_email_sender_name,
            )
            if success:
                self.logger.info(f"Email notification sent: {event_type}")
        except Exception as e:
            self.logger.debug(f"Email notification skipped: {e}")

    def _generate_audio_message(self, event_type: str, **kwargs) -> str:
        """Generate concise audio message for TTS."""
        if event_type == "2fa_required":
            return "Two factor authentication required. Check your device."
        elif event_type == "authentication_success":
            return "Authentication successful."
        elif event_type == "authentication_failed":
            return "Authentication failed."
        else:
            return f"Scholar authentication event: {event_type}"

    def _generate_notification_content(
        self, event_type: str, **kwargs
    ) -> tuple[str, str, str]:
        """Generate notification content based on event type.

        Args:
            event_type: Type of event
            **kwargs: Additional context

        Returns
        -------
            Tuple of (subject, message, priority)
        """
        institution = self.get_institution_name()

        if event_type == "2fa_required":
            subject = f"SciTeX Scholar: 2FA Required - {institution}"
            message = f"""
{institution} SSO Authentication

A two-factor authentication request has been triggered.

Action Required:
- Check your registered device for the authentication prompt
- Approve the request to complete login
- Authentication will continue automatically once approved

System: SciTeX Scholar Module
Institution: {institution}
Status: Awaiting 2FA approval
Timeout: {kwargs.get("timeout", "Unknown")} seconds

This is an automated notification from the SciTeX Scholar authentication system.
            """.strip()
            priority = "high"

        elif event_type == "authentication_success":
            subject = f"SciTeX Scholar: Authentication Successful - {institution}"
            message = f"""
{institution} SSO Authentication Complete

Your authentication has been completed successfully.

Details:
- Institution: {institution}
- Session expires: {kwargs.get("expires_at", "Unknown")}
- Cookies saved: {kwargs.get("cookie_count", "Unknown")}

System: SciTeX Scholar Module
Status: Authenticated

You can now access institutional resources through SciTeX Scholar.
            """.strip()
            priority = "normal"

        elif event_type == "authentication_failed":
            subject = f"SciTeX Scholar: Authentication Failed - {institution}"
            message = f"""
{institution} SSO Authentication Failed

Authentication was not completed successfully.

Details:
- Institution: {institution}
- Error: {kwargs.get("error", "Unknown error")}
- Retry available: Yes

System: SciTeX Scholar Module
Status: Authentication failed

Please check your credentials and try again.
            """.strip()
            priority = "high"

        elif event_type == "session_expired":
            subject = f"SciTeX Scholar: Session Expired - {institution}"
            message = f"""
{institution} SSO Session Expired

Your authentication session has expired and will need to be renewed.

Details:
- Institution: {institution}
- Expired at: {kwargs.get("expired_at", "Unknown")}
- Auto-renewal: {kwargs.get("auto_renewal", "Disabled")}

System: SciTeX Scholar Module
Status: Session expired

Authentication will be required for the next access.
            """.strip()
            priority = "normal"

        else:
            # Generic notification
            subject = f"SciTeX Scholar: {event_type.replace('_', ' ').title()} - {institution}"
            message = f"""
{institution} SSO Notification

Event: {event_type.replace("_", " ").title()}
Institution: {institution}
Context: {kwargs}

System: SciTeX Scholar Module

This is an automated notification from the SciTeX Scholar authentication system.
            """.strip()
            priority = "normal"

        return subject, message, priority


# EOF
