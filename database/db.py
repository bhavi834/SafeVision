"""
database/db.py
----------------
Module 7 (Database).

Thin MongoDB helper layer over pymongo. Disabled by default
(SAFEVISION_DB_ENABLED=false) so the core detection/compliance/Flask
pipeline works with zero DB setup; flip the flag and set MONGO_URI in
.env to start persisting workers, violations, and daily reports.

Collections:
  - workers      : known worker profiles (used later by Module 11 — face
                    recognition / worker identification)
  - violations   : one document per non-compliant person sighting
  - daily_reports: pre-aggregated daily stats (Module 10 will populate these)
"""

from __future__ import annotations

import logging

import config

logger = logging.getLogger(__name__)

_client = None
_db = None


def get_db():
    """Return the MongoDB database handle, connecting lazily on first use.

    Returns None (rather than raising) if the database is disabled or
    MONGO_URI isn't set, so callers can do:

        db = get_db()
        if db is not None:
            ...
    """
    global _client, _db

    if not config.DATABASE_ENABLED:
        return None

    if _db is None:
        if not config.MONGO_URI:
            logger.warning("SAFEVISION_DB_ENABLED is true but MONGO_URI is empty — skipping DB writes.")
            return None

        import pymongo

        _client = pymongo.MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[config.MONGO_DB_NAME]

        # Helpful indexes for the dashboard's "violation history" / reports queries
        _db.violations.create_index("timestamp")
        _db.violations.create_index("location")

    return _db


def insert_violation(record: dict):
    """Insert one violation record (see ComplianceEngine.to_violation_records)."""
    db = get_db()
    if db is None:
        return None
    return db.violations.insert_one(record).inserted_id


def insert_worker(profile: dict):
    """Insert/update a worker profile document (Module 11 will build on this)."""
    db = get_db()
    if db is None:
        return None
    return db.workers.insert_one(profile).inserted_id


def get_recent_violations(limit: int = 50):
    """Fetch the most recent violation records, newest first."""
    db = get_db()
    if db is None:
        return []
    return list(db.violations.find().sort("timestamp", -1).limit(limit))
