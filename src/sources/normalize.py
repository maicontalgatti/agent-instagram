"""Normaliza dicts brutos para o tipo Article."""

from __future__ import annotations

from typing import Any

from models.article import Article, empty_article, merge_article
from utils.time_utils import parse_published


def normalize_raw_article(
    *,
    source_id: str,
    raw: dict[str, Any],
    url: str,
    title: str,
    description: str | None = None,
    published: Any = None,
    author: str | None = None,
    image_url: str | None = None,
    content: str | None = None,
    language: str | None = None,
) -> Article:
    pub = parse_published(published)
    published_at = pub.isoformat() if pub else None
    base = empty_article()
    return merge_article(
        base,
        source=source_id,
        title=(title or "").strip() or "(sem título)",
        description=(description or "").strip(),
        url=url.strip(),
        published_at=published_at,
        author=(author or "").strip() or None,
        image_url=(image_url or "").strip() or None,
        content=(content or "").strip() or None,
        language=language,
        topic=None,
        score=None,
    )
