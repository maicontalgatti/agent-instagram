"""Classificação simples por palavras-chave."""

from __future__ import annotations

import re
from typing import Iterable

from models.article import Article

# Ordem importa na escolha do primeiro match forte
TOPIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ai", re.compile(r"\b(ai|artificial intelligence|machine learning|llm|gpt|openai|gemini|claude)\b", re.I)),
    ("big_tech", re.compile(r"\b(apple|google|alphabet|microsoft|meta|amazon|nvidia|tesla)\b", re.I)),
    ("cybersecurity", re.compile(r"\b(hack|breach|ransomware|malware|security|vulnerability|cve)\b", re.I)),
    ("startups", re.compile(r"\b(startup|venture|funding|series [a-z]|ipo)\b", re.I)),
    ("regulation", re.compile(r"\b(regulation|antitrust|eu law|congress|senate bill|lawsuit)\b", re.I)),
    ("gadgets", re.compile(r"\b(iphone|android|pixel|galaxy|smartphone|laptop|tablet|wearable)\b", re.I)),
    ("social_media", re.compile(r"\b(instagram|tiktok|twitter|x\.com|facebook|snapchat|threads)\b", re.I)),
    ("software", re.compile(r"\b(software|saas|cloud|api|developer|github)\b", re.I)),
]


def classify_topic(article: Article) -> str:
    blob = f"{article.get('title','')} {article.get('description','')}".lower()
    for topic, pat in TOPIC_PATTERNS:
        if pat.search(blob):
            return topic
    return "other"


def apply_topics(articles: Iterable[Article]) -> list[Article]:
    out: list[Article] = []
    for a in articles:
        d = dict(a)
        d["topic"] = classify_topic(a)
        out.append(d)  # type: ignore[arg-type]
    return out
