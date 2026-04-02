"""
Teste mínimo: só Graph API do Instagram (imagem pública fixa).
Uso na raiz do projeto: python src/instagram_tester.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from dotenv import load_dotenv

load_dotenv(_PROJECT_ROOT / ".env")

import requests

from utils.safe_log import credentials_loaded_hint, format_http_body_for_log

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

print(credentials_loaded_hint(ACCESS_TOKEN, IG_ID))

if not ACCESS_TOKEN or not IG_ID:
    print("ACCESS_TOKEN ou IG_ID não carregados do .env (caminho esperado:", _PROJECT_ROOT / ".env", ")")
    raise SystemExit(1)

# Imagem pública estável (Cloudinary demo — aceita pela Graph API)
IMAGE_URL = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
CAPTION = "Teste automático #teste #api #instagram"

GRAPH_VERSION = "v18.0"
MAX_RETRIES = 4
BACKOFF_SEC = 5


def _post_media_with_retries() -> str | None:
    media_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{IG_ID}/media"
    media_payload = {
        "image_url": IMAGE_URL,
        "caption": CAPTION,
        "access_token": ACCESS_TOKEN,
    }
    for attempt in range(1, MAX_RETRIES + 1):
        media_res = requests.post(media_url, data=media_payload, timeout=90)
        print("MEDIA RESPONSE:", format_http_body_for_log(media_res.text))
        try:
            media_json = media_res.json()
        except Exception:
            print("Não foi possível ler JSON da criação de mídia.")
            if attempt < MAX_RETRIES:
                print(f"Tentativa {attempt}/{MAX_RETRIES} — aguardando {BACKOFF_SEC}s…")
                time.sleep(BACKOFF_SEC)
            continue

        creation_id = media_json.get("id")
        if creation_id:
            return str(creation_id)

        err = media_json.get("error") or {}
        transient = err.get("is_transient") is True
        code = err.get("code")
        if transient or code == 2 or media_res.status_code >= 500:
            print(
                f"Erro (possivelmente temporário da Meta). "
                f"Tentativa {attempt}/{MAX_RETRIES}. is_transient={transient} code={code}"
            )
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_SEC * attempt)
            continue
        print("ERRO ao criar mídia (não retentável ou resposta sem id).")
        return None
    return None


creation_id = _post_media_with_retries()
if not creation_id:
    raise SystemExit(1)

print(f"Objeto de mídia criado: {creation_id}")
print("Aguardando processamento da mídia…")
time.sleep(10)

status_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{creation_id}"
status_params = {
    "fields": "status_code",
    "access_token": ACCESS_TOKEN,
}

status_code = None
for tentativa in range(10):
    status_res = requests.get(status_url, params=status_params, timeout=60)
    print("STATUS RESPONSE:", format_http_body_for_log(status_res.text))
    try:
        status_json = status_res.json()
    except Exception:
        print("Não foi possível ler o status da mídia.")
        raise SystemExit(1)

    status_code = status_json.get("status_code")
    print(f"Tentativa {tentativa + 1}/10 - status: {status_code}")
    if status_code == "FINISHED":
        print("Mídia pronta para publicar.")
        break

    time.sleep(3)

if status_code != "FINISHED":
    print("A mídia não ficou pronta a tempo. Tente novamente.")
    raise SystemExit(1)

publish_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{IG_ID}/media_publish"
publish_payload = {
    "creation_id": creation_id,
    "access_token": ACCESS_TOKEN,
}

publish_res = requests.post(publish_url, data=publish_payload, timeout=90)
print("PUBLISH RESPONSE:", format_http_body_for_log(publish_res.text))

try:
    publish_json = publish_res.json()
except Exception:
    print("Não foi possível ler a resposta de publicação.")
    raise SystemExit(1)

if publish_json.get("id"):
    print("Post publicado com sucesso!")
else:
    print("Erro ao publicar.")
