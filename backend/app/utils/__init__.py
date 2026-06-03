"""Shared utility functions."""

from __future__ import annotations

from datetime import datetime, timezone

__all__ = ["utcnow"]


def utcnow() -> datetime:
    """Return the current UTC time (naive, no tzinfo)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
