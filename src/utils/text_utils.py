"""Texto: normalização e similaridade leve."""

from __future__ import annotations

import html
import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_WS = re.compile(r"\s+")
_HTML_TAG = re.compile(r"<[^>]+>", re.DOTALL)


def strip_html(text: str | None) -> str:
    """Remove tags HTML e entidades para texto em template / legendas."""
    if not text:
        return ""
    t = _HTML_TAG.sub(" ", text)
    t = html.unescape(t)
    t = _WS.sub(" ", t).strip()
    return t


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normalize_title(title: str) -> str:
    t = (title or "").lower().strip()
    t = strip_accents(t)
    t = _WS.sub(" ", t)
    t = re.sub(r"[^\w\s]", "", t)
    return t


def normalize_url(url: str) -> str:
    if not url:
        return ""
    p = urlparse(url.strip())
    # remove tracking params comuns
    drop = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "fbclid", "gclid"}
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in drop]
    new_query = urlencode(q)
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme.lower(), p.netloc.lower(), path, "", new_query, ""))


def title_similarity(a: str, b: str) -> float:
    na = normalize_title(a)
    nb = normalize_title(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    return SequenceMatcher(None, na, nb).ratio()


def word_tokens(text: str) -> set[str]:
    t = normalize_title(text)
    return {w for w in t.split() if len(w) > 2}
