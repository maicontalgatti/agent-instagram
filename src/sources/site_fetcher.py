"""
Scraping leve de sites — placeholder extensível.

Por padrão não faz requisições agressivas; retorne lista vazia ou
implemente fontes específicas com BeautifulSoup + requests.
"""

from __future__ import annotations

import logging

from models.article import Article

logger = logging.getLogger(__name__)


def fetch_site_stubs() -> list[Article]:
    """Reservado para futuras fontes HTML (lista de URLs, seletores, etc.)."""
    return []
