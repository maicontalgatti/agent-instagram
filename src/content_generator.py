from openai import OpenAI

from config import OPENAI_API_KEY
from safe_log import safe_exc

class ContentGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_caption(self, news_article):
        prompt = f"""Com base na seguinte notícia de tecnologia, crie uma legenda curta e envolvente para um post do Instagram. Inclua hashtags relevantes. A legenda deve ter no máximo 2200 caracteres.

Título: {news_article["title"]}
Descrição: {news_article["description"]}
URL: {news_article["url"]}

Legenda:"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini", # Using a more capable model for better content generation
                messages=[
                    {"role": "system", "content": "Você é um assistente de marketing digital especializado em posts de tecnologia para Instagram."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro ao gerar legenda: {safe_exc(e)}")
            return """
            Confira as últimas notícias de tecnologia! Fique por dentro das inovações e tendências que estão moldando o futuro. #Tecnologia #Inovação #DesenvolvimentoDeSoftware
            """

    def generate_image_prompt(self, caption):
        prompt = f"""Legenda do post (tecnologia): {caption}

Escreva um único prompt em português para o DALL-E gerar a imagem de capa deste post.

Regras obrigatórias do prompt:
- Visual simples, claro e com pouca informação: muito espaço vazio, poucos objetos, uma ideia central.
- Evite: desenhos aleatórios, ícones espalhados, circuitos, hologramas, código flutuando, robôs caricatos, colagem futurista genérica, poluição visual.
- Prefira: fotografia realista minimalista OU ilustração flat muito enxuta; fundo claro ou neutro; luz suave; paleta calma (branco, bege, cinza-claro, no máximo um acento de cor).
- Proibido texto, logotipos ou letras na imagem.

Responda só com o prompt da imagem (2 a 4 frases curtas), sem aspas nem comentários."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini", # Using a more capable model for better content generation
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você cria prompts para DALL-E com estética editorial minimalista: "
                            "limpo, respirável, poucos elementos, nada de 'wallpaper de tecnologia' genérico."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=180,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro ao gerar prompt de imagem: {safe_exc(e)}")
            return (
                "Fotografia minimalista em tons claros: uma mesa de madeira clara com um único laptop "
                "fechado e uma xícara de café, luz natural suave pela janela, fundo desfocado neutro, "
                "muito espaço negativo, estética calma e editorial, sem pessoas e sem texto na imagem."
            )

if __name__ == "__main__":
    generator = ContentGenerator()
    sample_news = {
        "title": "Novos avanços em Inteligência Artificial",
        "description": "Pesquisadores desenvolveram um novo algoritmo de IA que promete revolucionar o processamento de linguagem natural.",
        "url": "https://example.com/ai-news"
    }
    caption = generator.generate_caption(sample_news)
    print(f"Legenda gerada:\n{caption}")
    image_prompt = generator.generate_image_prompt(caption)
    print(f"Prompt de imagem gerado:\n{image_prompt}")
