import random

from openai import OpenAI

from config import OPENAI_API_KEY
from safe_log import safe_exc

STYLES = ("noticia", "explicativo", "opiniao")

CTAS = (
    "O que você acha disso?",
    "Isso muda algo pra você?",
    "Você usaria isso?",
    "Comenta aqui 👇",
)


class ContentGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def _append_random_cta(self, caption: str) -> str:
        return caption.strip() + "\n\n" + random.choice(CTAS)

    def generate_caption(self, news_article, style=None):
        if style is None:
            style = random.choice(STYLES)

        title = news_article.get("title") or ""
        description = news_article.get("description") or ""
        url = news_article.get("url") or ""

        if style == "noticia":
            user_prompt = f"""Resuma essa notícia de forma direta e impactante para Instagram.

Título: {title}
Descrição: {description}
URL: {url}

Inclua hashtags relevantes. Legenda com no máximo 2200 caracteres."""
        elif style == "explicativo":
            user_prompt = f"""Explique essa notícia de forma simples para leigos, para Instagram.

Título: {title}
Descrição: {description}
URL: {url}

Inclua hashtags relevantes. Legenda com no máximo 2200 caracteres."""
        else:
            user_prompt = f"""Explique essa notícia e dê uma opinião provocativa (respeitosa), para Instagram.

Título: {title}
Descrição: {description}
URL: {url}

Inclua hashtags relevantes. Legenda com no máximo 2200 caracteres."""

        try:
            print(f"Variação de legenda (estilo): {style}")
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você escreve legendas para Instagram sobre tecnologia. "
                            "Varie o tom conforme o pedido; soe natural, não robótico."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=400,
            )
            base = response.choices[0].message.content.strip()
            return self._append_random_cta(base)
        except Exception as e:
            print(f"Erro ao gerar legenda: {safe_exc(e)}")
            fallback = (
                "Confira as últimas notícias de tecnologia! "
                "#Tecnologia #Inovação #DesenvolvimentoDeSoftware"
            )
            return self._append_random_cta(fallback)

    def generate_curiosity_caption(self) -> str:
        """Post estilo curiosidade ('Você sabia que...')."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você cria posts curtos de curiosidade sobre tecnologia para Instagram, tom leve e factual.",
                    },
                    {
                        "role": "user",
                        "content": (
                            "Escreva uma legenda de Instagram (máx. ~900 caracteres) começando com "
                            "'Você sabia que' sobre um fato interessante de IA, software ou hardware. "
                            "Inclua 3 a 6 hashtags em português."
                        ),
                    },
                ],
                max_tokens=350,
            )
            base = response.choices[0].message.content.strip()
            return self._append_random_cta(base)
        except Exception as e:
            print(f"Erro ao gerar legenda de curiosidade: {safe_exc(e)}")
            return self._append_random_cta(
                "Você sabia que a OpenAI treinou modelos com bilhões de parâmetros? 🤯 "
                "#Tech #IA #Curiosidade"
            )

    def generate_trend_caption(self) -> str:
        """Post sobre tendência ou futuro da tecnologia."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você comenta tendências de tecnologia para Instagram de forma acessível.",
                    },
                    {
                        "role": "user",
                        "content": (
                            "Escreva uma legenda de Instagram (máx. ~900 caracteres) sobre uma tendência "
                            "que pode moldar os próximos anos em tech (ex.: IA, energia, devices). "
                            "Tom conversacional. Inclua 3 a 6 hashtags em português."
                        ),
                    },
                ],
                max_tokens=350,
            )
            base = response.choices[0].message.content.strip()
            return self._append_random_cta(base)
        except Exception as e:
            print(f"Erro ao gerar legenda de tendência: {safe_exc(e)}")
            return self._append_random_cta(
                "Uma tendência que vem forte: mais automação no dia a dia com IA — o que isso muda pra você? "
                "#Tendências #Tech #Futuro"
            )

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
                model="gpt-4.1-mini",
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
        "url": "https://example.com/ai-news",
    }
    caption = generator.generate_caption(sample_news, style="noticia")
    print(f"Legenda gerada:\n{caption}")
    image_prompt = generator.generate_image_prompt(caption)
    print(f"Prompt de imagem gerado:\n{image_prompt}")
