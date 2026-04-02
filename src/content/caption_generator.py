"""Legendas estilo tech news para Instagram."""

from __future__ import annotations

import random
import re

from openai import OpenAI

import config
from models.article import Article
from utils.safe_log import safe_exc

STYLES = ("noticia", "explicativo", "opiniao")

# Frases proibidas (case-insensitive)
_FORBIDDEN_PATTERNS = (
    re.compile(r"confira\s+o\s+link\s+na\s+bio", re.I),
    re.compile(r"confira\s+na\s+bio", re.I),
    re.compile(r"link\s+na\s+bio", re.I),
    re.compile(r"acesse\s+o\s+link\s+na\s+bio", re.I),
    re.compile(r"veja\s+o\s+link\s+na\s+bio", re.I),
)


def _remove_forbidden_phrases(text: str) -> str:
    out = text
    for pat in _FORBIDDEN_PATTERNS:
        out = pat.sub("", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    return out.strip()

CTAS = (
    "O que você acha disso?",
    "Isso muda algo pra você?",
    "Você usaria isso?",
    "Comenta aqui 👇",
)


class CaptionGenerator:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def _append_random_cta(self, caption: str) -> str:
        return _remove_forbidden_phrases(caption.strip()) + "\n\n" + random.choice(CTAS)

    def generate_from_article(self, article: Article, style: str | None = None) -> str:
        if style is None:
            style = random.choice(STYLES)

        title = article.get("title") or ""
        description = article.get("description") or ""
        url = article.get("url") or ""
        topic = article.get("topic") or "tech"
        source = article.get("source") or ""

        if style == "noticia":
            user_prompt = f"""Escreva uma legenda para Instagram no estilo **tech news** — direta, clara, impactante.

Contexto editorial:
- Tema detectado: {topic}
- Fonte: {source}
- Título: {title}
- Resumo: {description}

Regras obrigatórias:
- NÃO use a frase "confira o link na bio" nem variações (link na bio, veja na bio, etc.).
- Não cole URL cru na legenda.

Inclua hashtags relevantes (PT/EN misturado é ok). Máximo ~2200 caracteres."""
        elif style == "explicativo":
            user_prompt = f"""Explique essa notícia de tecnologia de forma simples para quem não é da área — tom didático, Instagram.

Tema: {topic}
Título: {title}
Resumo: {description}

NÃO escreva "confira o link na bio" nem "link na bio".
Inclua hashtags. Máximo ~2200 caracteres."""
        else:
            user_prompt = f"""Dê uma opinião fundamentada e provocativa (respeitosa) sobre esta notícia de tech.

Tema: {topic}
Título: {title}
Resumo: {description}

NÃO escreva "confira o link na bio" nem "link na bio".
Inclua hashtags. Máximo ~2200 caracteres."""

        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é editor de uma conta de tecnologia no Instagram: voz moderna, limpa, "
                            "sem sensacionalismo vazio. Varie estrutura e ritmo entre posts. "
                            "Nunca use a expressão 'confira o link na bio' nem equivalentes sobre link na bio."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
            )
            base = _remove_forbidden_phrases(response.choices[0].message.content.strip())
            return self._append_random_cta(base)
        except Exception as e:
            print(f"Erro ao gerar legenda: {safe_exc(e)}")
            return self._append_random_cta(
                _remove_forbidden_phrases(f"{title}\n\n{description[:400]}\n\n#Tech #News")
            )

    def generate_curiosity_caption(self) -> str:
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você cria posts curtos de curiosidade sobre tecnologia para Instagram. "
                            "Nunca use 'confira o link na bio' nem 'link na bio'."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Escreva uma legenda (máx. ~900 caracteres) começando com "
                            "'Você sabia que' sobre IA, software ou hardware. 3–6 hashtags PT."
                        ),
                    },
                ],
                max_tokens=350,
            )
            base = _remove_forbidden_phrases(response.choices[0].message.content.strip())
            return self._append_random_cta(base)
        except Exception as e:
            print(f"Erro curiosidade: {safe_exc(e)}")
            return self._append_random_cta(
                "Você sabia que modelos modernos usam bilhões de parâmetros? 🤯 #Tech #IA"
            )

    def generate_trend_caption(self) -> str:
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você comenta tendências de tecnologia para Instagram. "
                            "Nunca use 'confira o link na bio' nem 'link na bio'."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Legenda ~900 caracteres sobre tendência tech nos próximos anos. "
                            "Tom conversacional. 3–6 hashtags PT."
                        ),
                    },
                ],
                max_tokens=350,
            )
            base = _remove_forbidden_phrases(response.choices[0].message.content.strip())
            return self._append_random_cta(base)
        except Exception as e:
            print(f"Erro tendência: {safe_exc(e)}")
            return self._append_random_cta(
                "Uma tendência forte: mais automação com IA no dia a dia. #Tendências #Tech"
            )
