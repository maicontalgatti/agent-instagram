"""Orquestra legenda + prompt de imagem."""

from __future__ import annotations

from models.article import Article
from content.caption_generator import CaptionGenerator
from content.image_prompt_builder import ImagePromptBuilder


class PostBuilder:
    def __init__(self) -> None:
        self.captions = CaptionGenerator()
        self.images = ImagePromptBuilder()

    def build_caption(self, article: Article) -> str:
        return self.captions.generate_from_article(article)

    def build_image_prompt(self, article: Article, caption: str) -> str:
        return self.images.build(article, caption)
