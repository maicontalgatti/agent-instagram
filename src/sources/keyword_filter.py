"""Filtro por palavras-chave (compatível com modo legado 'news')."""

from __future__ import annotations

from models.article import Article

KEYWORDS = [
    "AI",
    "inteligência artificial",
    "OpenAI",
    "Google",
    "Apple",
    "Microsoft",
    "startup",
    "tecnologia",
    "inovação",
]


def is_relevant(article: Article) -> bool:
    title = article.get("title") or ""
    desc = article.get("description") or ""
    text = f"{title} {desc}".lower()
    return any(k.lower() in text for k in KEYWORDS)


def filter_relevant_articles(articles: list[Article]) -> list[Article]:
    return [a for a in articles if is_relevant(a)]
