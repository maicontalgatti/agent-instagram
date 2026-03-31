from news_fetcher import NewsFetcher
from content_generator import ContentGenerator
from image_generator import ImageGenerator
from instagram_poster import InstagramPoster
import random

def main():
    news_fetcher = NewsFetcher()
    content_generator = ContentGenerator()
    image_generator = ImageGenerator()
    instagram_poster = InstagramPoster()

    # 1. Buscar notícias de tecnologia
    print("Buscando notícias de tecnologia...")
    tech_news_articles = news_fetcher.fetch_tech_news(query='desenvolvimento de software OR inteligãncia artificial OR cibersegurança OR programação OR tecnologia')

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
