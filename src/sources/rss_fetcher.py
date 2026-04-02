"""Busca artigos via RSS (feedparser)."""

from __future__ import annotations

import logging
from typing import Any

import feedparser

from models.article import Article
from sources.normalize import normalize_raw_article
from sources.source_registry import SourceDefinition
from utils.safe_log import safe_exc

logger = logging.getLogger(__name__)


def fetch_rss_source(source: SourceDefinition) -> list[Article]:
    out: list[Article] = []
    try:
        parsed = feedparser.parse(source.endpoint)
    except Exception as e:
        logger.warning("RSS falhou %s: %s", source.id, safe_exc(e))
        return out

    entries = getattr(parsed, "entries", []) or []
    for entry in entries[: source.limit]:
        try:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not link:
                continue
            summary = entry.get("summary") or entry.get("description") or ""
            published = entry.get("published") or entry.get("updated") or entry.get("created")
            author = ""
            if entry.get("author"):
                author = str(entry.author)
            elif entry.get("authors"):
                author = entry.authors[0].get("name", "") if entry.authors else ""

            media = None
            mc = entry.get("media_content") or []
            if mc and isinstance(mc[0], dict):
                media = mc[0].get("url")
            mt = entry.get("media_thumbnail") or []
            if not media and mt and isinstance(mt[0], dict):
                media = mt[0].get("url")

            raw: dict[str, Any] = dict(entry)
            art = normalize_raw_article(
                source_id=source.id,
                raw=raw,
                url=link,
                title=title,
                description=summary,
                published=published,
                author=author or None,
                image_url=media,
            )
            out.append(art)
        except Exception as e:
            logger.debug("Entrada RSS ignorada em %s: %s", source.id, safe_exc(e))
            continue

    return out
