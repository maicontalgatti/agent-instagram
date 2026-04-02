"""Configuração central: env, fontes, pesos e limites do pipeline editorial."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STATE_FILE = DATA_DIR / "editorial_state.json"
RSS_CACHE_DIR = DATA_DIR / "rss_cache"

# --- API keys ---
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
DEFAULT_POST_IMAGE_URL = os.getenv("DEFAULT_POST_IMAGE_URL")

# --- Editorial pipeline ---
PREFERRED_LANGUAGE = os.getenv("EDITORIAL_LANGUAGE", "pt")

# Janela: artigos mais velhos que isso são descartados na seleção (horas)
MAX_ARTICLE_AGE_HOURS = float(os.getenv("MAX_ARTICLE_AGE_HOURS", "72"))

# Meia-vida em horas para decaimento de frescor (após 24h ainda forte; depois cai suave)
FRESHNESS_HALF_LIFE_HOURS = float(os.getenv("FRESHNESS_HALF_LIFE_HOURS", "18"))

# Limite de artigos brutos por fonte em uma execução
DEFAULT_PER_SOURCE_LIMIT = int(os.getenv("PER_SOURCE_LIMIT", "25"))

# NewsAPI: query ampla em inglês costuma retornar mais matéria internacional tech
NEWSAPI_QUERY = os.getenv(
    "NEWSAPI_QUERY",
    "(technology OR AI OR startup OR software OR cybersecurity OR gadget) AND "
    "(Apple OR Google OR Microsoft OR OpenAI OR Meta OR Amazon OR Tesla OR Samsung)",
)
NEWSAPI_LANGUAGE = os.getenv("NEWSAPI_LANGUAGE", "en")
NEWSAPI_PAGE_SIZE = int(os.getenv("NEWSAPI_PAGE_SIZE", "40"))

# Pesos do score (ajustáveis)
SCORE_WEIGHTS: dict[str, float] = {
    "freshness": float(os.getenv("SCORE_W_FRESHNESS", "35")),
    "keyword_priority": float(os.getenv("SCORE_W_KEYWORD", "25")),
    "title_strength": float(os.getenv("SCORE_W_TITLE", "12")),
    "topic_priority": float(os.getenv("SCORE_W_TOPIC", "15")),
    "source_trust": float(os.getenv("SCORE_W_SOURCE", "10")),
    "engagement_hint": float(os.getenv("SCORE_W_ENGAGEMENT", "8")),
}

# Palavras que elevam relevância editorial (case-insensitive match)
PRIORITY_KEYWORDS: tuple[str, ...] = (
    "openai",
    "gpt",
    "gemini",
    "apple",
    "google",
    "microsoft",
    "meta",
    "nvidia",
    "ai",
    "artificial intelligence",
    "machine learning",
    "security",
    "breach",
    "launch",
    "iphone",
    "android",
    "startup",
    "acquisition",
    "regulation",
    "eu ",
    "china",
)

# Tópicos e peso extra quando classificado
TOPIC_PRIORITY_WEIGHT: dict[str, float] = {
    "ai": 1.35,
    "big_tech": 1.25,
    "cybersecurity": 1.2,
    "startups": 1.15,
    "regulation": 1.1,
    "software": 1.08,
    "gadgets": 1.05,
    "social_media": 1.05,
    "other": 1.0,
}

# Confiança por slug de fonte (multiplicador parcial aplicado em scorer)
SOURCE_TRUST: dict[str, float] = {
    "techcrunch": 1.15,
    "the_verge": 1.12,
    "wired": 1.12,
    "arstechnica": 1.1,
    "venturebeat": 1.08,
    "technologyreview": 1.14,
    "newsapi": 0.95,
    "unknown": 0.9,
}

# Similaridade mínima de título para considerar duplicata (0–1)
TITLE_SIMILARITY_THRESHOLD = float(os.getenv("TITLE_SIMILARITY_THRESHOLD", "0.86"))

# OpenAI
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
