"""Dynamic query service — queries raw_api_records JSON data."""

from __future__ import annotations

from sqlalchemy import Float, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.raw_record import RawApiRecord
from app.core.exceptions import ValidationError


class QueryService:
    """Execute dynamic queries against raw_api_records."""

    async def execute(
        self,
        db: AsyncSession,
        table: str,
        dimensions: list[str] | None = None,
        metrics: list[dict] | None = None,
        filters: list[dict] | None = None,
        sort: list[dict] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Execute a query and return columns + rows.

        For now, queries raw_api_records aggregated by data_source and status.
        """
        if table == "raw_api_records":
            return await self._query_raw_records(
                db, dimensions or [], metrics or [], filters or [],
                sort or [], limit, offset,
            )

        # For dynamic tables, query raw records filtered by data_source
        return await self._query_raw_records(
            db, dimensions, metrics, filters, sort, limit, offset,
        )

    async def _query_raw_records(
        self,
        db: AsyncSession,
        dimensions: list[str],
        metrics: list[dict],
        filters: list[dict],
        sort: list[dict],
        limit: int,
        offset: int,
    ) -> dict:
        """Execute query with aggregation support."""
        # Build columns from dimensions + metrics
        group_cols = []
        select_cols = []

        for dim in dimensions:
            col = self._json_col(dim)
            group_cols.append(col)
            select_cols.append(col.label(dim))

        for metric in metrics:
            field = metric["field"]
            agg = metric["aggregation"]
            alias = metric.get("alias") or f"{agg}_{field}"
            col = self._json_col(field)
            if agg == "count":
                select_cols.append(func.count(col).label(alias))
            elif agg == "sum":
                select_cols.append(func.sum(col.cast(Float)).label(alias))
            elif agg == "avg":
                select_cols.append(func.avg(col.cast(Float)).label(alias))
            elif agg == "max":
                select_cols.append(func.max(col).label(alias))
            elif agg == "min":
                select_cols.append(func.min(col).label(alias))
            else:
                select_cols.append(func.count(col).label(alias))

        if not select_cols:
            select_cols = [func.count().label("count")]

        q = select(*select_cols).select_from(RawApiRecord.__table__)
        if group_cols:
            q = q.group_by(*group_cols)

        if filters:
            for f in filters:
                col = self._json_col(f["field"])
                op = f.get("operator", "=")
                val = f.get("value")
                if op == "=":
                    q = q.where(col == val)
                elif op == ">":
                    q = q.where(col > val)
                elif op == "<":
                    q = q.where(col < val)
                elif op == ">=":
                    q = q.where(col >= val)
                elif op == "<=":
                    q = q.where(col <= val)
                elif op == "in" and isinstance(val, list):
                    q = q.where(col.in_(val))
                elif op == "like":
                    q = q.where(col.like(f"%{val}%"))

        if sort:
            for s in sort:
                col = self._json_col(s["field"])
                direction = s.get("direction", "asc")
                if direction == "desc":
                    q = q.order_by(col.desc())
                else:
                    q = q.order_by(col.asc())

        # Count total
        count_q = select(func.count()).select_from(q.subquery())
        total = (await db.execute(count_q)).scalar_one()

        q = q.limit(limit).offset(offset)
        result = await db.execute(q)

        columns = list(result.keys())
        rows = [list(row) for row in result.fetchall()]

        return {"columns": columns, "rows": rows, "total": total}

    @staticmethod
    def _json_col(path: str):
        """Build a JSON path extraction column using RawApiRecord.raw_payload."""
        return func.json_extract(RawApiRecord.raw_payload, f"$.{path}")
