from openai import OpenAI
from config import OPENAI_API_KEY

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
            print(f"Erro ao gerar legenda: {e}")
            return """
            Confira as últimas notícias de tecnologia! Fique por dentro das inovações e tendências que estão moldando o futuro. #Tecnologia #Inovação #DesenvolvimentoDeSoftware
            """

    def generate_image_prompt(self, caption):
        prompt = f"""Com base na seguinte legenda do Instagram sobre tecnologia, crie um prompt detalhado para gerar uma imagem visualmente atraente e relevante usando DALL-E. O prompt deve ser descritivo e focar em elementos visuais.

Legenda: {caption}

Prompt para imagem:"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini", # Using a more capable model for better content generation
                messages=[
                    {"role": "system", "content": "Você é um gerador de prompts de imagem para DALL-E, especializado em conceitos de tecnologia."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro ao gerar prompt de imagem: {e}")
            return """Uma imagem abstrata representando tecnologia, com elementos de código, circuitos e luzes brilhantes, em tons de azul e roxo.
            """

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
