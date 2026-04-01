import sys
from pathlib import Path

from config import DEFAULT_POST_IMAGE_URL
from instagram_poster import InstagramPoster
from safe_log import sanitize_url_for_log

# True = não chama News API, OpenAI nem DALL-E; só testa postagem (Cloudinary opcional).
USE_MOCK_FOR_POST_TEST = False

DEFAULT_TEST_CAPTION = (
    "Post de teste do agente — conteúdo fixo para validar a publicação no Instagram. "
    "#Teste #AgentInstagram #Tech"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE_PATH = PROJECT_ROOT / "assets" / "default_post.png"
USED_TITLES_PATH = PROJECT_ROOT / "used_titles.txt"

# Ordem fixa: a cada execução sem argumento, avança para o próximo (persistido em disco).
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
    """Escolhe o próximo modo na rotação e grava o índice para a próxima execução."""
    idx = _read_mode_index()
    mode = ROTATION_SEQUENCE[idx]
    _write_mode_index(idx + 1)
    return mode


def resolve_run_mode() -> tuple[str, bool]:
    """
    Retorna (modo, usou_rotação_automática).
    Com argumento explícito (news | curiosity | trend): usa esse modo e não altera o índice da rotação.
    Sem argumento: usa rotação automática.
    """
    if len(sys.argv) > 1:
        manual = sys.argv[1].strip().lower()
        if manual in ROTATION_SEQUENCE:
            return manual, False
        print(
            f"Argumento '{sys.argv[1]}' desconhecido. "
            f"Opções: {', '.join(ROTATION_SEQUENCE)}. Usando rotação automática."
        )
    mode = get_rotated_mode()
    return mode, True


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
    content_generator,
    image_generator,
    instagram_poster: InstagramPoster,
) -> bool:
    print("Gerando prompt para a imagem...")
    image_prompt = content_generator.generate_image_prompt(caption)
    print(f"Prompt de imagem gerado: {image_prompt}")

    print("Gerando imagem com DALL-E...")
    dalle_image_url = image_generator.generate_image(image_prompt)

    if not dalle_image_url:
        print("Falha ao gerar imagem com DALL-E. Encerrando.")
        return False
    print(f"URL da imagem gerada pelo DALL-E: {sanitize_url_for_log(dalle_image_url)}")

    print("Fazendo upload da imagem para o Cloudinary...")
    cloudinary_url = image_generator.upload_image_to_cloudinary(dalle_image_url)

    if not cloudinary_url:
        print("Falha ao fazer upload da imagem para o Cloudinary. Encerrando.")
        return False
    print(f"URL da imagem no Cloudinary: {sanitize_url_for_log(cloudinary_url)}")

    print("Postando no Instagram...")
    return instagram_poster.post_to_instagram(cloudinary_url, caption)


def post_news(
    instagram_poster: InstagramPoster,
    content_generator,
    image_generator,
) -> None:
    from news_fetcher import NewsFetcher, filter_relevant_articles, pick_best_article

    news_fetcher = NewsFetcher()
    used = load_used_titles(USED_TITLES_PATH)

    print("Buscando notícias de tecnologia...")
    tech_news_articles = news_fetcher.fetch_tech_news(
        query="desenvolvimento de software OR inteligência artificial OR cibersegurança OR programação OR tecnologia"
    )

    tech_news_articles = filter_relevant_articles(tech_news_articles)
    tech_news_articles = [
        a
        for a in tech_news_articles
        if (a.get("title") or "").strip() and (a.get("title") or "").strip() not in used
    ]

    if not tech_news_articles:
        print("Nenhuma notícia relevante disponível (ou todas já foram usadas). Encerrando.")
        return

    selected_article = pick_best_article(tech_news_articles)
    title_key = (selected_article.get("title") or "").strip()
    print(f"Notícia escolhida (score): {title_key}")

    print("Gerando legenda para o Instagram...")
    caption = content_generator.generate_caption(selected_article)
    print(f"Legenda gerada: {caption}")

    success = run_image_post_pipeline(
        caption, content_generator, image_generator, instagram_poster
    )
    if success and title_key:
        record_used_title(USED_TITLES_PATH, title_key)
        print("Título registrado em used_titles.txt")
    elif not success:
        print("Falha na postagem do Instagram.")


def post_curiosity(
    instagram_poster: InstagramPoster,
    content_generator,
    image_generator,
) -> None:
    print("Modo curiosidade: gerando legenda...")
    caption = content_generator.generate_curiosity_caption()
    print(f"Legenda gerada: {caption}")

    success = run_image_post_pipeline(
        caption, content_generator, image_generator, instagram_poster
    )
    if not success:
        print("Falha na postagem do Instagram.")


def post_trend(
    instagram_poster: InstagramPoster,
    content_generator,
    image_generator,
) -> None:
    print("Modo tendência: gerando legenda...")
    caption = content_generator.generate_trend_caption()
    print(f"Legenda gerada: {caption}")

    success = run_image_post_pipeline(
        caption, content_generator, image_generator, instagram_poster
    )
    if not success:
        print("Falha na postagem do Instagram.")


def main():
    instagram_poster = InstagramPoster()

    if USE_MOCK_FOR_POST_TEST:
        print("Modo teste: APIs de notícias/conteúdo/imagem (OpenAI, News) desligadas.")
        caption = DEFAULT_TEST_CAPTION
        print(f"Legenda fixa: {caption}")

        if DEFAULT_POST_IMAGE_URL:
            image_url = DEFAULT_POST_IMAGE_URL
            print("Usando DEFAULT_POST_IMAGE_URL do .env (sem upload no Cloudinary).")
        else:
            from image_generator import ImageGenerator

            image_generator = ImageGenerator()
            print(f"Enviando imagem padrão para o Cloudinary: {DEFAULT_IMAGE_PATH}")
            image_url = image_generator.upload_local_file_to_cloudinary(
                str(DEFAULT_IMAGE_PATH)
            )

        if not image_url:
            print("Não foi possível obter URL pública da imagem. Encerrando.")
            return

        print("Postando no Instagram...")
        success = instagram_poster.post_to_instagram(image_url, caption)
        if success:
            print("Postagem no Instagram concluída com sucesso!")
        else:
            print("Falha na postagem do Instagram.")
        return

    from content_generator import ContentGenerator
    from image_generator import ImageGenerator

    content_generator = ContentGenerator()
    image_generator = ImageGenerator()

    mode, from_rotation = resolve_run_mode()
    label = MODE_LABELS.get(mode, mode)
    if from_rotation:
        print(f"Modo desta execução (rotação automática): {label} ({mode})")
    else:
        print(f"Modo desta execução (manual): {label} ({mode})")

    if mode == "curiosity":
        post_curiosity(instagram_poster, content_generator, image_generator)
    elif mode == "trend":
        post_trend(instagram_poster, content_generator, image_generator)
    else:
        post_news(instagram_poster, content_generator, image_generator)


if __name__ == "__main__":
    main()
