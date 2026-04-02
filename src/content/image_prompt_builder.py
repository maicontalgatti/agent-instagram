"""
Constrói prompt de imagem alinhado à notícia — composição + estética (não só título).
"""

from __future__ import annotations

from openai import OpenAI

import config
from models.article import Article
from utils.safe_log import safe_exc


class ImagePromptBuilder:
    """Gera um único prompt rico para DALL·E a partir do artigo + legenda."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def build(self, article: Article, caption: str) -> str:
        title = (article.get("title") or "")[:300]
        topic = article.get("topic") or "tech"
        description = (article.get("description") or "")[:600]
        source = article.get("source") or "news"

        system = """Você é diretor de arte para capas de newsletter de tecnologia.
Gere UM único parágrafo em português com instruções visuais para DALL-E 3.

Regras visuais obrigatórias:
- Composição minimalista, muito espaço negativo, uma ideia visual central.
- Luz suave, paleta neutra (branco, bege, cinza), no máximo um acento de cor.
- Sem texto, logotipos, letras ou marcas reconhecíveis na imagem.
- Sem poluição: nada de ícones flutuando, circuitos genéricos, código na tela, colagem futurista.
- Estilo: fotografia editorial de produto OU ilustração flat muito limpa.

O visual deve sugerir metaforicamente o tema (ex.: privacidade → silhueta abstrata; hardware → um único objeto bem iluminado)."""

        user = f"""Notícia (título): {title}
Tema classificado: {topic}
Fonte (apenas contexto, não desenhar o nome): {source}
Resumo: {description}

Legenda do post (referência de tom, não copiar texto na imagem):
{caption[:1200]}

Responda só com o prompt da imagem (3–5 frases), descrevendo cena, luz, enquadramento e materiais."""

        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=320,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro no image prompt builder: {safe_exc(e)}")
            return (
                "Fotografia minimalista em estúdio: único objeto tecnológico genérico (silhueta) "
                "sobre superfície clara, luz difusa lateral, fundo neutro desfocado, "
                "amplo espaço vazio, sem pessoas e sem texto na cena."
            )
