"""Celery application configuration.

Defines the main ``celery_app`` instance used by all workers
and scheduled tasks (Celery Beat).
"""

from __future__ import annotations

from celery import Celery
from app.config import settings

celery_app = Celery(
    "gdp_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[  # modules the worker should auto-discover
        "app.workers.sync_worker",
        "app.workers.notification_worker",
    ],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule={},  # filled at runtime by sync_job_service
)
