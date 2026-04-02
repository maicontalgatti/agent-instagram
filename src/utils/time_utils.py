"""Datas e frescor."""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from dateutil import parser as date_parser


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_published(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s:
        return None
    try:
        dt = date_parser.parse(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError, OverflowError):
        pass
    try:
        dt = parsedate_to_datetime(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def age_hours(published: datetime | None, now: datetime | None = None) -> float | None:
    if published is None:
        return None
    ref = now or utc_now()
    delta = ref - published
    return max(0.0, delta.total_seconds() / 3600.0)
