from pathlib import Path

from config import DEFAULT_POST_IMAGE_URL
from instagram_poster import InstagramPoster

# True = não chama News API, OpenAI nem DALL-E; só testa postagem (Cloudinary opcional).
USE_MOCK_FOR_POST_TEST = True

DEFAULT_TEST_CAPTION = (
    "Post de teste do agente — conteúdo fixo para validar a publicação no Instagram. "
    "#Teste #AgentInstagram #Tech"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE_PATH = PROJECT_ROOT / "assets" / "default_post.png"


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

    # Fluxo completo (News API + OpenAI + DALL-E + Cloudinary)
    from news_fetcher import NewsFetcher
    from content_generator import ContentGenerator
    from image_generator import ImageGenerator
    import random

    news_fetcher = NewsFetcher()
    content_generator = ContentGenerator()
    image_generator = ImageGenerator()

    # 1. Buscar notícias de tecnologia
    print("Buscando notícias de tecnologia...")
    tech_news_articles = news_fetcher.fetch_tech_news(
        query="desenvolvimento de software OR inteligãncia artificial OR cibersegurança OR programação OR tecnologia"
    )

    if not tech_news_articles:
        print("Nenhuma notícia de tecnologia encontrada. Encerrando.")
        return

    # 2. Selecionar uma notícia aleatoriamente
    selected_article = random.choice(tech_news_articles)
    print(f'Notícia selecionada: {selected_article["title"]}')

    # 3. Gerar legenda para o Instagram
    print("Gerando legenda para o Instagram...")
    caption = content_generator.generate_caption(selected_article)
    print(f"Legenda gerada: {caption}")

    # 4. Gerar prompt para a imagem
    print("Gerando prompt para a imagem...")
    image_prompt = content_generator.generate_image_prompt(caption)
    print(f"Prompt de imagem gerado: {image_prompt}")

    # 5. Gerar imagem com DALL-E
    print("Gerando imagem com DALL-E...")
    dalle_image_url = image_generator.generate_image(image_prompt)

    if not dalle_image_url:
        print("Falha ao gerar imagem com DALL-E. Encerrando.")
        return
    print(f"URL da imagem gerada pelo DALL-E: {dalle_image_url}")

    # 6. Fazer upload da imagem para o Cloudinary
    print("Fazendo upload da imagem para o Cloudinary...")
    cloudinary_url = image_generator.upload_image_to_cloudinary(dalle_image_url)

    if not cloudinary_url:
        print("Falha ao fazer upload da imagem para o Cloudinary. Encerrando.")
        return
    print(f"URL da imagem no Cloudinary: {cloudinary_url}")

    # 7. Postar no Instagram
    print("Postando no Instagram...")
    success = instagram_poster.post_to_instagram(cloudinary_url, caption)

    if success:
        print("Postagem no Instagram concluída com sucesso!")
    else:
        print("Falha na postagem do Instagram.")


if __name__ == "__main__":
    main()
