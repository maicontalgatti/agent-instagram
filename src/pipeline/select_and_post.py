"""
Pipeline: buscar → normalizar → deduplicar → classificar → pontuar → escolher → gerar → publicar.
"""

from __future__ import annotations

import logging

import config
from content.image_generator import ImageGenerator
from content.post_builder import PostBuilder
from models.article import Article
from publish.instagram_poster import InstagramPoster
from ranking.deduplicator import deduplicate_articles
from ranking.scorer import filter_by_age, score_and_sort
from sources.newsapi_fetcher import fetch_newsapi
from sources.rss_fetcher import fetch_rss_source
from sources.site_fetcher import fetch_site_stubs
from sources.source_registry import get_all_sources
from storage.state_store import StateStore
from utils.logger import setup_logging
from utils.safe_log import sanitize_url_for_log

setup_logging()


def _gather_articles() -> tuple[list[Article], dict[str, int]]:
    log = logging.getLogger(__name__)
    per_source: dict[str, int] = {}
    merged: list[Article] = []

    for src in get_all_sources():
        if src.kind == "rss":
            try:
                batch = fetch_rss_source(src)
            except Exception as e:
                log.warning("Fonte RSS %s erro: %s", src.id, e)
                batch = []
            per_source[src.id] = len(batch)
            merged.extend(batch)

    try:
        api_batch = fetch_newsapi()
    except Exception as e:
        log.warning("NewsAPI erro: %s", e)
        api_batch = []
    per_source["newsapi"] = len(api_batch)
    merged.extend(api_batch)

    stub = fetch_site_stubs()
    per_source["site_stub"] = len(stub)
    merged.extend(stub)

    return merged, per_source


def run_select_and_post(*, dry_run: bool = False) -> bool:
    """
    Executa o pipeline completo.
    Retorna True se postou (ou dry-run completou até geração de conteúdo).
    """
    log = logging.getLogger("agent_instagram.pipeline")
    store = StateStore(config.STATE_FILE)
    store.load()

    raw, counts = _gather_articles()
    log.info("Coleta por fonte: %s | total_bruto=%s", counts, len(raw))

    deduped, removed_dup = deduplicate_articles(raw)
    log.info("Após deduplicação: removidos=%s restantes=%s", removed_dup, len(deduped))

    fresh, dropped_age = filter_by_age(deduped)
    log.info("Após filtro de idade: removidos=%s restantes=%s", dropped_age, len(fresh))

    fresh = [a for a in fresh if not store.is_posted(a)]
    log.info("Após filtro state_store (já postados): restantes=%s", len(fresh))

    if not fresh:
        log.error("Nenhum artigo elegível após filtros.")
        return False

    ranked = score_and_sort(fresh)
    top5 = ranked[:5]
    log.info("Top 5 por score:")
    for i, a in enumerate(top5, 1):
        log.info(
            "  %s. score=%s topic=%s source=%s title=%s",
            i,
            a.get("score"),
            a.get("topic"),
            a.get("source"),
            (a.get("title") or "")[:120],
        )

    best = ranked[0]
    log.info("Selecionado: score=%s %s", best.get("score"), (best.get("title") or "")[:160])

    if not config.OPENAI_API_KEY:
        log.error("OPENAI_API_KEY ausente — necessária para legenda e prompt de imagem.")
        return False

    builder = PostBuilder()
    caption = builder.build_caption(best)
    log.info("Legenda gerada (%s chars)", len(caption))
    print(f"Legenda (preview): {caption[:500]}...")

    if dry_run:
        log.info("Dry-run: pipeline visual e publicação não executados.")
        return True

    from visual.image_pipeline import build_post_image

    visual = build_post_image(best)
    if not visual:
        log.error("Falha no pipeline visual (notícia / marca / IA + template).")
        return False
    log.info(
        "Visual: fonte=%s quality=%s tempo=%ss",
        visual.source.value,
        visual.quality_score,
        visual.duration_sec,
    )

    ig = ImageGenerator()
    cloud_url = ig.upload_local_file_to_cloudinary(str(visual.path))
    if not cloud_url:
        log.error("Falha Cloudinary (upload arquivo local).")
        return False
    log.info("Cloudinary URL: %s", sanitize_url_for_log(cloud_url))

    poster = InstagramPoster()
    ok = poster.post_to_instagram(cloud_url, caption)

    if ok:
        store.record(
            url=best.get("url") or "",
            title=(best.get("title") or "").strip(),
            score=float(best.get("score") or 0),
            source=best.get("source") or "",
        )
        log.info("Publicado e registrado no state_store.")
    else:
        log.error("Falha na publicação Instagram.")

    return ok
