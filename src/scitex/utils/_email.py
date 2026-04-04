#!/usr/bin/env python3
# Time-stamp: "2024-11-03 06:33:08 (ywatanabe)"
# File: ./scitex_repo/src/scitex/utils/_email.py

import mimetypes
import os
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase as _MIMEBase
from email.mime.multipart import MIMEMultipart as _MIMEMultipart
from email.mime.text import MIMEText as _MIMEText

from scitex.repro import gen_ID

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def send_gmail(
    sender_gmail,
    sender_password,
    recipient_email,
    subject,
    message,
    sender_name=None,
    cc=None,
    ID=None,
    attachment_paths=None,
    verbose=True,
    smtp_server=None,
    smtp_port=None,
):
    """
    Send email via SMTP. Despite the name, supports any SMTP server.
    Uses mail1030.onamae.ne.jp by default (for scitex.ai emails).
    Falls back to Gmail if sender email is @gmail.com.
    """
    if ID == "auto":
        ID = gen_ID()

    if ID:
        if subject:
            subject = f"{subject} (ID: {ID})"
        else:
            subject = f"ID: {ID}"

    # Auto-detect SMTP server based on sender email or use provided server
    if smtp_server is None:
        if "@gmail.com" in sender_gmail:
            smtp_server = "smtp.gmail.com"
            smtp_port = smtp_port or 587
        else:
            # Use scitex.ai mail server for scitex.ai emails
            smtp_server = os.getenv(
                "SCITEX_SCHOLAR_FROM_EMAIL_SMTP_SERVER", "mail1030.onamae.ne.jp"
            )
            smtp_port = smtp_port or int(
                os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_SMTP_PORT", "587")
            )

    smtp_port = smtp_port or 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_gmail, sender_password)

        gmail = _MIMEMultipart()
        gmail["Subject"] = subject
        gmail["To"] = recipient_email
        if cc:
            if isinstance(cc, str):
                gmail["Cc"] = cc
            elif isinstance(cc, list):
                gmail["Cc"] = ", ".join(cc)
        if sender_name:
            gmail["From"] = f"{sender_name} <{sender_gmail}>"
        else:
            gmail["From"] = sender_gmail
        gmail_body = _MIMEText(message, "plain")
        gmail.attach(gmail_body)

        # Attachment files
        if attachment_paths:
            for path in attachment_paths:
                _, ext = os.path.splitext(path)
                if ext.lower() == ".log":
                    with open(path, encoding="utf-8") as file:
                        content = file.read()
                        cleaned_content = ansi_escape.sub("", content)
                        part = _MIMEText(cleaned_content, "plain")

                        # part = _MIMEText(file.read(), 'plain')
                else:
                    mime_type, _ = mimetypes.guess_type(path)
                    if mime_type is None:
                        mime_type = "text/plain"
                    main_type, sub_type = mime_type.split("/", 1)
                    with open(path, "rb") as file:
                        part = _MIMEBase(main_type, sub_type)
                        part.set_payload(file.read())
                        encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(path)}",
                )
                gmail.attach(part)

        recipients = [recipient_email]
        if cc:
            if isinstance(cc, str):
                recipients.append(cc)
            elif isinstance(cc, list):
                recipients.extend(cc)
        server.send_message(gmail, to_addrs=recipients)

        server.quit()

        if verbose:
            cc_info = f" (CC: {cc})" if cc else ""
            message = "Email was sent:\n"
            message += f"    {sender_gmail} -> {recipient_email}{cc_info}\n"
            message += f"    (ID: {ID})\n"
            if attachment_paths:
                message += "    Attached:\n"
                for ap in attachment_paths:
                    message += f"        {ap}\n"
            print(message)

            # message = f"\nEmail was sent:\n\t{sender_gmail} -> {recipient_email}{cc_info}\n\t(ID: {ID})"
            # if attachment_paths:
            #     attachment_paths_str = '\n\t\t'.join(attachment_paths)
            #     message += f"\n\tAttached:\n\t{attachment_paths_str}"
            # print(message)

    except Exception as e:
        print(f"Email was not sent: {e}")


async def send_email_async(
    from_email: str,
    to_email: str,
    subject: str,
    message: str,
    html: bool = False,
) -> bool:
    """Send email asynchronously using configured SMTP.

    Args:
        from_email: Sender email address
        to_email: Recipient email address
        subject: Email subject
        message: Email body (plain text or HTML)
        html: If True, send as HTML email

    Returns
    -------
        True if email was sent successfully, False otherwise
    """
    import asyncio
    import logging

    logger = logging.getLogger(__name__)

    # Get SMTP credentials from environment
    smtp_user = os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS")
    smtp_password = os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD")
    smtp_server = os.getenv(
        "SCITEX_SCHOLAR_FROM_EMAIL_SMTP_SERVER", "mail1030.onamae.ne.jp"
    )
    smtp_port = int(os.getenv("SCITEX_SCHOLAR_FROM_EMAIL_SMTP_PORT", "587"))

    # Check required credentials
    if not smtp_user:
        logger.warning(
            "Email not sent: SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS not set. "
            "Configure SMTP credentials to enable email notifications."
        )
        return False

    if not smtp_password:
        logger.warning(
            "Email not sent: SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD not set. "
            "Configure SMTP credentials to enable email notifications."
        )
        return False

    if not to_email:
        logger.warning("Email not sent: No recipient email address provided.")
        return False

    def _send_sync():
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)

            msg = _MIMEMultipart("alternative") if html else _MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email

            if html:
                msg.attach(_MIMEText(message, "html"))
            else:
                msg.attach(_MIMEText(message, "plain"))

            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    # Run sync email in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_sync)


# EOF
