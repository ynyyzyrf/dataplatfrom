"""Data record service — browse raw API records."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_source import DataSource
from app.models.raw_record import RawApiRecord
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class DataRecordService:

    async def list_records(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        data_source_id: str | None = None,
        sync_job_run_id: str | None = None,
        response_status: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[dict], int]:
        """List raw records with filters. Returns (records_with_ds_name, total)."""
        conditions = []
        if data_source_id:
            conditions.append(RawApiRecord.data_source_id == data_source_id)
        if sync_job_run_id:
            conditions.append(RawApiRecord.sync_job_run_id == sync_job_run_id)
        if response_status is not None:
            conditions.append(RawApiRecord.response_status == response_status)
        if start_date:
            conditions.append(RawApiRecord.fetched_at >= start_date)
        if end_date:
            conditions.append(RawApiRecord.fetched_at <= end_date)

        # Count
        count_q = select(func.count(RawApiRecord.id)).where(*conditions)
        total = (await db.execute(count_q)).scalar_one()

        # Fetch with data source name join
        q = (
            select(
                RawApiRecord,
                DataSource.name.label("data_source_name"),
            )
            .outerjoin(DataSource, RawApiRecord.data_source_id == DataSource.id)
            .where(*conditions)
            .order_by(RawApiRecord.fetched_at.desc().nullslast())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await db.execute(q)).all()

        records = []
        for row in rows:
            record, ds_name = row[0], row[1]
            payload_str = json.dumps(record.raw_payload, ensure_ascii=False) if record.raw_payload else ""
            preview = payload_str[:200] if len(payload_str) > 200 else payload_str
            records.append({
                "id": record.id,
                "data_source_id": record.data_source_id,
                "data_source_name": ds_name,
                "sync_job_run_id": record.sync_job_run_id,
                "response_status": record.response_status,
                "fetched_at": record.fetched_at,
                "created_at": record.created_at,
                "payload_preview": preview,
            })

        return records, total

    async def get_record(self, db: AsyncSession, record_id: str) -> dict:
        """Get a single raw record with full payload."""
        q = (
            select(
                RawApiRecord,
                DataSource.name.label("data_source_name"),
            )
            .outerjoin(DataSource, RawApiRecord.data_source_id == DataSource.id)
            .where(RawApiRecord.id == record_id)
        )
        row = (await db.execute(q)).one_or_none()
        if not row:
            raise NotFoundError("数据记录未找到")

        record, ds_name = row[0], row[1]
        payload_str = json.dumps(record.raw_payload, ensure_ascii=False) if record.raw_payload else ""
        preview = payload_str[:200] if len(payload_str) > 200 else payload_str

        return {
            "id": record.id,
            "data_source_id": record.data_source_id,
            "data_source_name": ds_name,
            "sync_job_run_id": record.sync_job_run_id,
            "response_status": record.response_status,
            "fetched_at": record.fetched_at,
            "created_at": record.created_at,
            "payload_preview": preview,
            "raw_payload": record.raw_payload,
        }
