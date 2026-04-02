"""Busca artigos via NewsAPI (get_everything)."""

from __future__ import annotations

import logging
from typing import Any

from newsapi import NewsApiClient

import config
from models.article import Article
from sources.normalize import normalize_raw_article
from utils.safe_log import safe_exc

logger = logging.getLogger(__name__)


def fetch_newsapi() -> list[Article]:
    if not config.NEWS_API_KEY:
        logger.warning("NEWS_API_KEY ausente — NewsAPI ignorada.")
        return []

    out: list[Article] = []
    try:
        client = NewsApiClient(api_key=config.NEWS_API_KEY)
        resp = client.get_everything(
            q=config.NEWSAPI_QUERY,
            language=config.NEWSAPI_LANGUAGE,
            sort_by="publishedAt",
            page_size=min(config.NEWSAPI_PAGE_SIZE, 100),
        )
        articles = resp.get("articles", []) or []
    except Exception as e:
        logger.warning("NewsAPI falhou: %s", safe_exc(e))
        return []

    for a in articles:
        try:
            src = a.get("source") or {}
            src_name = (src.get("name") or "newsapi").lower().replace(" ", "_")
            url = (a.get("url") or "").strip()
            title = (a.get("title") or "").strip()
            if not url or not title:
                continue
            raw: dict[str, Any] = dict(a)
            art = normalize_raw_article(
                source_id=f"newsapi_{src_name[:40]}",
                raw=raw,
                url=url,
                title=title,
                description=a.get("description") or "",
                published=a.get("publishedAt"),
                author=a.get("author"),
                image_url=a.get("urlToImage"),
                language=a.get("language") or config.NEWSAPI_LANGUAGE,
            )
            out.append(art)
        except Exception as e:
            logger.debug("Artigo NewsAPI ignorado: %s", safe_exc(e))
            continue

    return out
