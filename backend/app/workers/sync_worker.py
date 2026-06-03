"""Sync job worker — handles actual data fetching and storage."""

from __future__ import annotations

import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="sync:execute_sync_job")
def execute_sync_job(self, sync_job_run_id: str) -> dict:
    """Execute a sync job run (called by Celery).

    This is the entry point from the scheduler. It:
    1. Loads the sync job & data source config
    2. Calls the external API via Connector Runtime
    3. Stores raw data
    4. Maps fields & writes structured data
    5. Updates sync_job_runs status
    """
    logger.info("Executing sync job run: %s", sync_job_run_id)
    # TODO: Phase 1.4 implement full sync logic
    return {"status": "pending", "run_id": sync_job_run_id}
