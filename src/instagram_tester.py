from dotenv import load_dotenv
load_dotenv()

import os
import time
import requests

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

print("ACCESS_TOKEN:", ACCESS_TOKEN[:20] if ACCESS_TOKEN else None)
print("IG_ID:", IG_ID)

if not ACCESS_TOKEN or not IG_ID:
    print("ACCESS_TOKEN ou IG_ID não carregados do .env")
    raise SystemExit(1)

# Imagem publica fixa para teste
IMAGE_URL = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
CAPTION = "Teste automatico #teste #api #instagram"

# 1. Criar midia
media_url = f"https://graph.facebook.com/v18.0/{IG_ID}/media"
media_payload = {
    "image_url": IMAGE_URL,
    "caption": CAPTION,
    "access_token": ACCESS_TOKEN,
}

media_res = requests.post(media_url, data=media_payload)
print("MEDIA RESPONSE:", media_res.text)

try:
    media_json = media_res.json()
except Exception:
    print("Nao foi possivel ler resposta de criacao de midia.")
    raise SystemExit(1)

creation_id = media_json.get("id")
if not creation_id:
    print("ERRO ao criar midia, parando aqui.")
    raise SystemExit(1)

print(f"Objeto de midia criado: {creation_id}")
print("Aguardando processamento da midia...")
time.sleep(10)

# 2. Consultar status ate ficar pronto
status_url = f"https://graph.facebook.com/v18.0/{creation_id}"
status_params = {
    "fields": "status_code",
    "access_token": ACCESS_TOKEN,
}

status_code = None
for tentativa in range(10):
    status_res = requests.get(status_url, params=status_params)
    print("STATUS RESPONSE:", status_res.text)
    try:
        status_json = status_res.json()
    except Exception:
        print("Nao foi possivel ler o status da midia.")
        raise SystemExit(1)

    status_code = status_json.get("status_code")
    print(f"Tentativa {tentativa + 1}/10 - status: {status_code}")
    if status_code == "FINISHED":
        print("Midia pronta para publicar.")
        break

    time.sleep(3)

if status_code != "FINISHED":
    print("A midia nao ficou pronta a tempo. Tente novamente.")
    raise SystemExit(1)

# 3. Publicar midia
publish_url = f"https://graph.facebook.com/v18.0/{IG_ID}/media_publish"
publish_payload = {
    "creation_id": creation_id,
    "access_token": ACCESS_TOKEN,
}

publish_res = requests.post(publish_url, data=publish_payload)
print("PUBLISH RESPONSE:", publish_res.text)

try:
    publish_json = publish_res.json()
except Exception:
    print("Nao foi possivel ler a resposta de publicacao.")
    raise SystemExit(1)

if publish_json.get("id"):
    print("Post publicado com sucesso!")
else:
    print("Erro ao publicar.")
