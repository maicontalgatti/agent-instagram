"""Componente de frescor temporal (0–100)."""

from __future__ import annotations

import math

from config import FRESHNESS_HALF_LIFE_HOURS, MAX_ARTICLE_AGE_HOURS
from models.article import Article
from utils.time_utils import age_hours, parse_published, utc_now


def freshness_component(article: Article) -> float:
    """
    Retorna valor 0–100. Artigos sem data recebem score médio.
    Acima de MAX_ARTICLE_AGE_HOURS → 0.
    """
    pub = parse_published(article.get("published_at"))
    now = utc_now()
    if pub is None:
        return 45.0
    ah = age_hours(pub, now)
    if ah is None or ah > MAX_ARTICLE_AGE_HOURS:
        return 0.0
    # decaimento exponencial: meia-vida configurável
    decay = math.exp(-ah / max(FRESHNESS_HALF_LIFE_HOURS, 1e-6))
    return min(100.0, decay * 100.0)
