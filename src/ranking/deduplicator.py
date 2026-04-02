"""Remove duplicatas por URL e título similar."""

from __future__ import annotations

import logging

from config import TITLE_SIMILARITY_THRESHOLD
from models.article import Article
from utils.text_utils import normalize_url, title_similarity

logger = logging.getLogger(__name__)


def deduplicate_articles(articles: list[Article]) -> tuple[list[Article], int]:
    """
    Mantém ordem aproximada (primeira ocorrência vence).
    Retorna (lista, quantidade removida).
    """
    seen_urls: set[str] = set()
    kept: list[Article] = []
    removed = 0

    for art in articles:
        u = normalize_url(art.get("url") or "")
        if not u:
            removed += 1
            continue
        if u in seen_urls:
            removed += 1
            continue

        dup_title = False
        for prev in kept:
            if title_similarity(art.get("title") or "", prev.get("title") or "") >= TITLE_SIMILARITY_THRESHOLD:
                dup_title = True
                break
        if dup_title:
            removed += 1
            continue

        seen_urls.add(u)
        kept.append(art)

    logger.info("Deduplicação: removidos=%s restantes=%s", removed, len(kept))
    return kept, removed
