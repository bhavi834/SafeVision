"""
config.py
---------
Single source of truth for SafeVision settings.

Every setting is read from environment variables (with sane defaults),
so the same code works locally, in Docker, or in production just by
changing the .env file — nothing below needs to be edited directly.

Copy .env.example to .env and fill in real values (Mongo URI, SMTP
creds, Telegram bot token, etc.) when you're ready to wire up the
database/alerts modules. Until then, the defaults keep the core
detection + compliance + Flask pipeline fully usable on its own.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present.
load_dotenv()


def _env_list(name: str, default: list[str]) -> list[str]:
    """Read a comma-separated env var into a list of stripped strings."""
    raw = os.getenv(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# PPE classes the YOLOv8 model is trained to detect.
# Must match the class order in dataset/data.yaml exactly.
# ---------------------------------------------------------------------------
CLASS_NAMES: list[str] = _env_list(
    "SAFEVISION_CLASSES",
    ["Person", "Helmet", "Safety Vest", "Gloves", "Face Mask", "Goggles", "Safety Boots"],
)

# PPE items that MUST be present on a person for them to be COMPLIANT.
# Per the project spec this defaults to Helmet + Safety Vest, but is
# fully configurable per site via SAFEVISION_REQUIRED_PPE in .env.
REQUIRED_PPE: list[str] = _env_list("SAFEVISION_REQUIRED_PPE", ["Helmet", "Safety Vest"])

# ---------------------------------------------------------------------------
# Model / inference settings
# ---------------------------------------------------------------------------
MODEL_PATH: str = os.getenv("SAFEVISION_MODEL_PATH", "models/best.pt")
CONF_THRESHOLD: float = float(os.getenv("SAFEVISION_CONF_THRESHOLD", "0.40"))
IOU_THRESHOLD: float = float(os.getenv("SAFEVISION_IOU_THRESHOLD", "0.45"))

# How a PPE detection box is matched to a person box. A PPE box is
# assigned to the person whose box it overlaps the most, as long as
# the overlap (intersection-over-PPE-area) clears this fraction.
PPE_TO_PERSON_OVERLAP_THRESHOLD: float = float(
    os.getenv("SAFEVISION_OVERLAP_THRESHOLD", "0.30")
)

# ---------------------------------------------------------------------------
# Site / deployment metadata (used in alert messages, reports, etc.)
# ---------------------------------------------------------------------------
SITE_LOCATION: str = os.getenv("SAFEVISION_LOCATION", "Construction Site A")

# ---------------------------------------------------------------------------
# Flask app settings
# ---------------------------------------------------------------------------
SECRET_KEY: str = os.getenv("SAFEVISION_SECRET_KEY", "dev-secret-key-change-me")
UPLOAD_FOLDER: str = os.getenv("SAFEVISION_UPLOAD_FOLDER", "static/uploads")
OUTPUT_FOLDER: str = os.getenv("SAFEVISION_OUTPUT_FOLDER", "static/outputs")
MAX_CONTENT_LENGTH: int = int(os.getenv("SAFEVISION_MAX_UPLOAD_MB", "50")) * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}

# ---------------------------------------------------------------------------
# MongoDB (wired up properly in the database module — fill these in .env)
# ---------------------------------------------------------------------------
MONGO_URI: str = os.getenv("MONGO_URI", "")
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "safevision")
DATABASE_ENABLED: bool = _env_bool("SAFEVISION_DB_ENABLED", False)

# ---------------------------------------------------------------------------
# Email alerts (SMTP) — fill these in .env when you wire up the alerts module
# ---------------------------------------------------------------------------
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL_TO: list[str] = _env_list("ALERT_EMAIL_TO", [])
EMAIL_ALERTS_ENABLED: bool = _env_bool("SAFEVISION_EMAIL_ALERTS_ENABLED", False)

# ---------------------------------------------------------------------------
# Telegram alerts — fill these in .env when you wire up the alerts module
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ALERTS_ENABLED: bool = _env_bool("SAFEVISION_TELEGRAM_ALERTS_ENABLED", False)
