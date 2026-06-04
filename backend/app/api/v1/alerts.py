"""Alert rule management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.alert_rule import AlertRuleCreate, AlertRuleResponse, AlertRuleUpdate
from app.schemas.common import PaginatedResponse
from app.services.alert_service import AlertService
from app.security.authentication import get_current_user
from app.security.authorization import require_roles
from app.models.user import User

router = APIRouter(prefix="/alert-rules", tags=["Alert Rules"])
alert_svc = AlertService()


def _rule_to_dict(rule) -> dict:
    # Safely extract scalar values before any async boundary
    ch = rule.channels
    if not isinstance(ch, list):
        ch = []
    return AlertRuleResponse(
        id=rule.id,
        name=rule.name,
        rule_type=rule.rule_type,
        target_type=rule.target_type,
        target_id=rule.target_id,
        threshold=rule.threshold,
        window_minutes=rule.window_minutes,
        channels=ch,
        is_active=rule.is_active,
        created_by=rule.created_by,
        created_at=rule.created_at.isoformat() if rule.created_at else None,
        updated_at=rule.updated_at.isoformat() if rule.updated_at else None,
    ).model_dump()


@router.get("", response_model=PaginatedResponse)
async def list_alert_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    rules, total = await alert_svc.list_rules(db, page=page, page_size=page_size)
    items = [_rule_to_dict(r) for r in rules]
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.post("", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    body: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    _auth: User = Depends(require_roles("admin", "editor")),
):
    rule = await alert_svc.create_rule(db, str(current_user.id), **body.model_dump())
    return _rule_to_dict(rule)


@router.get("/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    rule = await alert_svc.get_rule(db, rule_id)
    return _rule_to_dict(rule)


@router.put("/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    body: AlertRuleUpdate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    updates = body.model_dump(exclude_unset=True)
    rule = await alert_svc.update_rule(db, rule_id, **updates)
    return _rule_to_dict(rule)


@router.delete("/{rule_id}", status_code=204)
async def delete_alert_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    await alert_svc.delete_rule(db, rule_id)
