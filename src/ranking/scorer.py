"""Score editorial composto — funções pequenas e pesos em config."""

from __future__ import annotations

import re
from typing import Iterable

import config
from models.article import Article
from ranking.freshness import freshness_component
from ranking.topic_classifier import classify_topic
_ENGAGEMENT = re.compile(
    r"\b(breaking|exclusive|first|launch|announces?|shuts? down|billion|million|record)\b",
    re.I,
)


def _source_trust_multiplier(source_id: str) -> float:
    s = (source_id or "").lower()
    for key, val in config.SOURCE_TRUST.items():
        if key in s:
            return val
    return config.SOURCE_TRUST.get("unknown", 0.9)


def _keyword_priority_score(article: Article) -> float:
    blob = f"{article.get('title','')} {article.get('description','')}".lower()
    hits = 0
    for kw in config.PRIORITY_KEYWORDS:
        if kw.lower() in blob:
            hits += 1
    return min(100.0, hits * 12.0)


def _title_strength(article: Article) -> float:
    title = (article.get("title") or "").strip()
    if not title:
        return 0.0
    # Comprimento razoável + não só clickbait curto
    L = len(title)
    length_score = min(40.0, L / 4.0)
    word_count = len(title.split())
    wc = min(30.0, word_count * 3.0)
    return min(100.0, length_score + wc)


def _engagement_hint(article: Article) -> float:
    t = f"{article.get('title','')} {article.get('description','')}"
    if _ENGAGEMENT.search(t):
        return 70.0
    return 35.0


def _topic_priority_score(topic: str) -> float:
    mult = config.TOPIC_PRIORITY_WEIGHT.get(topic, 1.0)
    return min(100.0, mult * 55.0)


def score_article(article: Article) -> float:
    topic = classify_topic(article)
    w = config.SCORE_WEIGHTS
    fresh = freshness_component(article)
    kw = _keyword_priority_score(article)
    title = _title_strength(article)
    tpc = _topic_priority_score(topic)
    trust = _source_trust_multiplier(article.get("source") or "") * 55.0
    trust = min(100.0, trust)
    eng = _engagement_hint(article)

    total = (
        w["freshness"] * fresh / 100.0
        + w["keyword_priority"] * kw / 100.0
        + w["title_strength"] * title / 100.0
        + w["topic_priority"] * tpc / 100.0
        + w["source_trust"] * trust / 100.0
        + w["engagement_hint"] * eng / 100.0
    )
    return round(total, 4)


def score_and_sort(articles: Iterable[Article]) -> list[Article]:
    scored: list[Article] = []
    for a in articles:
        d = dict(a)
        d["score"] = score_article(a)
        d["topic"] = classify_topic(a)
        scored.append(d)  # type: ignore[arg-type]
    scored.sort(key=lambda x: float(x.get("score") or 0), reverse=True)
    return scored


def filter_by_age(articles: list[Article]) -> tuple[list[Article], int]:
    """Remove artigos acima de MAX_ARTICLE_AGE_HOURS (frescor 0)."""
    from ranking.freshness import freshness_component

    kept: list[Article] = []
    dropped = 0
    for a in articles:
        if freshness_component(a) <= 0.01:
            dropped += 1
            continue
        kept.append(a)
    return kept, dropped
