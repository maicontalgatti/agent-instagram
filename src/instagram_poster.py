import requests
from config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID

class InstagramPoster:
    def __init__(self):
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        self.page_id = INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.graph_url = "https://graph.facebook.com/v19.0/"

    def create_media_object(self, image_url, caption):
        endpoint = f"{self.graph_url}{self.page_id}/media"
        params = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        try:
            response = requests.post(endpoint, params=params)
            response.raise_for_status()
            return response.json()["id"]
        except requests.exceptions.RequestException as e:
            print(f"Erro ao criar objeto de mídia: {e}")
            if response:
                print(f"Resposta da API: {response.json()}")
            return None

    def publish_media(self, creation_id):
        endpoint = f"{self.graph_url}{self.page_id}/media_publish"
        params = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        try:
            response = requests.post(endpoint, params=params)
            response.raise_for_status()
            return response.json()["id"]
        except requests.exceptions.RequestException as e:
            print(f"Erro ao publicar mídia: {e}")
            if response:
                print(f"Resposta da API: {response.json()}")
            return None

    def post_to_instagram(self, image_url, caption):
        print("Criando objeto de mídia...")
        media_object_id = self.create_media_object(image_url, caption)
        if media_object_id:
            print(f"Objeto de mídia criado com ID: {media_object_id}")
            print("Publicando mídia...")
            publish_id = self.publish_media(media_object_id)
            if publish_id:
                print(f"Mídia publicada com sucesso! Post ID: {publish_id}")
                return True
        print("Falha ao postar no Instagram.")
        return False

if __name__ == "__main__":
    # Este bloco só funcionará com as credenciais corretas do Instagram
    # e uma URL de imagem válida. Use para testes locais.
    poster = InstagramPoster()
    sample_image_url = "https://res.cloudinary.com/your_cloud_name/image/upload/v123456789/instagram_posts/sample_image.jpg"
    sample_caption = "Este é um post de teste automatizado! #Teste #InstagramAPI"
    # poster.post_to_instagram(sample_image_url, sample_caption)
    print("Para testar, descomente as linhas acima e forneça credenciais válidas no .env")
