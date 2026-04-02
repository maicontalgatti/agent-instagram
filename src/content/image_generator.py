"""DALL·E + Cloudinary."""

from __future__ import annotations

import requests
import cloudinary
import cloudinary.uploader
from openai import OpenAI

import config
from utils.safe_log import safe_exc, sanitize_url_for_log

_DALLE_STYLE_SUFFIX = (
    "Estilo fixo: composição minimalista e clara, fundo neutro ou muito claro, "
    "poucos elementos, sem poluição visual, sem desenhos aleatórios ou ícones espalhados, "
    "sem texto, logotipos ou letras na imagem, luz suave, paleta calma."
)

# Fallback do pipeline visual (capa editorial — não abstrato)
_EDITORIAL_IMAGE_SUFFIX = (
    "Photorealistic editorial photograph for a technology news magazine. "
    "Real environment, single clear subject, credible scene, professional lighting, "
    "high detail. No text, no watermark, no logos in the frame, no abstract art."
)


class ImageGenerator:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        cloudinary.config(
            cloud_name=config.CLOUDINARY_CLOUD_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
        )

    def generate_image(self, prompt: str) -> str | None:
        try:
            full_prompt = f"{prompt.strip()}\n\n{_DALLE_STYLE_SUFFIX}"
            response = self.client.images.generate(
                model=config.OPENAI_IMAGE_MODEL,
                prompt=full_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            print(f"Erro ao gerar imagem com DALL-E: {safe_exc(e)}")
            return None

    def generate_editorial_image(self, prompt: str) -> str | None:
        """Imagem para capa editorial (sem sufixo minimalista genérico)."""
        try:
            full_prompt = f"{prompt.strip()}\n\n{_EDITORIAL_IMAGE_SUFFIX}"
            response = self.client.images.generate(
                model=config.OPENAI_IMAGE_MODEL,
                prompt=full_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            print(f"Erro ao gerar imagem editorial (DALL-E): {safe_exc(e)}")
            return None

    def upload_image_to_cloudinary(self, image_url: str) -> str | None:
        try:
            response = requests.get(image_url, timeout=120)
            response.raise_for_status()
            upload_result = cloudinary.uploader.upload(response.content, folder="instagram_posts")
            return upload_result["secure_url"]
        except Exception as e:
            print(f"Erro ao fazer upload da imagem para o Cloudinary: {safe_exc(e)}")
            return None

    def upload_local_file_to_cloudinary(self, local_path: str) -> str | None:
        try:
            upload_result = cloudinary.uploader.upload(local_path, folder="instagram_posts")
            return upload_result["secure_url"]
        except Exception as e:
            print(f"Erro ao enviar arquivo local para o Cloudinary: {safe_exc(e)}")
            return None
