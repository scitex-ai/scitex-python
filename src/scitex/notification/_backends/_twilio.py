#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-python/src/scitex/notify/_backends/_twilio.py

"""Twilio phone call notification backend.

Makes an actual phone call to wake up the user.
Supports both direct TwiML calls and Studio Flow executions.

Environment Variables:
    SCITEX_NOTIFY_TWILIO_SID: Twilio Account SID
    SCITEX_NOTIFY_TWILIO_TOKEN: Twilio Auth Token
    SCITEX_NOTIFY_TWILIO_FROM: Twilio phone number (e.g., +1234567890)
    SCITEX_NOTIFY_TWILIO_TO: Destination phone number (e.g., +8190xxxx)
    SCITEX_NOTIFY_TWILIO_FLOW: Studio Flow SID (optional, e.g., FWxxxxxxx)
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Optional

from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult


class TwilioBackend(BaseNotifyBackend):
    """Phone call notification via Twilio."""

    name = "twilio"

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        to_number: Optional[str] = None,
        flow_sid: Optional[str] = None,
        repeat: int = 1,
    ):
        self.account_sid = account_sid or os.getenv("SCITEX_NOTIFY_TWILIO_SID", "")
        self.auth_token = auth_token or os.getenv("SCITEX_NOTIFY_TWILIO_TOKEN", "")
        self.from_number = from_number or os.getenv("SCITEX_NOTIFY_TWILIO_FROM", "")
        self.to_number = to_number or os.getenv("SCITEX_NOTIFY_TWILIO_TO", "")
        self.flow_sid = flow_sid or os.getenv("SCITEX_NOTIFY_TWILIO_FLOW", "")
        self.repeat = repeat

    def is_available(self) -> bool:
        return bool(
            self.account_sid and self.auth_token and self.from_number and self.to_number
        )

    async def send(
        self,
        message: str,
        title: Optional[str] = None,
        level: NotifyLevel = NotifyLevel.INFO,
        **kwargs,
    ) -> NotifyResult:
        try:
            to_number = kwargs.get("to_number") or self.to_number
            from_number = kwargs.get("from_number") or self.from_number
            flow_sid = kwargs.get("flow_sid") or self.flow_sid
            repeat = kwargs.get("repeat") or self.repeat

            if not all([self.account_sid, self.auth_token, from_number, to_number]):
                raise ValueError(
                    "Twilio requires: account_sid, auth_token, from_number, to_number. "
                    "Set SCITEX_NOTIFY_TWILIO_SID/TOKEN/FROM/TO env vars."
                )

            loop = asyncio.get_event_loop()

            for attempt in range(max(1, repeat)):
                if attempt > 0:
                    # Wait 30s between calls (iOS "Repeated Calls" needs
                    # same number within 3 min to bypass silent mode)
                    await asyncio.sleep(30)

                if flow_sid:
                    await loop.run_in_executor(
                        None,
                        lambda: _execute_flow(
                            self.account_sid,
                            self.auth_token,
                            flow_sid,
                            from_number,
                            to_number,
                        ),
                    )
                else:
                    full_message = f"{title}. {message}" if title else message
                    if level == NotifyLevel.CRITICAL:
                        full_message = f"Critical alert! {full_message}"
                    elif level == NotifyLevel.ERROR:
                        full_message = f"Error. {full_message}"

                    twiml = (
                        f"<Response>"
                        f'<Say voice="alice" language="en-US">'
                        f"{_escape_xml(full_message)}</Say>"
                        f'<Pause length="2"/>'
                        f'<Say voice="alice" language="en-US">'
                        f"{_escape_xml(full_message)}</Say>"
                        f"</Response>"
                    )

                    await loop.run_in_executor(
                        None,
                        lambda: _make_call(
                            self.account_sid,
                            self.auth_token,
                            from_number,
                            to_number,
                            twiml,
                        ),
                    )

            return NotifyResult(
                success=True,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                details={
                    "to": to_number,
                    "flow": flow_sid or "direct",
                    "repeat": repeat,
                },
            )
        except Exception as e:
            return NotifyResult(
                success=False,
                backend=self.name,
                message=message,
                timestamp=datetime.now().isoformat(),
                error=str(e),
            )


def _twilio_request(url: str, account_sid: str, auth_token: str, data: bytes):
    """Make an authenticated Twilio API request."""
    import base64
    import json
    import urllib.request

    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode(
        "ascii"
    )

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read().decode())


def _execute_flow(
    account_sid: str,
    auth_token: str,
    flow_sid: str,
    from_number: str,
    to_number: str,
) -> None:
    """Execute a Twilio Studio Flow (no SDK dependency)."""
    import urllib.parse

    url = f"https://studio.twilio.com/v2/Flows/{flow_sid}/Executions"
    data = urllib.parse.urlencode(
        {
            "To": to_number,
            "From": from_number,
        }
    ).encode("utf-8")

    result = _twilio_request(url, account_sid, auth_token, data)
    if result.get("status") == "failed":
        raise RuntimeError(f"Twilio flow failed: {result.get('message', 'unknown')}")


def _make_call(
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
    twiml: str,
) -> None:
    """Make a Twilio call using the REST API (no SDK dependency)."""
    import urllib.parse

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    data = urllib.parse.urlencode(
        {
            "To": to_number,
            "From": from_number,
            "Twiml": twiml,
        }
    ).encode("utf-8")

    result = _twilio_request(url, account_sid, auth_token, data)
    if result.get("status") in ("failed", "canceled"):
        raise RuntimeError(f"Twilio call failed: {result.get('message', 'unknown')}")


def _send_sms(
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
    body: str,
) -> dict:
    """Send an SMS via Twilio REST API (no SDK dependency)."""
    import urllib.parse

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = urllib.parse.urlencode(
        {
            "To": to_number,
            "From": from_number,
            "Body": body,
        }
    ).encode("utf-8")

    result = _twilio_request(url, account_sid, auth_token, data)
    if result.get("status") == "failed":
        raise RuntimeError(f"Twilio SMS failed: {result.get('message', 'unknown')}")
    return result


async def send_sms(
    message: str,
    title: Optional[str] = None,
    to_number: Optional[str] = None,
    from_number: Optional[str] = None,
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> NotifyResult:
    """Send an SMS message via Twilio.

    Parameters
    ----------
    message : str
        SMS body text
    title : str, optional
        Prepended to message if provided
    to_number : str, optional
        Override SCITEX_NOTIFY_TWILIO_TO
    from_number : str, optional
        Override SCITEX_NOTIFY_TWILIO_FROM
    account_sid : str, optional
        Override SCITEX_NOTIFY_TWILIO_SID
    auth_token : str, optional
        Override SCITEX_NOTIFY_TWILIO_TOKEN

    Returns
    -------
    NotifyResult
    """
    sid = account_sid or os.getenv("SCITEX_NOTIFY_TWILIO_SID", "")
    token = auth_token or os.getenv("SCITEX_NOTIFY_TWILIO_TOKEN", "")
    from_num = from_number or os.getenv("SCITEX_NOTIFY_TWILIO_FROM", "")
    to_num = to_number or os.getenv("SCITEX_NOTIFY_TWILIO_TO", "")

    if not all([sid, token, from_num, to_num]):
        return NotifyResult(
            success=False,
            backend="twilio_sms",
            message=message,
            timestamp=datetime.now().isoformat(),
            error=(
                "Twilio SMS requires: account_sid, auth_token, from_number, to_number. "
                "Set SCITEX_NOTIFY_TWILIO_SID/TOKEN/FROM/TO env vars."
            ),
        )

    try:
        body = f"{title}: {message}" if title else message
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _send_sms(sid, token, from_num, to_num, body),
        )
        return NotifyResult(
            success=True,
            backend="twilio_sms",
            message=message,
            timestamp=datetime.now().isoformat(),
            details={
                "to": to_num,
                "sid": result.get("sid", ""),
                "status": result.get("status", ""),
            },
        )
    except Exception as e:
        return NotifyResult(
            success=False,
            backend="twilio_sms",
            message=message,
            timestamp=datetime.now().isoformat(),
            error=str(e),
        )


def _escape_xml(text: str) -> str:
    """Escape XML special characters for TwiML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# EOF
