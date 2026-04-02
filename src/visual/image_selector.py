"""
Seleciona e valida imagem real da notícia (URL do artigo).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import requests
from PIL import Image

import config
from models.article import Article
from utils.safe_log import safe_exc

logger = logging.getLogger(__name__)

_PLACEHOLDER_HINTS = re.compile(
    r"placeholder|pixel\.gif|1x1|spacer|blank\.|transparent\.|data:image",
    re.I,
)


def _is_placeholder_url(url: str) -> bool:
    if not url:
        return True
    return bool(_PLACEHOLDER_HINTS.search(url))


def _download_to(path: Path, url: str, timeout: int = 45) -> bool:
    try:
        r = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; agent-instagram/1.0)"},
        )
        r.raise_for_status()
        path.write_bytes(r.content)
        return True
    except Exception as e:
        logger.debug("Download imagem notícia falhou: %s", safe_exc(e))
        return False


def select_best_image(article: Article, dest_dir: Path) -> Path | None:
    """
    Baixa article['image_url'] se existir e passar validação (tamanho, formato).
    Retorna caminho local ou None.
    """
    if not config.USE_REAL_IMAGE:
        return None

    url = (article.get("image_url") or "").strip()
    if not url or _is_placeholder_url(url):
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = ".jpg"
    if ".png" in url.lower().split("?")[0]:
        suffix = ".png"
    out = dest_dir / f"news_raw_{abs(hash(url)) % 10_000_000}{suffix}"

    if not _download_to(out, url):
        return None

    try:
        with Image.open(out) as im:
            im = im.convert("RGB")
            w, h = im.size
            if w < config.MIN_IMAGE_WIDTH or h < config.MIN_IMAGE_HEIGHT:
                logger.info("Imagem da notícia rejeitada: dimensões %sx%s", w, h)
                out.unlink(missing_ok=True)
                return None
            if w < 2 or h < 2:
                out.unlink(missing_ok=True)
                return None
            im.save(out, format="JPEG", quality=92)
    except Exception as e:
        logger.info("Imagem da notícia inválida (PIL): %s", safe_exc(e))
        out.unlink(missing_ok=True)
        return None

    logger.info("Imagem da notícia aceita: %s", out.name)
    return out
