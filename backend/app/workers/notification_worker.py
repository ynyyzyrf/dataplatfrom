"""Notification worker — sends alerts via configured channels."""

from __future__ import annotations

import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="notify:send_notification")
def send_notification(self, notification_id: str) -> dict:
    """Send a notification (in-station, email, etc.)."""
    logger.info("Sending notification: %s", notification_id)
    # TODO: Phase 2 implement notification logic
    return {"status": "sent", "notification_id": notification_id}
