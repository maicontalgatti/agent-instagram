from openai import OpenAI
import cloudinary
import cloudinary.uploader
from config import OPENAI_API_KEY, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
import requests

from safe_log import safe_exc, sanitize_url_for_log

# Reforço enviado ao DALL-E em toda geração (o modelo tende a imagens genéricas sem isso).
_DALLE_STYLE_SUFFIX = (
    "Estilo fixo: composição minimalista e clara, fundo neutro ou muito claro, "
    "poucos elementos, sem poluição visual, sem desenhos aleatórios ou ícones espalhados, "
    "sem texto, logotipos ou letras na imagem, luz suave, paleta calma."
)


class ImageGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )

    def generate_image(self, prompt):
        try:
            full_prompt = f"{prompt.strip()}\n\n{_DALLE_STYLE_SUFFIX}"
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"Erro ao gerar imagem com DALL-E: {safe_exc(e)}")
            return None

    def upload_image_to_cloudinary(self, image_url):
        try:
            # Download the image first
            response = requests.get(image_url)
            response.raise_for_status() # Raise an exception for HTTP errors
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(response.content, folder="instagram_posts")
            return upload_result["secure_url"]
        except Exception as e:
            print(f"Erro ao fazer upload da imagem para o Cloudinary: {safe_exc(e)}")
            return None

    def upload_local_file_to_cloudinary(self, local_path):
        try:
            upload_result = cloudinary.uploader.upload(local_path, folder="instagram_posts")
            return upload_result["secure_url"]
        except Exception as e:
            print(f"Erro ao enviar arquivo local para o Cloudinary: {safe_exc(e)}")
            return None

if __name__ == "__main__":
    generator = ImageGenerator()
    sample_prompt = (
        "Fotografia simples: apenas um laptop em ângulo suave sobre mesa clara, "
        "fundo desfocado neutro, luz de estúdio suave, muito espaço vazio, sem pessoas."
    )
    dalle_image_url = generator.generate_image(sample_prompt)
    if dalle_image_url:
        print(f"URL da imagem gerada pelo DALL-E: {sanitize_url_for_log(dalle_image_url)}")
        cloudinary_url = generator.upload_image_to_cloudinary(dalle_image_url)
        if cloudinary_url:
            print(f"URL da imagem no Cloudinary: {sanitize_url_for_log(cloudinary_url)}")
    else:
        print("Falha ao gerar ou fazer upload da imagem.")
