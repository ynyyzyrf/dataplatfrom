"""Alert rule management and evaluation service."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert_rule import AlertRule
from app.models.sync_job import SyncJobRun
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

ALERT_TYPES = ["consecutive_failures", "http_error", "timeout", "zero_data", "token_expiry"]
TARGET_TYPES = ["sync_job", "data_source"]


class AlertService:

    # -- CRUD ----------------------------------------------------------------

    async def list_rules(self, db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[AlertRule], int]:
        count_q = select(func.count(AlertRule.id))
        total = (await db.execute(count_q)).scalar_one()
        q = select(AlertRule).order_by(AlertRule.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
        rules = (await db.execute(q)).scalars().all()
        return list(rules), total

    async def get_rule(self, db: AsyncSession, rule_id: str) -> AlertRule:
        q = select(AlertRule).where(AlertRule.id == rule_id)
        rule = (await db.execute(q)).scalar_one_or_none()
        if not rule:
            raise NotFoundError("告警规则未找到")
        return rule

    async def create_rule(self, db: AsyncSession, user_id: str | None = None, **kwargs) -> AlertRule:
        rule = AlertRule(created_by=user_id, **kwargs)
        db.add(rule)
        await db.flush()
        return rule

    async def update_rule(self, db: AsyncSession, rule_id: str, **kwargs) -> AlertRule:
        rule = await self.get_rule(db, rule_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(rule, key):
                setattr(rule, key, value)
        await db.flush()
        # Refetch to ensure all columns are loaded in the current async context
        return await self.get_rule(db, rule_id)

    async def delete_rule(self, db: AsyncSession, rule_id: str) -> None:
        rule = await self.get_rule(db, rule_id)
        await db.delete(rule)
        await db.flush()

    # -- Evaluation ----------------------------------------------------------

    async def evaluate_for_job_run(self, db: AsyncSession, job_run: SyncJobRun) -> list[dict]:
        """Evaluate all active alert rules against a sync job run. Returns triggered alerts."""
        q = select(AlertRule).where(
            and_(
                AlertRule.is_active == True,
                AlertRule.target_type == "sync_job",
                AlertRule.target_id == job_run.sync_job_id,
            )
        )
        rules = (await db.execute(q)).scalars().all()
        triggered = []

        for rule in rules:
            is_triggered = await self._check_rule(db, rule, job_run)
            if is_triggered:
                triggered.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "rule_type": rule.rule_type,
                    "channels": rule.channels if isinstance(rule.channels, list) else (rule.channels or []),
                    "message": self._format_message(rule, job_run),
                })

        return triggered

    async def _check_rule(self, db: AsyncSession, rule: AlertRule, job_run: SyncJobRun) -> bool:
        """Check if a specific rule is triggered by this job run."""
        if rule.rule_type == "http_error":
            return job_run.status == "failed" and job_run.error_message is not None

        if rule.rule_type == "timeout":
            if job_run.finished_at and job_run.started_at:
                duration = (job_run.finished_at - job_run.started_at).total_seconds()
                return duration > rule.threshold
            return False

        if rule.rule_type == "zero_data":
            return job_run.status == "success" and job_run.fetched_count == 0

        if rule.rule_type == "consecutive_failures":
            # Count consecutive failures in window
            cutoff = datetime.now(timezone.utc)
            if rule.window_minutes:
                from datetime import timedelta
                cutoff = datetime.now(timezone.utc) - timedelta(minutes=rule.window_minutes)
            q = (
                select(func.count(SyncJobRun.id))
                .where(
                    and_(
                        SyncJobRun.sync_job_id == rule.target_id,
                        SyncJobRun.status == "failed",
                        SyncJobRun.started_at >= cutoff,
                    )
                )
                .order_by(SyncJobRun.started_at.desc())
            )
            count = (await db.execute(q)).scalar_one()
            return count >= rule.threshold

        if rule.rule_type == "token_expiry":
            # Check if data source auth is about to expire
            return False  # Placeholder for future implementation

        return False

    def _format_message(self, rule: AlertRule, job_run: SyncJobRun) -> str:
        messages = {
            "consecutive_failures": f"同步任务在过去{rule.window_minutes}分钟内连续失败{rule.threshold}次",
            "http_error": f"同步任务运行失败：{job_run.error_message or '未知错误'}",
            "timeout": f"同步任务运行超过{rule.threshold}秒超时",
            "zero_data": "同步任务已完成但获取了0条记录",
            "token_expiry": "数据源认证令牌即将过期",
        }
        return messages.get(rule.rule_type, f"告警规则'{rule.name}'已触发")
