from openai import OpenAI
import cloudinary
import cloudinary.uploader
from config import OPENAI_API_KEY, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
import requests

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
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"Erro ao gerar imagem com DALL-E: {e}")
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
            print(f"Erro ao fazer upload da imagem para o Cloudinary: {e}")
            return None

if __name__ == "__main__":
    generator = ImageGenerator()
    sample_prompt = "Um robô programando em um laptop, com código flutuando ao redor, estilo futurista e cores vibrantes."
    dalle_image_url = generator.generate_image(sample_prompt)
    if dalle_image_url:
        print(f"URL da imagem gerada pelo DALL-E: {dalle_image_url}")
        cloudinary_url = generator.upload_image_to_cloudinary(dalle_image_url)
        if cloudinary_url:
            print(f"URL da imagem no Cloudinary: {cloudinary_url}")
    else:
        print("Falha ao gerar ou fazer upload da imagem.")
