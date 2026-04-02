"""
Logo / marca via Clearbit e fallback.
"""

from __future__ import annotations

import logging
from pathlib import Path

import requests
from PIL import Image

import config
from models.article import Article
from utils.safe_log import safe_exc

logger = logging.getLogger(__name__)

# (palavra-chave no título/descrição, domínio Clearbit)
KEYWORD_DOMAIN: tuple[tuple[str, str], ...] = (
    ("openai", "openai.com"),
    ("gpt", "openai.com"),
    ("apple", "apple.com"),
    ("iphone", "apple.com"),
    ("google", "google.com"),
    ("gemini", "google.com"),
    ("android", "google.com"),
    ("microsoft", "microsoft.com"),
    ("meta", "meta.com"),
    ("facebook", "meta.com"),
    ("instagram", "meta.com"),
    ("amazon", "amazon.com"),
    ("nvidia", "nvidia.com"),
    ("tesla", "tesla.com"),
    ("samsung", "samsung.com"),
    ("intel", "intel.com"),
    ("amd", "amd.com"),
    ("netflix", "netflix.com"),
    ("spotify", "spotify.com"),
    ("uber", "uber.com"),
    ("twitter", "x.com"),
    ("x.com", "x.com"),
    ("snapchat", "snap.com"),
    ("adobe", "adobe.com"),
    ("salesforce", "salesforce.com"),
    ("oracle", "oracle.com"),
    ("ibm", "ibm.com"),
)


def _detect_domain(article: Article) -> str | None:
    blob = f"{article.get('title','')} {article.get('description','')}".lower()
    for kw, domain in KEYWORD_DOMAIN:
        if kw in blob:
            return domain
    return None


def fetch_brand_asset(article: Article, dest_dir: Path) -> Path | None:
    """Baixa logo Clearbit se conseguir inferir marca do texto."""
    if not config.USE_BRAND_ASSET:
        return None

    domain = _detect_domain(article)
    if not domain:
        return None

    url = f"https://logo.clearbit.com/{domain}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / f"brand_{domain.replace('.', '_')}.png"

    try:
        r = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (compatible; agent-instagram/1.0)"},
        )
        if r.status_code != 200 or len(r.content) < 500:
            logger.info("Clearbit sem logo útil para %s", domain)
            return None
        out.write_bytes(r.content)
        with Image.open(out) as im:
            im = im.convert("RGBA")
            w, h = im.size
            if w < 64 or h < 64:
                out.unlink(missing_ok=True)
                return None
        logger.info("Logo marca obtido: %s", domain)
        return out
    except Exception as e:
        logger.info("Clearbit falhou (%s): %s", domain, safe_exc(e))
        out.unlink(missing_ok=True)
        return None
