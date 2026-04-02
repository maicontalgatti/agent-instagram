"""
Modo legado: rotação news / curiosity / trend.
"""

from __future__ import annotations

from pathlib import Path

from content.caption_generator import CaptionGenerator
from content.image_generator import ImageGenerator
from content.post_builder import PostBuilder
from models.article import Article
from publish.instagram_poster import InstagramPoster
from ranking.scorer import score_and_sort
from sources.keyword_filter import filter_relevant_articles
from sources.newsapi_fetcher import fetch_newsapi

PROJECT_ROOT = Path(__file__).resolve().parent.parent
USED_TITLES_PATH = PROJECT_ROOT / "used_titles.txt"
ROTATION_SEQUENCE = ("news", "curiosity", "trend")
MODE_INDEX_PATH = PROJECT_ROOT / "post_mode_index.txt"
MODE_LABELS = {
    "news": "notícias",
    "curiosity": "curiosidades",
    "trend": "tendências",
}


def _read_mode_index() -> int:
    if not MODE_INDEX_PATH.exists():
        return 0
    try:
        return int(MODE_INDEX_PATH.read_text(encoding="utf-8").strip()) % len(ROTATION_SEQUENCE)
    except ValueError:
        return 0


def _write_mode_index(idx: int) -> None:
    MODE_INDEX_PATH.write_text(str(idx % len(ROTATION_SEQUENCE)), encoding="utf-8")


def get_rotated_mode() -> str:
    idx = _read_mode_index()
    mode = ROTATION_SEQUENCE[idx]
    _write_mode_index(idx + 1)
    return mode


def load_used_titles(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def record_used_title(path: Path, title: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(title.strip() + "\n")


def run_image_post_pipeline(
    caption: str,
    builder: PostBuilder,
    image_generator: ImageGenerator,
    instagram_poster: InstagramPoster,
    article_stub: Article | None = None,
) -> bool:
    from utils.safe_log import sanitize_url_for_log

    stub: Article = article_stub or {
        "title": caption[:200],
        "description": caption,
        "url": "",
        "topic": "tech",
        "source": "legacy",
    }
    print("Gerando prompt para a imagem...")
    image_prompt = builder.build_image_prompt(stub, caption)
    print(f"Prompt de imagem gerado: {image_prompt}")

    print("Gerando imagem com DALL-E...")
    dalle_image_url = image_generator.generate_image(image_prompt)
    if not dalle_image_url:
        print("Falha ao gerar imagem com DALL-E.")
        return False
    print(f"URL DALL-E: {sanitize_url_for_log(dalle_image_url)}")

    cloudinary_url = image_generator.upload_image_to_cloudinary(dalle_image_url)
    if not cloudinary_url:
        print("Falha Cloudinary.")
        return False
    print(f"URL Cloudinary: {sanitize_url_for_log(cloudinary_url)}")

    print("Postando no Instagram...")
    return instagram_poster.post_to_instagram(cloudinary_url, caption)


def post_news_legacy(
    instagram_poster: InstagramPoster,
    caption_gen: CaptionGenerator,
    image_generator: ImageGenerator,
) -> None:
    builder = PostBuilder()
    used = load_used_titles(USED_TITLES_PATH)

    articles = fetch_newsapi()
    articles = filter_relevant_articles(articles)
    articles = [
        a
        for a in articles
        if (a.get("title") or "").strip() and (a.get("title") or "").strip() not in used
    ]
    if not articles:
        print("Nenhuma notícia relevante (NewsAPI) ou todas usadas.")
        return

    ranked = score_and_sort(articles)
    selected_article = ranked[0]
    title_key = (selected_article.get("title") or "").strip()
    print(f"Notícia escolhida: {title_key}")

    caption = caption_gen.generate_from_article(selected_article)
    print(f"Legenda: {caption[:400]}...")

    success = run_image_post_pipeline(
        caption, builder, image_generator, instagram_poster, article_stub=selected_article
    )
    if success and title_key:
        record_used_title(USED_TITLES_PATH, title_key)
        print("Título registrado em used_titles.txt")


def post_curiosity_legacy(
    instagram_poster: InstagramPoster,
    caption_gen: CaptionGenerator,
    image_generator: ImageGenerator,
) -> None:
    builder = PostBuilder()
    caption = caption_gen.generate_curiosity_caption()
    success = run_image_post_pipeline(caption, builder, image_generator, instagram_poster)
    if not success:
        print("Falha na postagem.")


def post_trend_legacy(
    instagram_poster: InstagramPoster,
    caption_gen: CaptionGenerator,
    image_generator: ImageGenerator,
) -> None:
    builder = PostBuilder()
    caption = caption_gen.generate_trend_caption()
    success = run_image_post_pipeline(caption, builder, image_generator, instagram_poster)
    if not success:
        print("Falha na postagem.")


def run_legacy(mode: str | None = None) -> None:
    caption_gen = CaptionGenerator()
    image_generator = ImageGenerator()
    instagram_poster = InstagramPoster()

    if mode is None:
        mode = get_rotated_mode()
        print(f"Modo (rotação automática): {MODE_LABELS.get(mode, mode)}")
    else:
        print(f"Modo (fixo): {MODE_LABELS.get(mode, mode)}")

    if mode == "curiosity":
        post_curiosity_legacy(instagram_poster, caption_gen, image_generator)
    elif mode == "trend":
        post_trend_legacy(instagram_poster, caption_gen, image_generator)
    else:
        post_news_legacy(instagram_poster, caption_gen, image_generator)
