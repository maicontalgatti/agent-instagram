"""
Registro central de fontes RSS e NewsAPI.
Adicione/remova entradas aqui sem espalhar URLs pelo código.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SourceKind = Literal["rss", "newsapi", "site"]


@dataclass(frozen=True)
class SourceDefinition:
    id: str
    kind: SourceKind
    name: str
    # RSS: URL do feed | NewsAPI: ignorado | site: URL base (futuro)
    endpoint: str
    limit: int = 25


# Feeds públicos conhecidos (podem mudar; ajuste se algum falhar).
DEFAULT_RSS_SOURCES: tuple[SourceDefinition, ...] = (
    SourceDefinition("techcrunch", "rss", "TechCrunch", "https://techcrunch.com/feed/", 25),
    SourceDefinition("the_verge", "rss", "The Verge", "https://www.theverge.com/rss/index.xml", 25),
    SourceDefinition("wired", "rss", "Wired", "https://www.wired.com/feed/rss", 20),
    SourceDefinition(
        "arstechnica", "rss", "Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", 25
    ),
    SourceDefinition("venturebeat", "rss", "VentureBeat", "https://venturebeat.com/feed/", 20),
    SourceDefinition(
        "technologyreview",
        "rss",
        "MIT Technology Review",
        "https://www.technologyreview.com/feed/",
        20,
    ),
)


def get_all_sources() -> tuple[SourceDefinition, ...]:
    """Ponto único de leitura."""
    return DEFAULT_RSS_SOURCES
