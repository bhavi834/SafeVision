"""
alerts/email_alert.py
-----------------------
Module 9 (Alert System) — email channel.

Fully wired up against config.py's SMTP_* settings. Disabled by
default (SAFEVISION_EMAIL_ALERTS_ENABLED=false) so the core pipeline
runs fine with no credentials at all; flip it on and fill in SMTP_HOST
/ SMTP_USER / SMTP_PASSWORD / ALERT_EMAIL_TO in .env to go live.
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

import config

logger = logging.getLogger(__name__)


def build_violation_message(missing_ppe: list[str], location: str | None, timestamp: str) -> tuple[str, str]:
    """Build (subject, body) for a PPE violation alert, matching the
    spec's alert format.
    """
    location = location or config.SITE_LOCATION
    missing_str = ", ".join(missing_ppe) if missing_ppe else "required PPE"

    subject = "SafeVision WARNING: PPE Violation Detected"
    body = (
        "WARNING\n\n"
        f"Worker detected without {missing_str}.\n\n"
        f"Location: {location}\n"
        f"Time: {timestamp}"
    )
    return subject, body


def send_email_alert(subject: str, body: str, to: list[str] | None = None) -> bool:
    """Send a plaintext email alert. Returns True on success.

    Silently no-ops (returning False) if alerts are disabled or
    credentials are missing, so calling code never needs to branch on
    "is this configured?" before calling it.
    """
    if not config.EMAIL_ALERTS_ENABLED:
        logger.info("Email alerts disabled (SAFEVISION_EMAIL_ALERTS_ENABLED=false) — skipping.")
        return False

    recipients = to or config.ALERT_EMAIL_TO
    if not (config.SMTP_HOST and config.SMTP_USER and config.SMTP_PASSWORD and recipients):
        logger.warning("Email alert requested but SMTP settings/recipients are incomplete — skipping.")
        return False

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = config.SMTP_USER
    message["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, recipients, message.as_string())
        return True
    except Exception:
        logger.exception("Failed to send email alert")
        return False
