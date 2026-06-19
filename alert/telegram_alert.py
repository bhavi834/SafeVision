"""
alerts/telegram_alert.py
--------------------------
Module 9 (Alert System) — Telegram channel.

Uses the plain Telegram Bot HTTP API (no extra SDK needed). Disabled
by default; flip SAFEVISION_TELEGRAM_ALERTS_ENABLED on and fill in
TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID in .env to go live.

Setup reminder (for whoever's filling in .env):
  1. Create a bot via @BotFriend in Telegram, get the bot token.
  2. Message your bot once (or add it to a group), then call
     https://api.telegram.org/bot<TOKEN>/getUpdates to find the chat_id.
"""

from __future__ import annotations

import logging

import requests

import config

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


def build_violation_message(missing_ppe: list[str], location: str | None, timestamp: str) -> str:
    location = location or config.SITE_LOCATION
    missing_str = ", ".join(missing_ppe) if missing_ppe else "required PPE"

    return (
        "⚠️ *WARNING*\n\n"
        f"Worker detected without *{missing_str}*.\n\n"
        f"Location: {location}\n"
        f"Time: {timestamp}"
    )


def send_telegram_alert(message: str) -> bool:
    """Send a Markdown-formatted message via the Telegram Bot API.

    Returns True on success, False if disabled/unconfigured/failed —
    never raises, so a flaky network shouldn't take down a detection run.
    """
    if not config.TELEGRAM_ALERTS_ENABLED:
        logger.info("Telegram alerts disabled (SAFEVISION_TELEGRAM_ALERTS_ENABLED=false) — skipping.")
        return False

    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        logger.warning("Telegram alert requested but bot token/chat id are missing — skipping.")
        return False

    url = f"{TELEGRAM_API_BASE}/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        logger.exception("Failed to send Telegram alert")
        return False
