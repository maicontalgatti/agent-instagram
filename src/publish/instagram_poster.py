import json
import time

import requests

import config
from utils.safe_log import format_http_body_for_log, safe_exc, sanitize_json_obj

GRAPH_API_VERSION = "v18.0"
MEDIA_INITIAL_WAIT_SEC = 10
STATUS_POLL_INTERVAL_SEC = 3
STATUS_POLL_MAX_ATTEMPTS = 10
GRAPH_POST_RETRIES = 4
GRAPH_POST_BACKOFF_SEC = 5


def _should_retry_graph_response(status_code: int, body_json: dict | None) -> bool:
    if status_code >= 500:
        return True
    if not body_json:
        return status_code >= 500
    err = body_json.get("error") or {}
    if err.get("is_transient"):
        return True
    if err.get("code") in (1, 2, 4):  # comuns em falhas temporárias / rate
        return True
    return False


class InstagramPoster:
    def __init__(self) -> None:
        self.access_token = config.INSTAGRAM_ACCESS_TOKEN
        self.ig_id = config.INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.graph_base = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def create_media_object(self, image_url: str, caption: str):
        endpoint = f"{self.graph_base}/{self.ig_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }
        last_response = None
        for attempt in range(1, GRAPH_POST_RETRIES + 1):
            try:
                response = requests.post(endpoint, data=payload, timeout=90)
                last_response = response
                print(f"Resposta criação de mídia: {format_http_body_for_log(response.text)}")
                try:
                    data = response.json()
                except ValueError:
                    data = {}
                media_id = data.get("id")
                if media_id:
                    return media_id
                if _should_retry_graph_response(response.status_code, data) and attempt < GRAPH_POST_RETRIES:
                    print(
                        f"Retentativa criação de mídia {attempt}/{GRAPH_POST_RETRIES} "
                        f"(erro possivelmente temporário da Meta)…"
                    )
                    time.sleep(GRAPH_POST_BACKOFF_SEC * attempt)
                    continue
                print(f"Erro ao criar objeto de mídia (HTTP {response.status_code})")
                print(
                    "Resposta da API:",
                    json.dumps(sanitize_json_obj(data), ensure_ascii=False),
                )
                return None
            except requests.exceptions.RequestException as e:
                print(f"Erro de rede ao criar mídia: {safe_exc(e)}")
                if attempt < GRAPH_POST_RETRIES:
                    time.sleep(GRAPH_POST_BACKOFF_SEC * attempt)
                    continue
                if last_response is not None:
                    try:
                        print(
                            "Resposta da API:",
                            json.dumps(sanitize_json_obj(last_response.json()), ensure_ascii=False),
                        )
                    except Exception:
                        print(f"Corpo bruto: {format_http_body_for_log(last_response.text)}")
                return None
        return None

    def wait_until_media_ready(self, creation_id: str) -> bool:
        print("Aguardando processamento da mídia...")
        time.sleep(MEDIA_INITIAL_WAIT_SEC)

        status_url = f"{self.graph_base}/{creation_id}"
        status_params = {
            "fields": "status_code",
            "access_token": self.access_token,
        }

        status_code = None
        for attempt in range(STATUS_POLL_MAX_ATTEMPTS):
            try:
                status_res = requests.get(status_url, params=status_params, timeout=30)
                print(
                    f"Status da mídia (tentativa {attempt + 1}/{STATUS_POLL_MAX_ATTEMPTS}): "
                    f"{format_http_body_for_log(status_res.text)}"
                )
                status_res.raise_for_status()
                status_json = status_res.json()
            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"Erro ao consultar status da mídia: {safe_exc(e)}")
                return False

            status_code = status_json.get("status_code")
            print(f"status_code: {status_code}")

            if status_code == "FINISHED":
                print("Mídia pronta para publicar.")
                return True

            time.sleep(STATUS_POLL_INTERVAL_SEC)

        print("A mídia não ficou pronta a tempo (status_code != FINISHED).")
        return False

    def publish_media(self, creation_id: str):
        endpoint = f"{self.graph_base}/{self.ig_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        last_response = None
        for attempt in range(1, GRAPH_POST_RETRIES + 1):
            try:
                response = requests.post(endpoint, data=payload, timeout=90)
                last_response = response
                print(f"Resposta publicação: {format_http_body_for_log(response.text)}")
                try:
                    data = response.json()
                except ValueError:
                    data = {}
                pub_id = data.get("id")
                if pub_id:
                    return pub_id
                if _should_retry_graph_response(response.status_code, data) and attempt < GRAPH_POST_RETRIES:
                    print(
                        f"Retentativa publicação {attempt}/{GRAPH_POST_RETRIES} "
                        f"(erro possivelmente temporário da Meta)…"
                    )
                    time.sleep(GRAPH_POST_BACKOFF_SEC * attempt)
                    continue
                print(f"Erro ao publicar mídia (HTTP {response.status_code})")
                print(
                    "Resposta da API:",
                    json.dumps(sanitize_json_obj(data), ensure_ascii=False),
                )
                return None
            except requests.exceptions.RequestException as e:
                print(f"Erro de rede ao publicar: {safe_exc(e)}")
                if attempt < GRAPH_POST_RETRIES:
                    time.sleep(GRAPH_POST_BACKOFF_SEC * attempt)
                    continue
                if last_response is not None:
                    try:
                        print(
                            "Resposta da API:",
                            json.dumps(sanitize_json_obj(last_response.json()), ensure_ascii=False),
                        )
                    except Exception:
                        print(f"Corpo bruto: {format_http_body_for_log(last_response.text)}")
                return None
        return None

    def post_to_instagram(self, image_url: str, caption: str) -> bool:
        print("Criando objeto de mídia...")
        creation_id = self.create_media_object(image_url, caption)
        if not creation_id:
            print("Falha ao criar mídia.")
            return False

        print(f"Objeto de mídia criado: {creation_id}")

        if not self.wait_until_media_ready(creation_id):
            return False

        print("Publicando mídia...")
        publish_id = self.publish_media(creation_id)
        if publish_id:
            print(f"Mídia publicada com sucesso! Post ID: {publish_id}")
            return True

        print("Falha ao publicar no Instagram.")
        return False
