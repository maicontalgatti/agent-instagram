"""Formato padronizado de artigo no pipeline editorial."""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class Article(TypedDict, total=False):
    source: str
    title: str
    description: str
    url: str
    published_at: str | None
    author: str | None
    image_url: str | None
    content: str | None
    language: str | None
    topic: str | None
    score: float | None


def empty_article() -> Article:
    return {
        "source": "",
        "title": "",
        "description": "",
        "url": "",
        "published_at": None,
        "author": None,
        "image_url": None,
        "content": None,
        "language": None,
        "topic": None,
        "score": None,
    }


def merge_article(base: Article, **fields: Any) -> Article:
    out = dict(base)
    for k, v in fields.items():
        if v is not None:
            out[k] = v  # type: ignore[assignment]
    return out  # type: ignore[return-value]
