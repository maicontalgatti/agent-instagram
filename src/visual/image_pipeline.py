"""
Orquestra: imagem da notícia → marca → IA → template editorial final.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import requests

import config
from models.article import Article
from ranking.topic_classifier import classify_topic
from visual.asset_fetcher import fetch_brand_asset
from visual.image_selector import select_best_image
from visual.template_engine import render_template
from utils.safe_log import safe_exc

logger = logging.getLogger(__name__)


class VisualSource(str, Enum):
    NEWS_IMAGE = "news_image"
    BRAND_ASSET = "brand_asset"
    AI_GENERATED = "ai_generated"


@dataclass
class VisualBuildResult:
    """Imagem final pronta para upload (JPEG com template)."""

    path: Path
    source: VisualSource
    quality_score: float
    duration_sec: float


def _validate_base_layer(path: Path) -> tuple[bool, float]:
    from PIL import Image

    try:
        with Image.open(path) as im:
            w, h = im.size
            if w < 180 or h < 180:
                return False, 0.0
            score = min(1.0, (w * h) / 800_000.0)
            return True, round(score, 3)
    except Exception as e:
        logger.debug("Validação base: %s", safe_exc(e))
        return False, 0.0


def _validate_final(path: Path) -> tuple[bool, float]:
    from PIL import Image

    try:
        with Image.open(path) as im:
            w, h = im.size
            if w < config.MIN_FINAL_WIDTH or h < config.MIN_FINAL_HEIGHT:
                logger.warning("Final rejeitada: %sx%s", w, h)
                return False, 0.0
            g = im.convert("L")
            samples = [g.getpixel((w // 4, h // 2)), g.getpixel((w // 2, h // 2)), g.getpixel((3 * w // 4, h // 2))]
            mean = sum(samples) / (255.0 * len(samples))
            q = 0.75 + 0.25 * mean
            return True, round(min(1.0, q), 3)
    except Exception as e:
        logger.warning("Validação final: %s", safe_exc(e))
        return False, 0.0


def _download_url_to_file(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, timeout=120, headers={"User-Agent": "Mozilla/5.0 (compatible; agent-instagram/1.0)"})
        r.raise_for_status()
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        logger.warning("Download IA: %s", safe_exc(e))
        return False


def _generate_ai_fallback(article: Article, work_dir: Path) -> Path | None:
    if not config.OPENAI_API_KEY:
        return None
    from content.image_generator import ImageGenerator

    title = (article.get("title") or "technology news").strip()
    desc = (article.get("description") or "")[:400]
    topic = classify_topic(article)
    prompt = (
        f"Professional technology news editorial photograph for a magazine cover. "
        f"The scene must clearly relate to this story: {title}. "
        f"Context: {desc}. "
        f"Topic: {topic}. "
        f"Realistic environment, one clear subject (product, people at work, or hardware), "
        f"modern composition, strong focal point, NOT abstract, NOT random shapes, NOT clipart."
    )
    gen = ImageGenerator()
    url = gen.generate_editorial_image(prompt)
    if not url:
        return None
    out = work_dir / f"ai_{uuid.uuid4().hex[:10]}.png"
    if not _download_url_to_file(url, out):
        return None
    ok, _ = _validate_base_layer(out)
    if not ok:
        out.unlink(missing_ok=True)
        return None
    return out


def build_post_image(article: Article) -> VisualBuildResult | None:
    """
    Gera JPEG final com template editorial.
    Ordem: imagem da notícia → logo marca → DALL·E editorial.
    """
    t0 = time.perf_counter()
    topic = article.get("topic") or classify_topic(article)
    work_dir = config.VISUAL_OUTPUT_DIR / "work"
    work_dir.mkdir(parents=True, exist_ok=True)

    base: Path | None = None
    src: VisualSource | None = None

    if config.USE_REAL_IMAGE:
        base = select_best_image(article, work_dir)
        if base:
            src = VisualSource.NEWS_IMAGE
            logger.info("Fonte visual: news_image")

    if base is None and config.USE_BRAND_ASSET:
        base = fetch_brand_asset(article, work_dir)
        if base:
            src = VisualSource.BRAND_ASSET
            logger.info("Fonte visual: brand_asset")

    if base is None and config.USE_AI_FALLBACK:
        base = _generate_ai_fallback(article, work_dir)
        if base:
            src = VisualSource.AI_GENERATED
            logger.info("Fonte visual: ai_generated")

    if base is None or src is None:
        logger.error("Nenhuma camada base disponível (notícia / marca / IA).")
        return None

    ok_base, q_base = _validate_base_layer(base)
    if not ok_base:
        logger.warning("Camada base rejeitada na validação.")
        base.unlink(missing_ok=True)
        return None

    title = (article.get("title") or "Technology").strip()
    subtitle = (article.get("description") or "").strip() or None

    try:
        final_path = render_template(base, title, topic, subtitle=subtitle)
    except Exception as e:
        logger.error("Falha no template: %s", safe_exc(e))
        return None

    ok_final, q_final = _validate_final(final_path)
    if not ok_final:
        final_path.unlink(missing_ok=True)
        return None

    quality = round(0.5 * q_base + 0.5 * q_final, 3)
    elapsed = round(time.perf_counter() - t0, 2)
    logger.info(
        "Visual pronto | fonte=%s | quality≈%s | tempo=%ss | path=%s",
        src.value,
        quality,
        elapsed,
        final_path.name,
    )
    return VisualBuildResult(path=final_path, source=src, quality_score=quality, duration_sec=elapsed)


def generate_visual(article: Article) -> VisualBuildResult | None:
    """Alias pedido na especificação."""
    return build_post_image(article)
