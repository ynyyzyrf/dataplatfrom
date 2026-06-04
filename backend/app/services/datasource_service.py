"""Data source management service — CRUD with credential encryption."""

from __future__ import annotations

import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.data_source import DataSource, DataSourceStatus
from app.core.exceptions import NotFoundError, ConflictError
from app.security.encryption import encrypt, decrypt


def _encrypt_auth_config(auth_config: dict | None) -> str | None:
    """Encrypt auth_config dict to JSON string of Fernet tokens."""
    if not auth_config:
        return None
    encrypted = {}
    for k, v in auth_config.items():
        if v is not None:
            encrypted[k] = encrypt(str(v)).decode("utf-8")
    return json.dumps(encrypted)


def _decrypt_auth_config(encrypted_json: str | None) -> dict | None:
    """Decrypt auth_config from JSON string back to plain dict."""
    if not encrypted_json:
        return None
    encrypted = json.loads(encrypted_json)
    decrypted = {}
    for k, v in encrypted.items():
        try:
            decrypted[k] = decrypt(v.encode("utf-8"))
        except Exception:
            decrypted[k] = v  # Return raw value if decryption fails
    return decrypted


class DataSourceService:

    async def list_sources(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[DataSource], int]:
        """List data sources with pagination."""
        count_q = select(func.count(DataSource.id))
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(DataSource)
            .order_by(DataSource.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        sources = (await db.execute(q)).scalars().all()
        return list(sources), total

    async def get_source(self, db: AsyncSession, source_id: str) -> DataSource:
        """Get a single data source with eager-loaded sync_jobs."""
        q = (
            select(DataSource)
            .options(selectinload(DataSource.sync_jobs))
            .where(DataSource.id == source_id)
        )
        source = (await db.execute(q)).scalar_one_or_none()
        if not source:
            raise NotFoundError("数据源未找到")
        return source

    async def create_source(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        request_url: str,
        **kwargs,
    ) -> DataSource:
        """Create a new data source."""
        auth_config = kwargs.pop("auth_config", None)
        source = DataSource(
            name=name,
            request_url=request_url,
            created_by=user_id,
            **kwargs,
        )
        if auth_config:
            source.auth_config_encrypted = _encrypt_auth_config(auth_config)
        db.add(source)
        await db.flush()
        return source

    async def update_source(
        self,
        db: AsyncSession,
        source_id: str,
        **kwargs,
    ) -> DataSource:
        """Update a data source."""
        source = await self.get_source(db, source_id)

        auth_config = kwargs.pop("auth_config", None)
        for key, value in kwargs.items():
            if value is not None and hasattr(source, key):
                setattr(source, key, value)

        if auth_config is not None:
            source.auth_config_encrypted = _encrypt_auth_config(auth_config)

        await db.flush()
        return await self.get_source(db, source_id)

    async def delete_source(self, db: AsyncSession, source_id: str) -> None:
        """Delete a data source."""
        source = await self.get_source(db, source_id)
        await db.delete(source)
        await db.flush()

    async def get_decrypted_config(self, source: DataSource) -> dict:
        """Get the decrypted auth configuration for a data source."""
        return _decrypt_auth_config(source.auth_config_encrypted) or {}
